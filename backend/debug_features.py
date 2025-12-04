from ml_engine.feature_extractor import FeatureExtractor
import pandas as pd

urls = [
    "http://192.168.1.5/banking",
    "http://paypaI.com",
    "http://faceboook.com",
    "http://google.com",
    "http://secure-login.xyz"
]

print(f"{'URL':<30} | {'IP':<5} | {'TLD':<5} | {'Key':<5} | {'Dash':<5} | {'Dot':<5}")
print("-" * 70)

for url in urls:
    extractor = FeatureExtractor(url)
    f = extractor.extract_features()
    print(f"{url:<30} | {f['is_ip']:<5} | {f['suspicious_tld']:<5} | {f['suspicious_keywords']:<5} | {f['dash_count']:<5} | {f['dot_count']:<5}")
