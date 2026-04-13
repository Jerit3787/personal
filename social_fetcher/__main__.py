#!/usr/bin/env python
"""Entry point for the social media data fetcher.

Usage: python -m social_fetcher
"""

from . import instagram
from .utils import load_existing_data, save_data, is_remote_image_accessible


def main():
    """Fetch and save social media data."""
    # Refresh Instagram token before fetching data
    instagram.refresh_token()

    # Twitter API: Skipped — free tier no longer supports reading user data.
    # Existing Twitter data in social_data.json will be preserved as-is.
    print("Skipping Twitter API (free tier does not support read access)")
    twitter_profile_new = None

    instagram_profile_new = instagram.get_profile()

    # Load existing data for fallback and image link comparison
    existing_data = load_existing_data()
    twitter_existing = existing_data.get("twitter", {})
    instagram_existing = existing_data.get("instagram", {})

    # Fallback image URLs
    twitter_fallback_img = "img/twitter.png"
    instagram_fallback_img = "img/instagram.png"

    # --- Twitter (preserve existing data) ---
    twitter_profile = twitter_profile_new.copy() if twitter_profile_new else twitter_existing.copy()
    old_twitter_img = twitter_existing.get("profile_image_url")
    new_twitter_img = twitter_profile_new.get("profile_image_url") if twitter_profile_new else None
    if old_twitter_img and is_remote_image_accessible(old_twitter_img):
        twitter_profile["profile_image_url"] = old_twitter_img
    elif new_twitter_img:
        twitter_profile["profile_image_url"] = new_twitter_img
    else:
        twitter_profile["profile_image_url"] = twitter_fallback_img

    # --- Instagram ---
    instagram_profile = instagram_profile_new.copy() if instagram_profile_new else instagram_existing.copy()
    old_insta_img = instagram_existing.get("profile_image_url")
    new_insta_img = instagram_profile_new.get("profile_image_url") if instagram_profile_new else None
    if old_insta_img and is_remote_image_accessible(old_insta_img):
        instagram_profile["profile_image_url"] = old_insta_img
    elif new_insta_img:
        instagram_profile["profile_image_url"] = new_insta_img
    else:
        instagram_profile["profile_image_url"] = instagram_fallback_img

    # Save
    data = {
        "twitter": twitter_profile,
        "instagram": instagram_profile
    }
    save_data(data)
    print("Social media data update complete!")


if __name__ == "__main__":
    main()
