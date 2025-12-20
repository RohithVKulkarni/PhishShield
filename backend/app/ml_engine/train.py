import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)
from .feature_extractor import FeatureExtractor
import os
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# Try to import advanced libraries
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
    print("✓ XGBoost available")
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠ XGBoost not available, will use alternatives")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
    print("✓ LightGBM available")
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠ LightGBM not available, will use alternatives")

print("\n" + "="*70)
print("PHISHSHIELD ML MODEL TRAINING")
print("="*70 + "\n")

# Load dataset
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, 'dataset.csv')
df = pd.read_csv(dataset_path)

print(f"📊 Dataset loaded: {len(df)} URLs")
print(f"   - Phishing URLs: {sum(df['label'] == 1)}")
print(f"   - Legitimate URLs: {sum(df['label'] == 0)}")
print(f"   - Class balance: {sum(df['label'] == 1) / len(df) * 100:.1f}% phishing\n")

# Extract features
print("🔍 Extracting features from URLs...")
features_list = []
failed_urls = 0

for idx, url in enumerate(df['url']):
    try:
        extractor = FeatureExtractor(url)
        features_list.append(extractor.extract_features())
    except Exception as e:
        print(f"   ⚠ Failed to extract features from URL {idx}: {e}")
        failed_urls += 1
        # Add dummy features for failed URLs
        features_list.append({})

if failed_urls > 0:
    print(f"   ⚠ Failed to process {failed_urls} URLs\n")

X = pd.DataFrame(features_list)
y = df['label']

# Remove rows with missing features
valid_indices = X.notna().all(axis=1)
X = X[valid_indices]
y = y[valid_indices]

print(f"✓ Feature extraction complete")
print(f"   - Total features: {len(X.columns)}")
print(f"   - Valid samples: {len(X)}")
print(f"   - Feature names: {', '.join(list(X.columns)[:10])}...\n")

# Feature scaling
print("📏 Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
print("✓ Features scaled using StandardScaler\n")

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"📂 Data split:")
print(f"   - Training set: {len(X_train)} samples")
print(f"   - Test set: {len(X_test)} samples\n")

# Define models to train
models = {}

# Random Forest (baseline)
print("🌲 Training Random Forest (baseline)...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
models['Random Forest'] = rf_model

# Gradient Boosting (scikit-learn)
print("🚀 Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=5,
    min_samples_split=5,
    min_samples_leaf=2,
    subsample=0.8,
    random_state=42
)
models['Gradient Boosting'] = gb_model

# XGBoost (if available)
if XGBOOST_AVAILABLE:
    print("⚡ Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    models['XGBoost'] = xgb_model

# LightGBM (if available)
if LIGHTGBM_AVAILABLE:
    print("💡 Training LightGBM...")
    lgb_model = lgb.LGBMClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    models['LightGBM'] = lgb_model

print()

# Train and evaluate all models
results = {}
best_model = None
best_score = 0
best_model_name = ""

print("="*70)
print("MODEL TRAINING & EVALUATION")
print("="*70 + "\n")

for name, model in models.items():
    print(f"Training {name}...")
    
    # Train model
    model.fit(X_train, y_train)
    
    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
    
    # Test set predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    results[name] = {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std()
    }
    
    print(f"✓ {name} Results:")
    print(f"   - Accuracy:  {accuracy*100:.2f}%")
    print(f"   - Precision: {precision*100:.2f}%")
    print(f"   - Recall:    {recall*100:.2f}%")
    print(f"   - F1-Score:  {f1*100:.2f}%")
    print(f"   - ROC-AUC:   {roc_auc:.4f}")
    print(f"   - CV Score:  {cv_scores.mean()*100:.2f}% (±{cv_scores.std()*100:.2f}%)")
    print()
    
    # Track best model based on F1-score (balanced metric)
    if f1 > best_score:
        best_score = f1
        best_model = model
        best_model_name = name

print("="*70)
print(f"🏆 BEST MODEL: {best_model_name}")
print(f"   F1-Score: {best_score*100:.2f}%")
print("="*70 + "\n")

# Detailed evaluation of best model
print("DETAILED EVALUATION OF BEST MODEL")
print("="*70 + "\n")

y_pred_best = best_model.predict(X_test)
y_pred_proba_best = best_model.predict_proba(X_test)[:, 1]

print("Classification Report:")
print(classification_report(y_test, y_pred_best, target_names=['Legitimate', 'Phishing']))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred_best)
print(f"                 Predicted")
print(f"                 Legit  Phish")
print(f"Actual Legit     {cm[0][0]:5d}  {cm[0][1]:5d}")
print(f"       Phish     {cm[1][0]:5d}  {cm[1][1]:5d}")

# Feature importance
print("\n" + "="*70)
print("TOP 15 MOST IMPORTANT FEATURES")
print("="*70 + "\n")

if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(15).iterrows():
        bar_length = int(row['importance'] * 50)
        bar = '█' * bar_length
        print(f"{row['feature']:25s} {bar} {row['importance']:.4f}")
    
    # Save feature importance
    importance_path = os.path.join(current_dir, 'feature_importance.csv')
    feature_importance.to_csv(importance_path, index=False)
    print(f"\n✓ Feature importance saved to {importance_path}")

# Save the best model
print("\n" + "="*70)
print("SAVING MODEL ARTIFACTS")
print("="*70 + "\n")

model_path = os.path.join(current_dir, 'model.pkl')
scaler_path = os.path.join(current_dir, 'scaler.pkl')
metadata_path = os.path.join(current_dir, 'model_metadata.pkl')

joblib.dump(best_model, model_path)
print(f"✓ Model saved to {model_path}")

joblib.dump(scaler, scaler_path)
print(f"✓ Scaler saved to {scaler_path}")

# Save metadata
metadata = {
    'model_name': best_model_name,
    'accuracy': results[best_model_name]['accuracy'],
    'precision': results[best_model_name]['precision'],
    'recall': results[best_model_name]['recall'],
    'f1_score': results[best_model_name]['f1'],
    'roc_auc': results[best_model_name]['roc_auc'],
    'training_date': datetime.now().isoformat(),
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'num_features': len(X.columns),
    'feature_names': list(X.columns)
}

joblib.dump(metadata, metadata_path)
print(f"✓ Metadata saved to {metadata_path}")

print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)
print(f"\nModel: {best_model_name}")
print(f"Accuracy: {results[best_model_name]['accuracy']*100:.2f}%")
print(f"F1-Score: {results[best_model_name]['f1']*100:.2f}%")
print(f"Ready for deployment! 🚀")

