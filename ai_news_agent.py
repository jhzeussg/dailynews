import os
import requests
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
# Ensure these are set in your GitHub Repository Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Categories tailored to your specific interests
CATEGORIES = {
    "Singapore Business & SGX": "Singapore finance stocks economy",
    "Tennis (Madrid Open/ATP)": "Madrid Open tennis ATP results",
    "Japan & Korea Travel": "Japan South Korea travel luxury tourism",
    "Tech & AI Development": "Adobe Experience Manager generative AI software",
    "Gaming Hardware": "4K OLED monitors gaming tech"
}

def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('articles', [])[:5]
    return []

def summarize_articles(articles):
    if not articles:
        return "No significant updates in this category today."
    
    context = "\n".join([f"- {a['title']}: {a['description']}" for a in articles])
    prompt = f"Summarize the following news stories into a single, high-density professional briefing paragraph for a Solution Architect. Focus on actionable facts:\n\n{context}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Summary generation temporarily unavailable."

# --- DATA PROCESSING ---
news_data = {}
for display_name, search_query in CATEGORIES.items():
    articles = fetch_news(search_query)
    summary = summarize_articles(articles)
    news_data[display_name] = {
        "summary": summary,
        "links": articles
    }

# --- HTML GENERATION (PLATINUM EDITION + ANALYTICS) ---
now = datetime.now().strftime('%d %b %Y | %I:%M %p SGT')

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligence Hub | {now}</title>
    
    <script data-goatcounter="https://jhzeussg.goatcounter.com/count"
            async src="//gc.zgo.at/count.js"></script>

    <style>
        :root {{
            --glass: rgba(255, 255, 255, 0.08);
            --bg: #0f172a;
            --accent: #38bdf8;
            --text: #f1f5f9;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'Inter', -apple-system, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 1px solid var(--glass);
            padding-bottom: 20px;
        }}
        .card {{
            background: var(--glass);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            transition: transform 0.2s ease;
        }}
        .card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
        }}
        h2 {{
            color: var(--accent);
            margin-top: 0;
            font-size: 1.25rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .summary {{
            font-size: 1.05rem;
            margin-bottom: 15px;
            color: #cbd5e1;
        }}
        .sources {{
            font-size: 0.85rem;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        a {{
            color: var(--accent);
            text-decoration: none;
            opacity: 0.8;
        }}
        a:hover {{
            opacity: 1;
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 50px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Intelligence Hub</h1>
            <p>{now}</p>
        </header>

        <main>
"""

for category, data in news_data.items():
    links_html = "".join([f'<a href="{a["url"]}" target="_blank">Source {i+1}</a> ' for i, a in enumerate(data['links'])])
    html_content += f"""
            <div class="card">
                <h2>{category}</h2>
                <div class="summary">{data['summary']}</div>
                <div class="sources">{links_html}</div>
            </div>
    """

html_content += """
        </main>
        <div class="footer">
            Generated by Gemini 1.5 Flash • Curated for Solution Architecture
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
