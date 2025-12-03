import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from feature_extractor import FeatureExtractor
import os

# Load dataset
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, 'dataset.csv')
df = pd.read_csv(dataset_path)

print(f"Loaded {len(df)} URLs from {dataset_path}")

# Extract features
print("Extracting features...")
features_list = []
for url in df['url']:
    extractor = FeatureExtractor(url)
    features_list.append(extractor.extract_features())

X = pd.DataFrame(features_list)
y = df['label']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Model
print("Training Random Forest Model...")
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save Model
model_path = os.path.join(current_dir, 'model.pkl')
joblib.dump(clf, model_path)
print(f"Model saved to {model_path}")
