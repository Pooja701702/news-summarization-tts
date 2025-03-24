import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:5000/analyze"  # Flask API URL

st.title("Company News Sentiment Analysis")

company_name = st.text_input("Enter Company Name:")

if st.button("Analyze"):
    if company_name:
        payload = {"company": company_name}
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            result = response.json()

            # Display Company Name
            st.subheader(f"Company: {result['Company']}")

            # Display Articles
            st.subheader("Articles:")
            for article in result['Articles']:
                st.write(f"**Title:** {article['Title']}")
                st.write(f"**Summary:** {article['Summary']}")
                st.write(f"**Sentiment:** {article['Sentiment']}")
                st.write(f"**Topics:** {', '.join(article['Topics'])}")
                st.write("---")  # Separator

            # Display Sentiment Score
            st.subheader("Comparative Sentiment Score:")
            st.write(f"**Sentiment Distribution:** {result['Comparative Sentiment Score']['Sentiment Distribution']}")
            st.subheader("Coverage Differences:")
            for diff in result['Comparative Sentiment Score']['Coverage Differences']:
                st.write(f"**Comparison:** {diff['Comparison']}")
                st.write(f"**Impact:** {diff['Impact']}")
                st.write("---")  # Separator

            # Display Topic Overlap
            st.subheader("Topic Overlap:")
            st.write(f"**Common Topics:** {', '.join(result['Topic Overlap']['Common Topics']) if result['Topic Overlap']['Common Topics'] else 'None'}")
            st.write(f"**Unique Topics in Positive Articles:** {', '.join(result['Topic Overlap']['Unique Topics in Positive Articles']) if result['Topic Overlap']['Unique Topics in Positive Articles'] else 'None'}")
            st.write(f"**Unique Topics in Negative Articles:** {', '.join(result['Topic Overlap']['Unique Topics in Negative Articles']) if result['Topic Overlap']['Unique Topics in Negative Articles'] else 'None'}")

            # Display Final Sentiment Analysis
            st.subheader("Final Sentiment Analysis:")
            st.write(result['Final Sentiment Analysis'])

            # Display Audio
            if "Audio" in result:
                st.audio("output.mp3")

        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with API: {e}")
        except json.JSONDecodeError:
            st.error("Invalid JSON response from API.")
    else:
        st.warning("Please enter a company name.")