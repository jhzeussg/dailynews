import os
import requests
import google.generativeai as genai
from datetime import datetime

# 1. SETUP: Access Secrets from GitHub Actions
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Configure Gemini (Using the 2026 standard model)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

def get_basket_news():
    """Scrapes raw data from the 'Basket' of news topics."""
    # Architecting the query for high-signal retrieval
    query = "(Singapore business) OR (SGX REIT dividend) OR (ATP tennis) OR (Japan Korea travel logistics) OR (AI automation enterprise)"
    
    # We pull 50 articles to ensure we have enough for 10 high-quality summaries
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=50&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        
        if not articles:
            return "No recent news found for these categories today."
            
        context = ""
        for a in articles:
            if a.get('description') and a.get('title'):
                context += f"Source: {a['source']['name']}\nTitle: {a['title']}\nSnippet: {a['description']}\nLink: {a['url']}\n\n"
        return context
    except Exception as e:
        return f"Error fetching news: {e}"

def generate_ai_summary(raw_data):
    """Uses Gemini to curate and format the news into professional cards."""
    prompt = f"""
    You are a Chief of Staff for a Singapore-based Technical Lead. 
    Review the provided news data and create a detailed intelligence brief with 7-10 stories total across these FIVE categories:

    1. 🇸🇬 Singapore & Local Business: Focus on infrastructure and local policy.
    2. 💰 Finance & SGX: Prioritize REIT dividends and blue-chip performance.
    3. 🎾 Tennis: Focus on ATP updates, tournament results (Madrid/Rome), and performance equipment.
    4. ✈️ Japan & Korea Travel: Logistics, high-speed rail updates, and travel efficiency trends.
    5. 🤖 AI & Technology: Enterprise automation, software architecture, and developer tools.

    REQUIREMENTS:
    - Target 7-10 total high-quality items.
    - Format each story as a list item in this style: 
      "<li><strong>Headline</strong>: Brief summary insight. <a href='URL' target='_blank'>Read Original Article →</a></li>"
    - Wrap each category in a <h2>Category Name</h2> and a <ul>.
    - If a category has no relevant data, skip it.

    Raw Data:
    {raw_data}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"<p>Error generating summary: {e}</p>"

# --- MAIN EXECUTION FLOW ---

# 1. Get the raw news
news_context = get_basket_news()

# 2. Let the AI build the body content
ai_html_body = generate_ai_summary(news_context)

# 3. Assemble the final mobile-responsive Dashboard
final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligence Hub</title>
    <style>
        :root {{
            --primary: #1a365d;
            --secondary: #2d3748;
            --accent: #3182ce;
            --bg: #f7fafc;
            --card-bg: #ffffff;
        }}
        body {{ 
            font-family: 'Inter', -apple-system, sans-serif; 
            line-height: 1.6; 
            background-color: var(--bg); 
            color: var(--secondary);
            margin: 0; padding: 0;
        }}
        header {{
            background: var(--primary);
            color: white;
            padding: 2.5rem 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .container {{
            max-width: 900px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}
        .timestamp {{
            font-size: 0.95rem;
            opacity: 0.9;
            margin-top: 0.8rem;
            font-weight: 300;
        }}
        h2 {{ 
            color: var(--primary);
            border-left: 6px solid var(--accent);
            padding-left: 15px;
            margin: 3rem 0 1.5rem 0;
            font-size: 1.6rem;
            letter-spacing: -0.5px;
        }}
        ul {{ list-style: none; padding: 0; }}
        li {{ 
            background: var(--card-bg);
            margin-bottom: 1.2rem;
            padding: 1.8rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02), 0 1px 3px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }}
        li:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        }}
        a {{ 
            display: inline-block;
            margin-top: 12px;
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85rem;
            border: 1px solid #e2e8f0;
            padding: 4px 12px;
            border-radius: 6px;
        }}
        a:hover {{ background: #ebf8ff; }}
        
        @media (max-width: 600px) {{
            header {{ padding: 2rem 1rem; }}
            h1 {{ font-size: 1.5rem; }}
            li {{ padding: 1.2rem; }}
            h2 {{ font-size: 1.3rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Intelligence Hub</h1>
        <div class="timestamp">Updated: {datetime.now().strftime('%d %b %Y | %I:%M %p')} SGT</div>
    </header>
    <div class="container">
        {ai_html_body}
    </div>
</body>
</html>
"""

# 4. Save to file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Success: Intelligence Hub generated!")
