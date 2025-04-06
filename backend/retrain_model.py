import json
import pandas as pd
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
from pathlib import Path
from config import LOCAL_MODEL_DIR


# Load the JSON dataset with error handling
def load_data(filename='swiggyindia_all_posts.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Loaded {len(data)} posts from {filename}.")
        # Check if the data is empty
        
        return data
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found. Please ensure it is in the same directory as this script.")
        print(f"Current directory: {Path.cwd()}")
        return []

# Extract features from the dataset (only hour and day_of_week)
def extract_features(data):
    if not data:
        return pd.DataFrame()
    features = []
    print("extracting features...")
    for post in data:
        dt = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))

        # Basic features
        hour = dt.hour
        day_of_week = dt.strftime('%A')
        is_peak_hour = 1 if 12 <= hour <= 18 else 0
        is_weekday = 1 if dt.weekday() < 5 else 0

        # Store features and target (excluding days_since_first_post and avg_likes_last_5)
        features.append({
            'hour': hour,
            'day_of_week': day_of_week,
            'is_peak_hour': is_peak_hour,
            'is_weekday': is_weekday,
            'likes_count': post['likes_count']
        })
    print("features extracted!")
    # Convert to DataFrame
    
    print("converting to dataframe...")
    features = pd.DataFrame(features)
    print("features converted!")
    # Drop rows with NaN values
    features.dropna(inplace=True)
    # Ensure likes_count is numeric
    features['likes_count'] = pd.to_numeric(features['likes_count'], errors='coerce')
    features.dropna(subset=['likes_count'], inplace=True)  # Drop rows where likes_count is NaN
    print(pd.DataFrame(features))
    print("features ready!")
    return pd.DataFrame(features)

# Prepare data
def prepare_data(df):
    print("preparing data.....")
    if df.empty:
        print("Error: No data available to prepare.")
        return pd.DataFrame(), pd.Series(dtype='float64')  # Return an empty Series with a specified dtype
    print("preparing dataframe...")
    # Encode day_of_week using one-hot encoding
    df = pd.get_dummies(df, columns=['day_of_week'], drop_first=True)
    print("dataframe prepared!")
    # Separate features and target
    X = df.drop(columns=['likes_count'])
    y = df['likes_count']
    print("data has been prepared!")
    return X, y

# Train the model with tuned hyperparameters
def train_model(X, y):
    print("training data.....")
    if X.empty or y.empty:
        print("Error: No data available to train the model.")
        return None, None
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the XGBoost Regressor with tuned parameters
    model = xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error on Test Set: {mae:.2f}")

    return model, X_train.columns.tolist()

def retrain_model(data):
    """
    Retrain the model with new data.
    """
    try:
        # Extract features from the data
        features = extract_features(data)
        
        # Ensure features is a DataFrame
        if isinstance(features, tuple):
            features = features[0]  # Assuming the first element is the DataFrame

        # Debugging: Print the first few rows of the DataFrame
        print("Extracted features:")
        print(features.head())

        # Prepare data for training
        X, y = prepare_data(features)

        # Train the model
        new_model, feature_names = train_model(X, y)

        # Save the new model and feature names
        model_path = LOCAL_MODEL_DIR / 'likes_predictor.joblib'
        joblib.dump({'model': new_model, 'feature_names': feature_names}, model_path)

        print("Model retrained and saved successfully.")
        return True
    except Exception as e:
        print(f"Error during retraining: {e}")
        return False

# Main execution
def main(post_data_file='swiggyindia_posts.json'):
    try:
        # Load and prepare data
        data = load_data(post_data_file)
        df = extract_features(data)
        X, y = prepare_data(df)

        # Check if data is empty before proceeding
        if X.empty or y.empty:
            print("Error: No data available for training.")
            return

        # Train the model
        model, feature_names = train_model(X, y)

        if model:
            LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
            # Save the model and feature names
            model_path = LOCAL_MODEL_DIR / 'likes_predictor.joblib'
            joblib.dump({'model': model, 'feature_names': feature_names}, model_path)
            print(f"Model saved to {model_path}")
            return  model, feature_names
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()