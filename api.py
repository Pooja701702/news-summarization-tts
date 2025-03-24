from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from transformers import pipeline
from textblob import TextBlob
from gtts import gTTS
import os
import json
import requests

app = Flask(__name__)

# Load the summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def fetch_news(company_name):
    """Fetches latest news headlines related to a company."""
    search_url = f"https://news.google.com/search?q={company_name}"
    try:
        response = requests.get(search_url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        for item in soup.find_all("h3")[:5]:  # Get top 5 news articles
            title = item.text
            articles.append(title)
        return articles
    except requests.exceptions.RequestException as e:
        return [f"Error fetching news: {e}"]

def get_sentiment(text):
    """Analyzes the sentiment of a given text."""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def text_to_speech(text, language='hi'):
    """Converts text to Hindi speech using gTTS (Google Text-to-Speech)."""
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save("output.mp3")
        os.system("start output.mp3")  # For Windows, change to 'open output.mp3' for Mac/Linux
        return "Audio generated"
    except Exception as e:
        return f"Error generating audio: {e}"

def analyze_news_sentiments(company_name):
    """Fetches news, summarizes, analyzes sentiment, and structures output."""
    articles = fetch_news(company_name)
    analyzed_news = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
   
    for article in articles:
        if "Error fetching news:" in article:
            return {"error": article}

        try:
            summary = summarizer(article, max_length=50, min_length=10, do_sample=False)[0]["summary_text"]
            sentiment = get_sentiment(summary)
            sentiment_counts[sentiment] += 1
            topics = ["Stock Market", "Electric Vehicles", "Regulations", "Innovation", "Autonomous Vehicles"]
            assigned_topics = topics[:3] if sentiment == "Positive" else topics[3:] if sentiment == "Negative" else topics[1:3]

            analyzed_news.append({
                "Title": article,
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": assigned_topics
            })
        except Exception as e:
            return {"error": f"Error processing article '{article}': {e}"}

    total_articles = len(articles)
    sentiment_distribution = {key: round((value / total_articles) * 100, 2) for key, value in sentiment_counts.items()}
   
    output = {
        "Company": company_name,
        "Articles": analyzed_news,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_counts,
            "Coverage Differences": [
                {
                    "Comparison": "Article 1 highlights positive aspects, while others discuss challenges.",
                    "Impact": "Positive news can boost investor confidence, while negative news may indicate risks."
                },
                {
                    "Comparison": "Articles cover financial growth, regulatory issues, and innovation.",
                    "Impact": "Provides a comprehensive view of the company's current standing."
                }
            ]
        },
        "Topic Overlap": {
            "Common Topics": ["Electric Vehicles"] if "Electric Vehicles" in [topic for news in analyzed_news for topic in news["Topics"]] else [],
            "Unique Topics in Positive Articles": list(set([topic for news in analyzed_news if news["Sentiment"] == "Positive" for topic in news["Topics"]]) - set([topic for news in analyzed_news if news["Sentiment"] != "Positive" for topic in news["Topics"]])),
            "Unique Topics in Negative Articles": list(set([topic for news in analyzed_news if news["Sentiment"] == "Negative" for topic in news["Topics"]]) - set([topic for news in analyzed_news if news["Sentiment"] != "Negative" for topic in news["Topics"]]))
        },
        "Final Sentiment Analysis": f"{company_name}'s latest news coverage indicates a mix of optimism and challenges.",
        "Audio": "[Play Hindi Speech]"
    }

    hindi_text = f"{company_name} के नवीनतम समाचार कवरेज में आशावाद और चुनौतियों का मिश्रण है।"
    text_to_speech(hindi_text, language='hi')
   
    return output

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    company_name = data.get('company')
    if not company_name:
        return jsonify({"error": "Company name is required"}), 400
    result = analyze_news_sentiments(company_name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)