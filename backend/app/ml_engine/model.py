import joblib
import pandas as pd
import os
from .feature_extractor import FeatureExtractor

class PhishDetector:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'model.pkl')
        try:
            self.model = joblib.load(model_path)
            print(f"ML Model loaded from {model_path}")
        except Exception as e:
            print(f"Failed to load ML model: {e}")
            self.model = None

    def predict(self, url):
        extractor = FeatureExtractor(url)
        features = extractor.extract_features()
        
        # Convert features to DataFrame for prediction
        df = pd.DataFrame([features])
        
        score = 0
        reasons = []
        is_phishing = False

        if self.model:
            # Get probability of class 1 (Phishing)
            try:
                probabilities = self.model.predict_proba(df)
                score = probabilities[0][1]
                is_phishing = score > 0.60
            except Exception as e:
                print(f"Prediction error: {e}")
                # Fallback to heuristics if model fails
                score = self._heuristic_score(features, reasons)
                is_phishing = score > 0.60
        else:
            # Fallback to heuristics
            score = self._heuristic_score(features, reasons)
            is_phishing = score > 0.60

        # Add explainability reasons based on features (Model is black box, so we still use heuristics for reasons)
        self._add_reasons(features, reasons)

        return {
            "score": float(score),
            "is_phishing": bool(is_phishing),
            "features": features,
            "reasons": reasons
        }

    def _heuristic_score(self, features, reasons):
        score = 0
        if features['is_ip']: score += 0.40
        if features['suspicious_tld']: score += 0.35
        if features['suspicious_keywords']: score += 0.30
        return min(score, 0.99)

    def _add_reasons(self, features, reasons):
        if features['is_ip']: reasons.append("IP address used as domain")
        if features['suspicious_tld']: reasons.append("Suspicious Top-Level Domain (TLD)")
        if features['suspicious_keywords']: reasons.append("Sensitive keywords found in URL")
        if features['double_slash_redirect']: reasons.append("Double slash redirection found")
        if features['https_token']: reasons.append("HTTPS token in domain name")
