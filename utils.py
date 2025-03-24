import os
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from textblob import TextBlob
from gtts import gTTS

# Load the summarization model explicitly
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def fetch_news(company_name):
    """Fetches latest news headlines related to a company."""
    search_url = f"https://news.google.com/search?q={company_name}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Ensure response is valid
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
    """Converts text to Hindi speech using gTTS."""
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save("output.mp3")
        print("Audio saved as output.mp3")
    except Exception as e:
        print(f"Error generating audio: {e}")

# Test Run
if __name__ == "__main__":
    company_name = "Tesla"
    print(f"Fetching news for: {company_name}")

    articles = fetch_news(company_name)
    print(f"News Articles: {articles}")

    for article in articles:
        try:
            summary = summarizer(article, max_length=50, min_length=10, do_sample=False)[0]["summary_text"]
            sentiment = get_sentiment(summary)
            print(f"\nTitle: {article}")
            print(f"Summary: {summary}")
            print(f"Sentiment: {sentiment}")
        except Exception as e:
            print(f"Error summarizing article '{article}': {e}")

    text_to_speech(f"{company_name} के नवीनतम समाचार कवरेज में आशावाद और चुनौतियों का मिश्रण है।")
    print("✅ Script executed successfully!")


