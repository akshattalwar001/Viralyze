from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np
import json

app = Flask(__name__)
CORS(app)
load_dotenv()

# Load sample data from JSON file
def load_sample_data():
    with open('data/sample_posts.json', 'r') as file:
        return json.load(file)

# Initialize the database
def init_db():
    conn = sqlite3.connect('instagram.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (post_id TEXT, likes INTEGER, comments INTEGER, shares INTEGER, timestamp TEXT)''')
    conn.commit()
    conn.close()

# Load or train the ML model
MODEL_PATH = 'likes_predictor.joblib'
LABEL_ENCODER_PATH = 'label_encoder_day.joblib'

def train_or_load_model(posts):
    # Initialize label_encoder_day
    label_encoder_day = LabelEncoder()

    # Define all days of the week to ensure the encoder knows them
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if os.path.exists(MODEL_PATH) and os.path.exists(LABEL_ENCODER_PATH):
        # Load the existing model and label encoder
        model = joblib.load(MODEL_PATH)
        label_encoder_day = joblib.load(LABEL_ENCODER_PATH)
    else:
        # Prepare the data for training
        X = []
        y = []

        for post in posts:
            dt = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
            hour = dt.hour
            day = dt.strftime('%A')
            X.append([hour, day])
            y.append(post['likes_count'])

        # Encode the day of the week
        days = [x[1] for x in X]
        # Fit the encoder on all days to avoid unseen labels
        label_encoder_day.fit(all_days)
        encoded_days = label_encoder_day.transform(days)
        X = [[x[0], encoded_days[i]] for i, x in enumerate(X)]

        # Train a linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Save the model and label encoder
        joblib.dump(model, MODEL_PATH)
        joblib.dump(label_encoder_day, LABEL_ENCODER_PATH)

    return model, label_encoder_day

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        # Load sample data
        posts = load_sample_data()

        # Save to SQLite
        conn = sqlite3.connect('instagram.db')
        c = conn.cursor()
        for post in posts:
            c.execute('INSERT OR IGNORE INTO posts VALUES (?, ?, ?, ?, ?)',
                      (post['id'], post['likes_count'], post['comments_count'], 0, post['timestamp']))
        conn.commit()
        conn.close()

        # AI: Best posting hour
        hourly_likes = {}
        for post in posts:
            hour = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')).hour
            hourly_likes[hour] = hourly_likes.get(hour, 0) + post['likes_count']
        best_hour = max(hourly_likes, key=hourly_likes.get)

        # AI: Best day of the week
        daily_likes = {}
        for post in posts:
            day = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')).strftime('%A')
            daily_likes[day] = daily_likes.get(day, 0) + post['likes_count']
        best_day = max(daily_likes, key=daily_likes.get)

        # AI: Engagement rate per post
        engagement_rates = []
        for post in posts:
            total_engagement = post['likes_count'] + post['comments_count']
            engagement_rates.append({
                'post_id': post['id'],
                'engagement': total_engagement,
                'timestamp': post['timestamp']
            })
        top_post = max(engagement_rates, key=lambda x: x['engagement'])

        # AI: Engagement trend
        posts_sorted = sorted(posts, key=lambda x: x['timestamp'])
        engagement_trend = []
        for i in range(1, len(posts_sorted)):
            prev_engagement = posts_sorted[i-1]['likes_count'] + posts_sorted[i-1]['comments_count']
            curr_engagement = posts_sorted[i]['likes_count'] + posts_sorted[i]['comments_count']
            trend = 'up' if curr_engagement > prev_engagement else 'down'
            engagement_trend.append({
                'from': posts_sorted[i-1]['timestamp'],
                'to': posts_sorted[i]['timestamp'],
                'trend': trend,
                'change': curr_engagement - prev_engagement
            })

        return jsonify({
            'stats': posts,
            'bestTime': f'{best_hour}:00',
            'bestDay': best_day,
            'topPost': top_post,
            'engagementTrend': engagement_trend
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_likes():
    try:
        data = request.get_json()
        hour = int(data['hour'])
        day = data['day']

        # Load the model and label encoder
        model = joblib.load(MODEL_PATH)
        label_encoder_day = joblib.load(LABEL_ENCODER_PATH)

        # Prepare the input for prediction
        encoded_day = label_encoder_day.transform([day])[0]
        X_pred = [[hour, encoded_day]]

        # Make the prediction
        predicted_likes = model.predict(X_pred)[0]
        predicted_likes = max(0, int(predicted_likes))  # Ensure non-negative integer

        return jsonify({'predictedLikes': predicted_likes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load sample data and train or load the model at startup
    sample_posts = load_sample_data()
    train_or_load_model(sample_posts)
    init_db()
    app.run(port=int(os.getenv('FLASK_PORT', 5000)), debug=True)