import os
import requests
import json

TOKEN = "YOUR_GITHUB_TOKEN_HERE"
REPO = "U38572331/etf-dividend-analyzer"
TAG = "v2.1.0"
ASSET_PATH = r"dist\app.exe"
ASSET_NAME = "etf-dividend-analyzer.exe"

# Create a release
url = f"https://api.github.com/repos/{REPO}/releases"
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
data = {
    "tag_name": TAG,
    "name": "Release v2.1.0 (UI/UX Pro Max Redesign)",
    "body": "Complete UI overhaul using the UI UX Pro Max 'Fintech Analytics Dashboard' design system. Features new High-Contrast Accessible colors, modern Card-Based layouts, and styled Matplotlib charts.",
    "draft": False,
    "prerelease": False
}

print("Creating release...")
response = requests.post(url, headers=headers, json=data)

# Check if release already exists
if response.status_code == 422: # Validation failed (usually because tag already exists)
    print("Release might already exist. Trying to get release by tag...")
    get_url = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
    response = requests.get(get_url, headers=headers)
    release_id = response.json().get('id')
    upload_url = response.json().get('upload_url').split('{')[0]
elif response.status_code == 201:
    release_id = response.json().get('id')
    upload_url = response.json().get('upload_url').split('{')[0]
else:
    print(f"Error creating release: {response.text}")
    exit(1)

print(f"Release ID: {release_id}")
print(f"Upload URL: {upload_url}")

# Upload the asset
print("Uploading asset...")
with open(ASSET_PATH, 'rb') as f:
    asset_data = f.read()

upload_headers = {
    "Authorization": f"token {TOKEN}",
    "Content-Type": "application/octet-stream"
}

upload_response = requests.post(
    f"{upload_url}?name={ASSET_NAME}",
    headers=upload_headers,
    data=asset_data
)

if upload_response.status_code == 201:
    print("Asset uploaded successfully!")
else:
    print(f"Error uploading asset: {upload_response.text}")
    exit(1)
