#!/usr/bin/env python3
"""
Automated News Website Generator
Generates news articles automatically using AI
"""

import requests
import json
import os
from datetime import datetime
import time
import openai
from github import Github
import re

# ===== CONFIGURATION =====
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_REPO = "gvt027813-wq/ZEXO"
BRANCH_NAME = "automated-news"

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# ===== NEWS CATEGORIES =====
CATEGORIES = [
    "general",
    "technology",
    "business",
    "entertainment",
    "sports",
    "health"
]

def fetch_latest_news(category, country="in"):
    """NewsAPI से latest news fetch करो"""
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": category,
            "country": country,
            "apiKey": NEWSAPI_KEY,
            "sortBy": "publishedAt",
            "pageSize": 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            print(f"  ❌ NewsAPI Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ Error fetching news: {e}")
        return []

def generate_article_with_ai(headline, description, category):
    """ChatGPT से full article generate करो"""
    try:
        prompt = f"""Write a comprehensive news article based on:
Headline: {headline}
Description: {description}
Category: {category}

Requirements:
- 600-800 words
- Professional tone
- Include: Background, Impact, Analysis, Future implications
- SEO optimized with keywords
- Use clear formatting with paragraphs

Write the article now:"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"  ❌ Error generating article: {e}")
        # Fallback: use description as article
        return f"<p>{description}</p><p>This article is auto-generated from latest news.</p>"

def get_image_url_from_news(news_item):
    """News item से image URL निकालो"""
    try:
        img_url = news_item.get("urlToImage")
        if img_url and (img_url.startswith("http://") or img_url.startswith("https://")):
            return img_url
    except:
        pass
    
    # Default image
    return "https://via.placeholder.com/1200x630?text=AI+News"

def create_html_article(headline, article_content, image_url, category, source="AI News", original_url=""):
    """Full HTML article बनाओ"""
    try:
        # Create slug
        slug = re.sub(r'[^a-z0-9]+', '-', headline.lower().strip())[:50]
        slug = slug.strip('-')
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Clean article content
        article_content = article_content.replace('\n', '</p><p>').replace('<p></p>', '')
        if not article_content.startswith('<p>'):
            article_content = f'<p>{article_content}</p>'
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{headline[:160]}">
    <meta property="og:title" content="{headline}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:type" content="article">
    <meta name="author" content="{source}">
    <title>{headline} - ZEXO News</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        header {{
            background: #1a1a1a;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .nav {{
            background: #333;
            padding: 10px;
            text-align: center;
        }}
        .nav a {{
            color: white;
            text-decoration: none;
            margin: 0 15px;
            font-size: 14px;
        }}
        .nav a:hover {{
            color: #4CAF50;
        }}
        .article {{
            max-width: 800px;
            margin: 40px auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
            color: #666;
        }}
        .category {{
            background: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        h1 {{
            font-size: 32px;
            line-height: 1.3;
            margin: 20px 0;
            color: #1a1a1a;
        }}
        .featured-image {{
            width: 100%;
            height: auto;
            margin: 30px 0;
            border-radius: 8px;
            object-fit: cover;
        }}
        .content {{
            font-size: 16px;
            line-height: 1.8;
        }}
        .content p {{
            margin-bottom: 15px;
        }}
        .share-buttons {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }}
        .share-buttons a {{
            display: inline-block;
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
        }}
        .share-buttons a:hover {{
            background: #45a049;
        }}
        footer {{
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 50px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>📰 ZEXO NEWS</h1>
        <p>Auto-Generated Quality News</p>
    </header>
    
    <nav class="nav">
        <a href="../index.html">Home</a>
        <a href="../index.html#technology">Technology</a>
        <a href="../index.html#business">Business</a>
        <a href="../index.html#general">General</a>
    </nav>
    
    <article class="article">
        <div class="meta">
            <span class="category">{category.upper()}</span>
            <div>
                <span>{date}</span> | <span>By {source}</span>
            </div>
        </div>
        
        <h1>{headline}</h1>
        
        <img src="{image_url}" alt="{headline}" class="featured-image">
        
        <div class="content">
            {article_content}
        </div>
        
        <div class="share-buttons">
            <a href="https://twitter.com/intent/tweet?text={headline[:100]}...&url=YOUR_SITE" target="_blank">📱 Share on Twitter</a>
            <a href="https://www.facebook.com/sharer/sharer.php?u=YOUR_SITE" target="_blank">📚 Share on Facebook</a>
        </div>
    </article>
    
    <footer>
        <p>&copy; 2026 ZEXO News. Auto-generated with AI. All rights reserved.</p>
        <p><a href="../index.html" style="color: #4CAF50; text-decoration: none;">← Back to Home</a></p>
    </footer>
    
    <!-- AdSense Code -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?ca-pub-YOUR_ADSENSE_ID"></script>
    <script>
        (adsbygoogle = window.adsbygoogle || []).push({{
            google_ad_client: "ca-pub-YOUR_ADSENSE_ID",
            enable_page_level_ads: true
        }});
    </script>
</body>
</html>"""
        
        return html, slug
    except Exception as e:
        print(f"  ❌ Error creating HTML: {e}")
        return "", ""

def publish_to_github(filename, content, message):
    """GitHub पर publish करो"""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_user().get_repo(GITHUB_REPO)
        
        try:
            repo.create_file(f"articles/{filename}", message, content, branch=BRANCH_NAME)
            print(f"  ✅ Published: {filename}")
            return True
        except Exception as e:
            # File might already exist, try to update
            try:
                contents = repo.get_contents(f"articles/{filename}", ref=BRANCH_NAME)
                repo.update_file(
                    f"articles/{filename}",
                    message,
                    content,
                    contents.sha,
                    branch=BRANCH_NAME
                )
                print(f"  ✅ Updated: {filename}")
                return True
            except:
                print(f"  ⚠️  Could not publish: {filename}")
                return False
    except Exception as e:
        print(f"  ❌ GitHub Error: {e}")
        return False

def update_index_page(articles_list):
    """Homepage update करो"""
    try:
        articles_html = ""
        for article in articles_list:
            articles_html += f"""        <div class="article-card">
            <img src="{article['image']}" alt="{article['title']}" onerror="this.src='https://via.placeholder.com/400x250?text=News'">
            <div class="card-content">
                <span class="category">{article['category'].upper()}</span>
                <h3><a href="articles/{article['slug']}.html">{article['title']}</a></h3>
                <p>{article['description'][:150]}...</p>
                <a href="articles/{article['slug']}.html" class="read-more">Read More →</a>
            </div>
        </div>
"""
        
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="ZEXO News - Auto-generated quality news updates 24/7 using AI">
    <meta property="og:title" content="ZEXO News - Latest News & Updates">
    <meta property="og:description" content="Get the latest news automatically generated by AI">
    <title>ZEXO News - Latest News & Updates</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header h1 {{
            font-size: 48px;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        header p {{
            font-size: 18px;
            opacity: 0.9;
        }}
        nav {{
            background: #333;
            padding: 15px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        nav a {{
            color: white;
            text-decoration: none;
            margin: 0 20px;
            font-size: 16px;
            font-weight: 500;
            transition: color 0.3s;
        }}
        nav a:hover {{
            color: #667eea;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }}
        .article-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }}
        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        }}
        .article-card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .card-content {{
            padding: 20px;
        }}
        .category {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .article-card h3 {{
            font-size: 20px;
            margin: 10px 0;
            line-height: 1.4;
        }}
        .article-card h3 a {{
            color: #1a1a1a;
            text-decoration: none;
        }}
        .article-card h3 a:hover {{
            color: #667eea;
        }}
        .article-card p {{
            color: #666;
            font-size: 14px;
            margin: 10px 0;
            height: 42px;
            overflow: hidden;
        }}
        .read-more {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
            margin-top: 10px;
            transition: color 0.3s;
        }}
        .read-more:hover {{
            color: #764ba2;
        }}
        .no-articles {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}
        footer {{
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 30px 20px;
            margin-top: 60px;
        }}
        footer p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        .updated {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <header>
        <h1>🔔 ZEXO NEWS</h1>
        <p>Auto-Generated Quality News Updates 24/7</p>
    </header>
    
    <nav>
        <a href="#">Home</a>
        <a href="#technology">Technology</a>
        <a href="#business">Business</a>
        <a href="#general">General</a>
        <a href="#entertainment">Entertainment</a>
        <a href="#sports">Sports</a>
        <a href="#health">Health</a>
    </nav>
    
    <div class="container">
        <div class="updated">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        {articles_html if articles_html else '<div class="no-articles"><h2>No articles yet. Check back soon!</h2></div>'}
    </div>
    
    <footer>
        <p>&copy; 2026 ZEXO News. All rights reserved.</p>
        <p>Powered by AI | Auto-generated News Platform</p>
        <p><a href="https://github.com/gvt027813-wq/ZEXO" style="color: #667eea;" target="_blank">View on GitHub</a></p>
    </footer>
    
    <!-- AdSense Code -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?ca-pub-YOUR_ADSENSE_ID"></script>
    <script>
        (adsbygoogle = window.adsbygoogle || []).push({{
            google_ad_client: "ca-pub-YOUR_ADSENSE_ID",
            enable_page_level_ads: true
        }});
    </script>
</body>
</html>"""
        
        publish_to_github("index.html", index_html, "Update homepage with latest articles")
    except Exception as e:
        print(f"❌ Error updating index: {e}")

def main():
    """Main automation function - हर 6 hours चलेगा"""
    
    print(f"\n🚀 Starting automation at {datetime.now()}")
    print(f"Repository: {GITHUB_REPO}")
    print(f"Branch: {BRANCH_NAME}")
    
    all_articles = []
    
    for category in CATEGORIES:
        print(f"\n📰 Processing: {category.upper()}")
        
        try:
            # Step 1: News fetch करो
            news_items = fetch_latest_news(category)
            
            if not news_items:
                print(f"  ⚠️  No news found for {category}")
                continue
            
            for idx, news in enumerate(news_items[:1]):  # एक ही article per category
                headline = news.get('title', 'Untitled')
                description = news.get('description', '')
                
                print(f"  ✓ Fetched: {headline[:60]}...")
                
                # Step 2: Article generate करो
                print(f"  ⏳ Generating article with AI...")
                article_content = generate_article_with_ai(headline, description, category)
                print(f"  ✓ Generated article")
                
                # Step 3: Image get करो
                image_url = get_image_url_from_news(news)
                print(f"  ✓ Got image")
                
                # Step 4: HTML create करो
                html_content, slug = create_html_article(
                    headline,
                    article_content,
                    image_url,
                    category
                )
                
                if not slug:
                    continue
                
                # Step 5: GitHub पर publish करो
                filename = f"{slug}.html"
                publish_to_github(filename, html_content, f"Add article: {headline}")
                
                all_articles.append({
                    "title": headline,
                    "slug": slug,
                    "category": category,
                    "description": description[:150],
                    "image": image_url
                })
                
                time.sleep(1)  # Rate limiting
        
        except Exception as e:
            print(f"  ❌ Error in {category}: {e}")
            continue
    
    # Step 6: Homepage update करो
    if all_articles:
        print(f"\n📄 Updating homepage with {len(all_articles)} articles...")
        update_index_page(all_articles)
    
    print(f"\n✅ Automation complete! Published {len(all_articles)} articles")
    print(f"Finished at {datetime.now()}")

if __name__ == "__main__":
    main()
