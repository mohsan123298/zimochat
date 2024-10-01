import requests
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.http import JsonResponse
import glob
from textblob import TextBlob

# Constants for Crypto API
CRYPTOCOMPARE_API_KEY = 'ed10f0c946b3cb641714b26a51709f64c7541505f01cc5610c05d4f874a32fce'
CRYPTOCOMPARE_BASE_URL = 'https://min-api.cryptocompare.com/data'
GOOGLE_API_KEY = 'AIzaSyB0YUtBMDug85PCO_25xdr67TMhWxuKk3g'
CSE_ID = '76707d3022bfe45ae'


# 1. Load data from multiple CSV files (for healthcare bot)
def load_data():
    queries = []
    responses = []
    
    for filename in glob.glob('chat_bot/data/medical/*.csv'):
        df=pd.read_csv(filename)
        
        required_column=['Question','Answer']
        # print(f"Columns in {filename}: {df.columns}")
        
        if all(col in df.columns for col in required_column):
            df.fillna('', inplace=True)
            filtered_df = df[df['Question'].str.strip() != '']  # Filter empty questions
            queries.extend(filtered_df['Question'].astype(str).tolist())
            responses.extend(filtered_df['Answer'].astype(str).tolist())
        else:
            print(f"Missing columns in {filename}: {set(required_column) - set(df.columns)}")
    return queries, responses




# 2. Train TF-IDF vectorizer for the chatbot
def train_bot():
    queries, responses = load_data()
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(queries)
    return X, vectorizer, queries, responses


# 3. Google Search fallback
def google_search(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    try:
        response = requests.get(search_url)
        results = response.json()
        links = [item['link'] for item in results.get('items', [])[:3]]
        return "\n".join(links) if links else "No relevant links found."
    except Exception as e:
        return f"Error occurred while searching on Google: {str(e)}"


# 4. Cryptocurrency data fetcher
def get_coin_data(coin_name):
    try:
        coin_symbol = coin_name.upper()
        headers = {'authorization': f'Apikey {CRYPTOCOMPARE_API_KEY}'}
        response = requests.get(f'{CRYPTOCOMPARE_BASE_URL}/pricemultifull',
                                params={'fsyms': coin_symbol, 'tsyms': 'USD'},
                                headers=headers)
        coin_data = response.json()

        if 'DISPLAY' in coin_data and coin_symbol in coin_data['DISPLAY']:
            coin_info = coin_data['DISPLAY'][coin_symbol]['USD']
            response_message = ""
            for key, value in coin_info.items():
                response_message += f"<strong>{key}:</strong> {value}<br>"
            return response_message
        else:
            return None  # Return None if no valid data is found
    except Exception as e:
        return None  # Return None if an error occurs


# 5. Get response from the bot
def bot_response(user_input, X, vectorizer, queries, responses):
    if not user_input:
        return "I'm sorry, I didn't understand that."

    try:
        # Transform user input into vector space
        user_vec = vectorizer.transform([user_input])
        similarity = cosine_similarity(user_vec, X)
        best_match_idx = np.argmax(similarity)

        if best_match_idx >= len(responses):
            raise IndexError("Best match index out of range")

        max_similarity = similarity[0][best_match_idx]

        # If similarity is too low, fall back to Google search

            
        if max_similarity < 0.1:
            return f"I couldn't find a good match in my dataset. Here are some links from Google:\n{google_search(user_input)}"

        return responses[best_match_idx]

    except (IndexError, ValueError, Exception) as e:
        print(f"Error occurred: {str(e)}")
        return f"Sorry, I couldn't process your request. Here's what I found from Google:\n{google_search(user_input)}"


# 6. Sentiment analysis and overall response
def process_message(user_input, X, vectorizer, queries, responses):
    # Perform sentiment analysis
    analyse = TextBlob(user_input)
    sentiment = analyse.sentiment.polarity
    
    # Convert input to lowercase and split into words
    input = user_input.lower()
    words = input.split()
    
    # Check for cryptocurrency-related keywords
    for word in words:
        coin_data = get_coin_data(word)
  

    # Sentiment-based response
    if sentiment > 0:
        response = 'That sounds really good! Happy to hear this from you. If you have any questions, feel free to ask.'
    elif sentiment < 0:
        response = 'That sounds bad. I am sorry to hear that. If you have any questions, feel free to ask.'
    elif coin_data:
        response = coin_data
    else:
        # Fallback to healthcare bot response
        response = bot_response(user_input, X, vectorizer, queries, responses)

    return response
