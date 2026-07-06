import sys
import os
import subprocess
from huggingface_hub import HfApi

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

    print(f"Downloading {url} to {filename} with 20 concurrent connections...")
    subprocess.run(["yt-dlp", "-N", "20", "--socket-timeout", "10", "--abort-on-unavailable-fragment", "--fragment-retries", "3", "--retry-sleep", "fragment:2", "--referer", "https://iframe.mediadelivery.net/", url, "-o", filename], check=True)

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
