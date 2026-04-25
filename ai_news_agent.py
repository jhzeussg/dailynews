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
    # Tailored search query for your specific interests
    query = "(Singapore business OR SGX) OR (AI automation tech lead) OR (Japan Korea travel) OR (ATP tennis news)"
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=20&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        context = ""
        for a in articles:
            context += f"Source: {a['source']['name']}\nTitle: {a['title']}\nSnippet: {a['description']}\nLink: {a['url']}\n\n"
        return context
    except Exception as e:
        return f"Error fetching news: {e}"

def generate_ai_summary(raw_data):
    prompt = f"""
    You are an AI Chief of Staff. Summarize the following news into a clean, executive "Basket of Categories" for a 60-year-old Tech Lead and Investor in Singapore.
    
    Structure the response with these exact headers:
    - 🇸🇬 Singapore & Business (Focus on SME grants, local banks, and infrastructure)
    - 💰 Finance & SGX (Focus on REITs, dividends, and blue chips)
    - 🤖 Technology & AI (Focus on enterprise automation and agentic AI)
    - 🎾 Sports & Travel (Professional tennis updates and Japan/Korea travel trends)

    For each category, provide 2-3 bullet points. Each bullet must end with a [Source Link].
    Format everything in valid HTML. Use <h2> for headers and <ul>/<li> for lists.
    
    Data:
    {raw_data}
    """
    response = model.generate_content(prompt)
    return response.text

# Main Execution
news_context = get_basket_news()
ai_html_body = generate_ai_summary(news_context)

# Final HTML Wrapper with basic styling
final_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Daily Intelligence Hub</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; background-color: #f4f7f6; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #2980b9; margin-top: 30px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 10px; }}
        a {{ color: #3498db; text-decoration: none; font-size: 0.9em; }}
        .date {{ color: #7f8c8d; font-style: italic; }}
    </style>
</head>
<body>
    <h1>Daily Intelligence Hub</h1>
    <p class="date">Last updated: {datetime.now().strftime('%d %B %Y, %I:%M %p')} SGT</p>
    {ai_html_body}
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)
