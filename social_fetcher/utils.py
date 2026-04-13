"""Utility functions for image handling and data persistence."""

import os
import json
import requests

from .config import OUTPUT_PATH


def download_image(image_url, filename):
    """Download an image from the given URL and save it to the src/img directory."""
    if not image_url:
        return None
    try:
        img_dir = os.path.join("src", "img")
        relative_img_dir = "img"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        image_path = os.path.join(img_dir, filename)
        relative_image_path = os.path.join(relative_img_dir, filename)

        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        with open(image_path, 'wb') as img_file:
            for chunk in response.iter_content(chunk_size=8192):
                img_file.write(chunk)
        print(f"Downloaded image: {image_path}")
        return relative_image_path
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return None


def load_existing_data():
    """Load existing data file if it exists."""
    try:
        if os.path.exists(OUTPUT_PATH):
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as file:
                return json.load(file)
    except Exception as e:
        print(f"Error loading existing data: {e}")

    return {
        "instagram": {"followers": 0},
        "twitter": {"followers": 0}
    }


def save_data(data):
    """Save data to JSON file."""
    try:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
        print(f"Data successfully saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error saving data: {e}")


def is_remote_image_accessible(url):
    """Check if a remote image URL is accessible (returns 200 and is an image)."""
    try:
        resp = requests.head(url, timeout=5, allow_redirects=True)
        if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', ''):
            return True
    except Exception:
        pass
    return False
