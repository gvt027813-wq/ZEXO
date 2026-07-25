"""
Configuration file for Automated News Website
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (Use GitHub Secrets in production)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Repository Configuration
GITHUB_REPO = "gvt027813-wq/ZEXO"
BRANCH_NAME = "automated-news"

# News Categories
NEWS_CATEGORIES = [
    "general",
    "technology",
    "business",
    "entertainment",
    "sports",
    "health"
]

# Country for news (ISO 3166-1 alpha-2 code)
NEWS_COUNTRY = "in"  # India

# Article generation settings
ARTICLE_MIN_LENGTH = 600
ARTICLE_MAX_LENGTH = 800
ARTICLE_TEMPERATURE = 0.7

# Publishing settings
ARTICLES_PER_CATEGORY = 1
AUTOMATION_INTERVAL_HOURS = 6

# Site settings
SITE_TITLE = "ZEXO NEWS"
SITE_DESCRIPTION = "Auto-Generated Quality News Updates 24/7"
ADSENSE_ID = "ca-pub-YOUR_ADSENSE_ID"  # Replace with your AdSense ID

# Social media settings
TWITTER_HANDLE = "@ZEXO_News"
FACEBOOK_PAGE = "https://facebook.com/ZEXO-News"

print("✅ Configuration loaded successfully!")
