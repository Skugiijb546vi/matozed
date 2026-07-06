import sys
import os
import subprocess
import urllib.request
import tarfile
import json
from huggingface_hub import HfApi

def install_nm3u8dl():
    print("Fetching latest N_m3u8DL-RE release...")
    req = urllib.request.Request("https://api.github.com/repos/nilaoda/N_m3u8DL-RE/releases/latest")
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    
    asset_url = None
    for asset in data["assets"]:
        if "linux-x64" in asset["name"] and asset["name"].endswith(".tar.gz"):
            asset_url = asset["browser_download_url"]
            break
            
    if not asset_url:
        print("Could not find linux-x64 asset!")
        sys.exit(1)
        
    print(f"Downloading {asset_url}...")
    urllib.request.urlretrieve(asset_url, "nm3u8dl.tar.gz")
    
    print("Extracting...")
    with tarfile.open("nm3u8dl.tar.gz", "r:gz") as tar:
        tar.extractall()
        for member in tar.getmembers():
            if member.name.endswith("N_m3u8DL-RE"):
                os.rename(member.name, "./N_m3u8DL-RE")
                os.chmod("./N_m3u8DL-RE", 0o755)
                break
    print("Installed N_m3u8DL-RE")

def main():
    if len(sys.argv) < 3:
        print("Usage: python download_upload.py <m3u8_url> <filename>")
        sys.exit(1)

    url = sys.argv[1]
    filename = sys.argv[2]
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("HF_TOKEN environment variable is not set!")
        sys.exit(1)

    install_nm3u8dl()

    save_name = filename.rsplit('.', 1)[0]
    
    print(f"Downloading {url} to {filename} with N_m3u8DL-RE...")
    subprocess.run([
        "./N_m3u8DL-RE", 
        url, 
        "--save-name", save_name,
        "--thread-count", "32",
        "-H", "Referer: https://iframe.mediadelivery.net/",
        "--auto-select"
    ], check=True)
    
    created_file = None
    for f in os.listdir("."):
        if f.startswith(save_name) and f.endswith((".mp4", ".mkv", ".ts", ".m4a")):
            if f != filename and f != save_name:
                created_file = f
                break
                
    if created_file:
        os.rename(created_file, filename)
    elif os.path.exists(save_name):
        os.rename(save_name, filename)

    print(f"Uploading {filename} to Hugging Face dataset Sarkoakram/matozed...")
    api = HfApi()
    api.upload_file(
        path_or_fileobj=filename,
        path_in_repo=filename,
        repo_id="Sarkoakram/matozed",
        repo_type="dataset",
        token=hf_token
    )
    print("Upload complete!")

if __name__ == '__main__':
    main()
