import joblib
import pandas as pd
import os
from .feature_extractor import FeatureExtractor

class PhishDetector:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'model.pkl')
        scaler_path = os.path.join(current_dir, 'scaler.pkl')
        
        # Load model
        try:
            self.model = joblib.load(model_path)
            print(f"✓ ML Model loaded from {model_path}")
        except Exception as e:
            print(f"✗ Failed to load ML model: {e}")
            self.model = None
        
        # Load scaler
        try:
            self.scaler = joblib.load(scaler_path)
            print(f"✓ Feature scaler loaded from {scaler_path}")
        except Exception as e:
            print(f"⚠ Scaler not found, predictions will use unscaled features: {e}")
            self.scaler = None
        
        # Load model metadata if available
        metadata_path = os.path.join(current_dir, 'model_metadata.pkl')
        try:
            self.metadata = joblib.load(metadata_path)
            print(f"✓ Model metadata loaded: Accuracy={self.metadata.get('accuracy', 'N/A')}")
        except:
            self.metadata = {}

    def predict(self, url):
        """Predict if URL is phishing with explainability"""
        extractor = FeatureExtractor(url)
        features = extractor.extract_features()
        
        # Convert features to DataFrame for prediction
        df = pd.DataFrame([features])
        
        score = 0
        reasons = []
        is_phishing = False
        confidence = 0.0

        if self.model:
            try:
                # Apply scaling if scaler is available
                if self.scaler:
                    df_scaled = pd.DataFrame(
                        self.scaler.transform(df),
                        columns=df.columns
                    )
                else:
                    df_scaled = df
                
                # Get probability of class 1 (Phishing)
                probabilities = self.model.predict_proba(df_scaled)
                score = probabilities[0][1]  # Probability of phishing
                confidence = max(probabilities[0])  # Confidence in prediction
                is_phishing = score > 0.60
                
            except Exception as e:
                print(f"⚠ Prediction error: {e}")
                # Fallback to heuristics if model fails
                score = self._heuristic_score(features, reasons)
                is_phishing = score > 0.60
                confidence = score
        else:
            # Fallback to heuristics if no model
            score = self._heuristic_score(features, reasons)
            is_phishing = score > 0.60
            confidence = score

        # Add explainability reasons based on features
        self._add_reasons(features, reasons)

        return {
            "score": float(score),
            "is_phishing": bool(is_phishing),
            "confidence": float(confidence),
            "features": features,
            "reasons": reasons
        }

    def _heuristic_score(self, features, reasons):
        """Fallback heuristic scoring when model is unavailable"""
        score = 0
        
        # High-risk indicators
        if features.get('is_ip', 0): 
            score += 0.40
        if features.get('suspicious_tld', 0): 
            score += 0.35
        if features.get('suspicious_keywords', 0): 
            score += 0.30
        if features.get('typosquatting', 0): 
            score += 0.50
        if features.get('homograph_attack', 0): 
            score += 0.45
        
        # Medium-risk indicators
        if features.get('brand_keywords', 0): 
            score += 0.25
        if features.get('https_token', 0): 
            score += 0.30
        if features.get('has_at_symbol', 0): 
            score += 0.20
        
        # Normalize to 0-1 range
        return min(score, 0.99)

    def _add_reasons(self, features, reasons):
        """Generate human-readable reasons for the prediction"""
        # Critical security issues
        if features.get('is_ip', 0):
            reasons.append("⚠ IP address used instead of domain name")
        
        if features.get('typosquatting', 0):
            reasons.append("⚠ Domain appears to mimic a well-known brand")
        
        if features.get('homograph_attack', 0):
            reasons.append("⚠ Contains lookalike characters (homograph attack)")
        
        # Suspicious patterns
        if features.get('suspicious_tld', 0):
            reasons.append("⚠ Suspicious top-level domain (TLD)")
        
        if features.get('suspicious_keywords', 0):
            reasons.append("⚠ Contains sensitive keywords (login, verify, account, etc.)")
        
        if features.get('brand_keywords', 0):
            reasons.append("⚠ Brand name appears in suspicious location")
        
        if features.get('https_token', 0):
            reasons.append("⚠ 'HTTPS' appears in domain name (deceptive)")
        
        if features.get('double_slash_redirect', 0):
            reasons.append("⚠ Double slash redirection detected")
        
        if features.get('has_at_symbol', 0):
            reasons.append("⚠ '@' symbol in URL (potential credential phishing)")
        
        if features.get('url_shortening', 0):
            reasons.append("ℹ URL shortening service detected")
        
        # Statistical anomalies
        if features.get('url_entropy', 0) > 4.5:
            reasons.append("ℹ High URL randomness detected")
        
        if features.get('digit_ratio', 0) > 0.3:
            reasons.append("ℹ Unusually high number of digits in URL")
        
        if features.get('subdomain_count', 0) > 3:
            reasons.append("ℹ Excessive subdomains detected")
        
        if features.get('url_encoded_chars', 0) > 5:
            reasons.append("ℹ High number of encoded characters")
        
        # Positive indicators (if no reasons found)
        if not reasons:
            if features.get('is_https', 0):
                reasons.append("✓ Uses HTTPS protocol")
            reasons.append("✓ No obvious phishing indicators detected")

