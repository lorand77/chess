"use strict";

const chess = new Chess();
let selected = null;
let legalFromSelected = [];
let lastMove = null;
let promotionPending = null;
let thinking = false;
let moveHistory = [];

const boardEl   = document.getElementById('board');
const turnEl    = document.getElementById('turn');
const statusEl  = document.getElementById('status');
const historyEl = document.getElementById('history');
const promoEl   = document.getElementById('promo');
const promoOpts = document.getElementById('promoOptions');

function pieceImgSrc(piece) {
  return `assets/${piece.c}_${PIECE_NAMES[piece.t]}_1x_ns.png`;
}

function logLegalMoves() {
  const moves = chess.legalMoves();
  const side = chess.turn === W ? 'White' : 'Black';
  const sans = moves.map(m => chess.moveToSan(m));
  console.log(`[${side} to move] ${moves.length} legal moves: ${sans.join(' ')}`);
}

function render() {
  boardEl.innerHTML = '';
  const inCheckNow = chess.inCheck();
  for (let r = 7; r >= 0; r--) {
    for (let f = 0; f < 8; f++) {
      const sq = sqIdx(f, r);
      const div = document.createElement('div');
      div.className = 'square ' + ((r + f) % 2 === 0 ? 'dark' : 'light');
      div.dataset.sq = sq;

      if (lastMove && (lastMove.from === sq || lastMove.to === sq)) div.classList.add('last-move');
      if (selected === sq) div.classList.add('selected');

      const piece = chess.squares[sq];
      if (inCheckNow && piece && piece.t === 'k' && piece.c === chess.turn) {
        div.classList.add('check');
      }

      // Coordinates: ranks on file a, files on rank 1
      if (f === 0) {
        const c = document.createElement('div');
        c.className = 'coord rank';
        c.textContent = r + 1;
        c.style.color = ((r + f) % 2 === 0) ? '#b58863' : '#f0d9b5';
        div.appendChild(c);
      }
      if (r === 0) {
        const c = document.createElement('div');
        c.className = 'coord file';
        c.textContent = String.fromCharCode(97 + f);
        c.style.color = ((r + f) % 2 === 0) ? '#b58863' : '#f0d9b5';
        div.appendChild(c);
      }

      if (piece) {
        const img = document.createElement('img');
        img.src = pieceImgSrc(piece);
        if (piece.t === 'p') img.classList.add('pawn');
        img.draggable = false;
        img.alt = piece.c + piece.t;
        div.appendChild(img);
      }

      if (selected !== null) {
        const m = legalFromSelected.find(x => x.to === sq);
        if (m) {
          const hint = document.createElement('div');
          hint.className = 'hint';
          if (chess.squares[sq] || m.enpassant) hint.classList.add('capture');
          div.appendChild(hint);
        }
      }

      div.addEventListener('click', () => onSquareClick(sq));
      boardEl.appendChild(div);
    }
  }

  // Info panel
  if (chess.isGameOver() && !thinking) {
    turnEl.textContent = '';
    turnEl.className = '';
  } else if (thinking) {
    turnEl.textContent = 'Engine thinking...';
    turnEl.className = 'thinking';
  } else {
    turnEl.textContent = 'Turn: ' + (chess.turn === W ? 'White' : 'Black');
    turnEl.className = '';
  }

  if (chess.isGameOver()) {
    let s = `Game Over: ${chess.result()}`;
    if (chess.isCheckmate()) {
      s += ` — ${chess.turn === W ? 'Black' : 'White'} wins!`;
    } else if (chess.isStalemate()) {
      s += ' — Stalemate';
    } else if (chess.isInsufficientMaterial()) {
      s += ' — Insufficient material';
    } else if (chess.isThreefoldRepetition()) {
      s += ' — Threefold repetition';
    } else if (chess.halfmove >= 100) {
      s += ' — 50-move rule';
    }
    statusEl.textContent = s;
    statusEl.className = 'game-over';
  } else if (inCheckNow) {
    statusEl.textContent = 'Check!';
    statusEl.className = 'check-text';
  } else {
    statusEl.textContent = '';
    statusEl.className = '';
  }

  historyEl.textContent = buildPgn();
  historyEl.scrollTop = historyEl.scrollHeight;
}

function buildPgn() {
  const d = new Date();
  const dateStr = d.getFullYear() + '.'
    + String(d.getMonth() + 1).padStart(2, '0') + '.'
    + String(d.getDate()).padStart(2, '0');
  const result = chess.isGameOver() ? chess.result() : '*';

  let pgn = '';
  pgn += '[Event "Human vs LorFish"]\n';
  pgn += `[Date "${dateStr}"]\n`;
  pgn += '[White "Human"]\n';
  pgn += '[Black "LorFish"]\n';
  pgn += `[Result "${result}"]\n`;
  pgn += '\n';

  let body = '';
  for (let i = 0; i < moveHistory.length; i++) {
    if (i % 2 === 0) body += (i / 2 + 1) + '. ';
    body += moveHistory[i] + ' ';
  }
  body += result;
  return pgn + body;
}

function onSquareClick(sq) {
  if (promotionPending || thinking || chess.isGameOver()) return;
  if (chess.turn !== W) return;

  if (selected === null) {
    const piece = chess.squares[sq];
    if (piece && piece.c === W) {
      selected = sq;
      legalFromSelected = chess.legalMoves().filter(m => m.from === sq);
      render();
    }
    return;
  }

  const candidate = legalFromSelected.find(m => m.to === sq);
  if (candidate) {
    const piece = chess.squares[selected];
    if (piece.t === 'p' && (rankOf(sq) === 0 || rankOf(sq) === 7)) {
      promotionPending = { from: selected, to: sq };
      showPromotionDialog();
      return;
    }
    doHumanMove(candidate);
    return;
  }

  // Reselect or deselect
  const piece = chess.squares[sq];
  if (piece && piece.c === W) {
    selected = sq;
    legalFromSelected = chess.legalMoves().filter(m => m.from === sq);
  } else {
    selected = null;
    legalFromSelected = [];
  }
  render();
}

function doHumanMove(move) {
  const san = chess.moveToSan(move);
  chess.makeMove(move);
  lastMove = move;
  moveHistory.push(san);
  selected = null;
  legalFromSelected = [];
  render();
  logLegalMoves();

  if (!chess.isGameOver()) {
    setTimeout(makeEngineMove, 50);
  }
}

function makeEngineMove() {
  if (chess.isGameOver() || chess.turn !== B) return;
  thinking = true;
  render();
  // Defer to next tick so the "thinking" UI paints before we block.
  setTimeout(() => {
    const depth = parseInt(document.getElementById('depth').value, 10);
    const move = LorFish.getBestMove(chess, depth);
    if (move) {
      const san = chess.moveToSan(move);
      chess.makeMove(move);
      lastMove = move;
      moveHistory.push(san);
    }
    thinking = false;
    render();
    logLegalMoves();
  }, 30);
}

function showPromotionDialog() {
  promoOpts.innerHTML = '';
  for (const t of ['q','r','b','n']) {
    const opt = document.createElement('div');
    opt.className = 'opt';
    const img = document.createElement('img');
    img.src = `assets/w_${PIECE_NAMES[t]}_1x_ns.png`;
    opt.appendChild(img);
    opt.addEventListener('click', () => {
      const move = legalFromSelected.find(m => m.to === promotionPending.to && m.promo === t);
      promoEl.classList.remove('show');
      promotionPending = null;
      if (move) doHumanMove(move);
    });
    promoOpts.appendChild(opt);
  }
  promoEl.classList.add('show');
}

function undo() {
  if (thinking) return;
  promotionPending = null;
  promoEl.classList.remove('show');

  // After a normal turn it's white to move; pop two plies (engine + human).
  if (chess.turn === W && chess.history.length >= 2) {
    chess.undoMove();
    chess.undoMove();
    moveHistory.splice(-2);
  } else if (chess.turn === B && chess.history.length >= 1) {
    chess.undoMove();
    moveHistory.splice(-1);
  }
  lastMove = chess.history.length > 0
    ? chess.history[chess.history.length - 1].move
    : null;
  selected = null;
  legalFromSelected = [];
  render();
  logLegalMoves();
}

document.addEventListener('keydown', e => {
  if (e.key === 'r' || e.key === 'R') undo();
});
document.getElementById('undoBtn').addEventListener('click', undo);
document.getElementById('resetBtn').addEventListener('click', () => {
  chess.reset();
  moveHistory = [];
  lastMove = null;
  selected = null;
  legalFromSelected = [];
  promotionPending = null;
  promoEl.classList.remove('show');
  thinking = false;
  render();
  logLegalMoves();
});

render();
logLegalMoves();
