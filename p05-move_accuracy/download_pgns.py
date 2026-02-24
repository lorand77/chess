import requests
import os

PLAYER = "lorand111"

archives_url = "https://api.chess.com/pub/player/"+PLAYER+"/games/archives"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"
}

archives_response = requests.get(archives_url, headers=headers)
archives_response.raise_for_status()
urls = [url + "/pgn" for url in archives_response.json()["archives"]]
print(urls)

# Create directory if it doesn't exist
os.makedirs("pgn_files", exist_ok=True)

# Download the files
for i, url in enumerate(urls):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        filename = f"pgn_files/games_{i}.pgn"
        with open(filename, 'w') as f:
            f.write(response.text)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {url}")
        print(f"  Status code: {response.status_code}")
        print(f"  Response headers: {dict(response.headers)}")
        body_preview = response.text[:500] if response.text else "<empty>"
        print(f"  Response body (first 500 chars): {body_preview}")
