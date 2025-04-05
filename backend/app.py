import joblib
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from config import LOCAL_DATA_DIR, LOCAL_MODEL_DIR, LOCAL_PROFILE_DIR
from predict_like import extract_features, predict_likes
from utils import load_data
from retrain_model import main as train_the_model, prepare_data, train_model


app = Flask(__name__)
CORS(app)

# Load the pre-trained model and feature names
try:
    # Ensure the model directory exists
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if the model file exists
    if not (LOCAL_MODEL_DIR / 'likes_predictor.joblib').exists():
        # raise FileNotFoundError("Model file not found. Please train the model first.")
        train_the_model()
    # Load the model and feature names from the joblib file
    model_data_path = LOCAL_MODEL_DIR / 'likes_predictor.joblib'
    model_data = joblib.load(model_data_path)
    model = model_data['model']
    feature_names = model_data['feature_names']
except FileNotFoundError:
    print("Error: 'likes_predictor.joblib' not found. Please train the model first.")
    model, feature_names = None, None

# API endpoint for the API details
@app.route('/', methods=['GET'])
def index():
    current_time = datetime.now()
    protocol = request.scheme
    hostname = request.host

    return jsonify({
        'protocol': protocol,
        'hostname': hostname,
        'current_date': current_time.strftime('%Y-%m-%d'),
        'current_time': current_time.strftime('%H:%M:%S'),
        'api_methods': [
            {
                'method': 'GET',
                'endpoint': '/',
                'description': 'Returns a list of available API methods and their functionality.'
            },
            {
                'method': 'GET',
                'endpoint': '/api/stats',
                'description': 'Fetches statistics and engagement trends.'
            },
            {
                'method': 'POST',
                'endpoint': '/api/predict/likes',
                'description': 'Predicts the number of likes based on hour and day.'
            }
        ]
    }), 200

# API endpoint for stats
@app.route('/api/stats', methods=['GET'])
def get_stats():
    data = load_data()
    if not data:
        return jsonify({'error': 'Data not found'}), 404

    # Extract features and calculate statistics
    stats, best_time, best_day, top_post, engagement_trend = extract_features(data)
    
    return jsonify({
        'stats': stats,
        'bestTime': int(best_time),
        'bestDay': best_day,
        'topPost': top_post,
        'engagementTrend': engagement_trend
    })

# API endpoint for prediction (using only hour and day)
@app.route('/api/predict/likes', methods=['POST'])
def predict():
    """
    Predict the number of likes based on hour and day of the week.
    Expects a JSON payload with 'hour' (0-23) and 'day' (e.g., 'Monday').
    Returns the predicted number of likes.
    e.g. {
        "hour": 12,
        "day": "Monday"
    }
    
    """
    try:
        # Get input from the request
        data = request.get_json()
        hour = int(data['hour'])
        day_of_week = data['day']

        # Validate inputs
        if not (0 <= hour <= 23):
            return jsonify({'error': 'Hour must be between 0 and 23'}), 400

        # Make prediction
        predicted_likes = predict_likes(model, feature_names, hour, day_of_week)
        return jsonify({'predictedLikes': predicted_likes})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/retrain', methods=['POST'])
def retrain_model():
    try:
        # Load and prepare new data
        data = request.get_json()
        username = data['username']
        username_data_path = LOCAL_PROFILE_DIR / f"{username}/posts.json"
        data = load_data(username_data_path)  # Assuming new data is fetched and saved in the same file
        df = extract_features(data)
        X, y = prepare_data(df)

        # Train the model
        new_model, feature_names = train_model(X, y)

        if new_model:
            # Save the new model and feature names
            model_path = LOCAL_MODEL_DIR / 'likes_predictor.joblib'
            joblib.dump({'model': new_model, 'feature_names': feature_names}, model_path)

            # Update the global model and feature names
            global model
            global feature_names
            model = new_model
            feature_names = feature_names

            return jsonify({'message': 'Model retrained and updated successfully.'}), 200
        else:
            return jsonify({'error': 'Model retraining failed.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)