"""Configuration constants loaded from environment variables."""

import os

OUTPUT_PATH = "src/social_data.json"
TWITTER_USER_ID = os.environ.get("TWITTER_USER_ID", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME", "")
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "")
SAVE_PROFILE_IMAGES = True
