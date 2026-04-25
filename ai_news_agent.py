import os
import requests
import google.generativeai as genai
from datetime import datetime

# 1. Configuration - Fetches from GitHub Secrets
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

def get_basket_news():
    # Focused but broad enough to find 10+ stories
    query = "(Singapore business) OR (SGX REIT) OR (tennis ATP news) OR (Japan Korea travel) OR (AI automation enterprise)"
    # Increased pageSize to 50
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=50&apiKey={NEWS_API_KEY}"
    # ... (rest of your fetching logic)

def generate_ai_summary(raw_data):
    prompt = f"""
    You are a Chief of Staff for a Singaporean Tech Lead. 
    Create a detailed intelligence brief with 5-10 stories total across these FIVE distinct categories:
    
    1. 🇸🇬 Singapore & Local Business: Focus on infrastructure and SME policy.
    2. 💰 Finance & SGX: Prioritize REIT dividends and blue-chip performance.
    3. 🎾 Tennis: General ATP/WTA news, tournament updates (Madrid/Rome), and equipment.
    4. ✈️ Japan & Korea Travel: Logistics, rail updates, and travel trends for these specific regions.
    5. 🤖 AI & Technology: Enterprise automation, architecture, and developer tools.
    
    REQUIREMENTS:
    - Total stories: Aim for at least 7-10 high-quality items.
    - Format: Use the professional card style. 
    - Links: Use <a href='URL' target='_blank'>Read Original Article →</a>.
    - Content: If no specific news is found for a category, omit the header rather than saying "none."
    
    Data:
    {{raw_data}}
    """
    response = model.generate_content(prompt)
    return response.text

# Main Execution
news_context = get_basket_news()
ai_html_body = generate_ai_summary(news_context)

# Final HTML Wrapper with basic styling
# Replace the 'final_html' variable in your script with this:

final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Intelligence Hub</title>
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
            margin: 0;
            padding: 0;
        }}
        header {{
            background: var(--primary);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .container {{
            max-width: 1000px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        .timestamp {{
            font-size: 0.9rem;
            opacity: 0.8;
            margin-top: 0.5rem;
        }}
        /* Card Styling */
        h2 {{ 
            color: var(--primary);
            border-left: 5px solid var(--accent);
            padding-left: 15px;
            margin-top: 2rem;
            font-size: 1.5rem;
        }}
        ul {{ list-style: none; padding: 0; }}
        li {{ 
            background: var(--card-bg);
            margin-bottom: 1rem;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }}
        li:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        /* Link Styling */
        a {{ 
            display: inline-block;
            margin-top: 10px;
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        a:hover {{ text-decoration: underline; }}
        
        /* Mobile Optimization */
        @media (max-width: 600px) {{
            header {{ padding: 1.5rem 1rem; }}
            h1 {{ font-size: 1.4rem; }}
            li {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Daily Intelligence Hub</h1>
        <div class="timestamp">Updated: {datetime.now().strftime('%d %b %Y | %I:%M %p')} SGT</div>
    </header>
    <div class="container">
        {ai_html_body}
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)
