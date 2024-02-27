import requests
import re
import os
import shutil
import tarfile

repo_owner = 'AsamK'
repo_name = 'signal-cli'
download_dir = './'
archive_dir = "./"
regex_pattern = r'signal-cli-\d+\.\d+\.\d+\.tar\.gz'
target_dir = "./"


def get_latest_release_version(repo_owner, repo_name, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        release_info = response.json()
        return release_info.get('tag_name', '')
    else:
        print(f"Failed to fetch latest release version. Status code: {response.status_code}")
        return None


def download_release(repo_owner, repo_name, version, download_dir, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{version}"
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        release_info = response.json()
        assets = release_info.get('assets', [])

        if assets:

            desired_asset_pattern = re.compile(r'signal-cli-\d+\.\d+\.\d+\.tar\.gz')
            desired_asset_url = None
            for asset in assets:
                asset_name = asset.get('name')
                if desired_asset_pattern.match(asset_name):
                    desired_asset_url = asset.get('browser_download_url')
                    break

            if desired_asset_url:

                download_path = os.path.join(download_dir, asset_name)
                with open(download_path, 'wb') as f:
                    asset_response = requests.get(desired_asset_url, headers=headers)
                    f.write(asset_response.content)

                print(f"Downloaded: {asset_name}")
            else:
                print("Desired asset not found in the latest release.")
        else:
            print("No assets found in the latest release.")
    else:
        print(f"Failed to fetch release information. Status code: {response.status_code}")


def check_and_download_latest_release(repo_owner, repo_name, download_dir, token=None):
    latest_version = get_latest_release_version(repo_owner, repo_name, token)
    if not latest_version:
        print("Failed to fetch the latest release version.")
        return

    stored_version_path = os.path.join(download_dir, 'stored_version.txt')
    stored_version = None
    if os.path.exists(stored_version_path):
        with open(stored_version_path, 'r') as f:
            stored_version = f.read().strip()

    if latest_version != stored_version:

        download_release(repo_owner, repo_name, latest_version, download_dir, token)

        with open(stored_version_path, 'w') as f:
            f.write(latest_version)
    else:
        print("No new release available.")


def extract_signal_cli(archive_dir, regex_pattern, target_dir):
    # Find the archive matching the pattern
    archive_path = None
    for filename in os.listdir(archive_dir):
        if re.match(regex_pattern, filename):
            archive_path = os.path.join(archive_dir, filename)
            break

    if archive_path:
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                # Extract the archive to a temporary directory
                temp_dir = os.path.join(target_dir, "temp_extracted")
                tar.extractall(path=temp_dir)

                # Find the signal-cli executable
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file == "signal-cli":
                            # Move the executable to the target directory
                            shutil.move(os.path.join(root, file), os.path.join(target_dir, file))
                            print("Signal-cli executable extracted.")
                            return
                print("Signal-cli executable not found in the archive.")
        except tarfile.TarError as e:
            print(f"Error extracting archive: {e}")
    else:
        print("Archive matching the pattern not found.")


check_and_download_latest_release(repo_owner, repo_name, download_dir)
extract_signal_cli(archive_dir, download_dir, regex_pattern)
