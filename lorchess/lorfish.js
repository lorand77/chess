"use strict";

// ====================================================================
// LorFish engine — port of lorfish.py
// ====================================================================
const LorFish = {
  // Same piece values and PSTs as the Python (sunfish-derived).
  pieceValues: { p: 100, n: 280, b: 320, r: 479, q: 929, k: 0 },
  pst: {
    p: [
        0,   0,   0,   0,   0,   0,   0,   0,
      -31,   8,  -7, -37, -36, -14,   3, -31,
      -22,   9,   5, -11, -10,  -2,   3, -19,
      -26,   3,  10,   9,   6,   1,   0, -23,
      -17,  16,  -2,  15,  14,   0,  15, -13,
        7,  29,  21,  44,  40,  31,  44,   7,
       78,  83,  86,  73, 102,  82,  85,  90,
        0,   0,   0,   0,   0,   0,   0,   0
    ],
    n: [
      -74, -23, -26, -24, -19, -35, -22, -69,
      -23, -15,   2,   0,   2,   0, -23, -20,
      -18,  10,  13,  22,  18,  15,  11, -14,
       -1,   5,  31,  21,  22,  35,   2,   0,
       24,  24,  45,  37,  33,  41,  25,  17,
       10,  67,   1,  74,  73,  27,  62,  -2,
       -3,  -6, 100, -36,   4,  62,  -4, -14,
      -66, -53, -75, -75, -10, -55, -58, -70
    ],
    b: [
       -7,   2, -15, -12, -14, -15, -10, -10,
       19,  20,  11,   6,   7,   6,  20,  16,
       14,  25,  24,  15,   8,  25,  20,  15,
       13,  10,  17,  23,  17,  16,   0,   7,
       25,  17,  20,  34,  26,  25,  15,  10,
       -9,  39, -32,  41,  52, -10,  28, -14,
      -11,  20,  35, -42, -39,  31,   2, -22,
      -59, -78, -82, -76, -23,-107, -37, -50
    ],
    r: [
      -30, -24, -18,   5,  -2, -18, -31, -32,
      -53, -38, -31, -26, -29, -43, -44, -53,
      -42, -28, -42, -25, -25, -35, -26, -46,
      -28, -35, -16, -21, -13, -29, -46, -30,
        0,   5,  16,  13,  18,  -4,  -9,  -6,
       19,  35,  28,  33,  45,  27,  25,  15,
       55,  29,  56,  67,  55,  62,  34,  60,
       35,  29,  33,   4,  37,  33,  56,  50
    ],
    q: [
      -39, -30, -31, -13, -31, -36, -34, -42,
      -36, -18,   0, -19, -15, -15, -21, -38,
      -30,  -6, -13, -11, -16, -11, -16, -27,
      -14, -15,  -2,  -5,  -1, -10, -20, -22,
        1, -16,  22,  17,  25,  20, -13,  -6,
       -2,  43,  32,  60,  72,  63,  43,   2,
       14,  32,  60, -10,  20,  76,  57,  24,
        6,   1,  -8,-104,  69,  24,  88,  26
    ],
    k: [
       17,  30,  -3, -14,   6,  -1,  40,  18,
       -4,   3, -14, -50, -57, -18,  13,   4,
      -47, -42, -43, -79, -64, -32, -29, -32,
      -55, -43, -52, -28, -51, -47,  -8, -50,
      -55,  50,  11,  -4, -19,  13,   0, -49,
      -62,  12, -57,  44, -67,  28,  37, -31,
      -32,  10,  55,  56,  56,  55,  10,   3,
        4,  54,  47, -99, -99,  60,  83, -62
    ],
  },

  orderMoves(chess, moves) {
    // MVV-LVA + promotion bonus. Skipping gives_check bonus for performance.
    const scored = new Array(moves.length);
    for (let i = 0; i < moves.length; i++) {
      const m = moves[i];
      let s = 0;
      const victim = m.enpassant ? { t: 'p' } : chess.squares[m.to];
      const attacker = chess.squares[m.from];
      if (victim && attacker) {
        s += (this.pieceValues[victim.t] || 0) * 10;
        s -= (this.pieceValues[attacker.t] || 0) / 100 | 0;
      }
      if (m.promo) s += 8000;
      scored[i] = { m, s };
    }
    scored.sort((a, b) => b.s - a.s);
    return scored.map(x => x.m);
  },

  evaluate(chess) {
    let score = 0;
    for (let sq = 0; sq < 64; sq++) {
      const p = chess.squares[sq];
      if (!p) continue;
      const idx = p.c === W ? sq : (sq ^ 56);
      const v = this.pieceValues[p.t] + this.pst[p.t][idx];
      score += p.c === W ? v : -v;
    }
    return chess.turn === W ? score : -score;
  },

  quiescence(chess, alpha, beta, qdepth) {
    this.nodes++;
    if (qdepth > this.maxQ) this.maxQ = qdepth;

    const moves = chess.legalMoves();
    if (moves.length === 0) return chess.inCheck() ? -99999 : 0;
    if (chess.isInsufficientMaterial()) return 0;

    const standPat = this.evaluate(chess);
    if (standPat >= beta) return beta;
    if (standPat > alpha) alpha = standPat;

    const captures = this.orderMoves(chess, moves.filter(m => m.capture || m.enpassant));
    for (const m of captures) {
      chess.makeMove(m);
      const score = -this.quiescence(chess, -beta, -alpha, qdepth + 1);
      chess.undoMove();
      if (score >= beta) return beta;
      if (score > alpha) alpha = score;
    }
    return alpha;
  },

  negamax(chess, depth, alpha, beta) {
    this.nodes++;
    const moves = chess.legalMoves();
    if (moves.length === 0) return chess.inCheck() ? (-99999 - depth) : 0;
    if (chess.isInsufficientMaterial()) return 0;
    if (depth === 0) return this.quiescence(chess, alpha, beta, 0);

    const ordered = this.orderMoves(chess, moves);
    let best = -Infinity;
    for (const m of ordered) {
      chess.makeMove(m);
      const v = -this.negamax(chess, depth - 1, -beta, -alpha);
      chess.undoMove();
      if (v > best) best = v;
      if (best > alpha) alpha = best;
      if (alpha >= beta) break;
    }
    return best;
  },

  getBestMove(chess, depth) {
    this.nodes = 0;
    this.maxQ = 0;
    const t0 = performance.now();
    let bestMove = null, bestVal = -Infinity;
    const moves = this.orderMoves(chess, chess.legalMoves());
    const evals = [];
    for (const m of moves) {
      // SAN must be built BEFORE makeMove (needs pre-move state).
      const san = chess.moveToSan(m);
      chess.makeMove(m);
      // Full window at root so logged evals are exact, not pruning bounds.
      const raw = -this.negamax(chess, depth - 1, -Infinity, Infinity);
      chess.undoMove();
      // Tiny tiebreaker noise so equal-ish moves vary game to game.
      const noise = Math.floor(Math.random() * 21) - 10; // -10..+10
      const v = raw + noise;
      if (v > bestVal) { bestVal = v; bestMove = m; }
      evals.push({ san, raw, v });
    }
    const dt = ((performance.now() - t0) / 1000).toFixed(3);
    evals.sort((a, b) => b.v - a.v);
    const side = chess.turn === W ? 'White' : 'Black';
    console.log(`LorFish evals (${side} to move, depth=${depth}):`);
    for (const e of evals) console.log(`  ${e.san.padEnd(8)} ${e.v}  [raw=${e.raw}]`);
    console.log(`nodes=${this.nodes} time=${dt}s maxQ=${this.maxQ}`);
    return bestMove;
  },
};
