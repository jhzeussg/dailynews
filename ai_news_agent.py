import os
import requests
import google.generativeai as genai
from datetime import datetime

# 1. SETUP
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

def get_basket_news():
    """Performs 5 distinct searches to ensure high story density."""
    categories = {
        "Singapore Business": "Singapore economy OR SME news Singapore",
        "Finance & SGX": "SGX REIT dividends OR Singapore blue chip stocks",
        "Tennis": "ATP tennis news OR Madrid Open results OR Sinner Alcaraz",
        "Japan & Korea Travel": "Japan travel logistics OR Korea Shinkansen KTX",
        "AI & Tech": "enterprise AI automation OR software architecture trends"
    }
    
    combined_context = ""
    for name, query in categories.items():
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=20&apiKey={NEWS_API_KEY}"
        try:
            response = requests.get(url).json()
            articles = response.get('articles', [])
            combined_context += f"--- CATEGORY: {name} ---\n"
            for a in articles[:12]:
                if a.get('description'):
                    combined_context += f"Title: {a['title']}\nSnippet: {a['description']}\nLink: {a['url']}\n\n"
        except: continue
    return combined_context

def generate_ai_summary(raw_data):
    prompt = f"""
    You are a Chief of Staff. Create an expansive Intelligence Brief.
    VOLUME: Target 5-8 high-quality stories PER CATEGORY. 

    CATEGORIES:
    1. 🇸🇬 Singapore & Local Business
    2. 💰 Finance & SGX
    3. 🎾 Tennis
    4. ✈️ Japan & Korea Travel
    5. 🤖 AI & Technology

    FORMATTING:
    - Wrap each category in <h2>Category Name</h2> and a <ul>.
    - Each story MUST be an <li> with a bold headline and a 1-sentence insight.
    - Links: <a href='URL' target='_blank' class='source-link'>Read Original Article →</a>
    
    Data:
    {raw_data}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"<p>Error: {e}</p>"

# --- EXECUTION ---
news_context = get_basket_news()
ai_html_body = generate_ai_summary(news_context)

final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligence Hub 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0f172a; --accent: #3b82f6; --bg: #f8fafc; --glass: rgba(255, 255, 255, 0.9);
        }}
        body {{ 
            font-family: 'Inter', sans-serif; background-color: var(--bg); color: #1e293b; margin: 0; 
        }}
        header {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white; padding: 4rem 1rem; text-align: center;
        }}
        .container {{ max-width: 1000px; margin: -3rem auto 4rem; padding: 0 1.5rem; }}
        .timestamp {{ font-size: 0.9rem; opacity: 0.7; margin-top: 10px; text-transform: uppercase; letter-spacing: 1px; }}
        
        h2 {{ 
            font-size: 1.25rem; color: var(--primary); text-transform: uppercase; 
            letter-spacing: 1px; margin: 3rem 0 1rem; display: flex; align-items: center;
        }}
        h2::after {{ content: ""; flex: 1; height: 1px; background: #e2e8f0; margin-left: 15px; }}

        ul {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; padding: 0; }}
        li {{ 
            background: var(--glass); backdrop-filter: blur(10px);
            padding: 2rem; border-radius: 20px; border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column;
        }}
        li:hover {{ border-color: var(--accent); transform: translateY(-2px); transition: 0.3s; }}
        
        .source-link {{
            margin-top: auto; padding-top: 15px; color: var(--accent); text-decoration: none;
            font-weight: 600; font-size: 0.8rem;
        }}

        @media (max-width: 600px) {{
            ul {{ grid-template-columns: 1fr; }}
            header {{ padding: 3rem 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Intelligence Hub</h1>
        <div class="timestamp">Market Brief • {datetime.now().strftime('%d %b %Y')}</div>
    </header>
    <div class="container">{ai_html_body}</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)
