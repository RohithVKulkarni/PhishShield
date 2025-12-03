# PhishShield AI

Real-Time Adaptive Phishing Detection and Prevention System.

## Project Structure

-   `backend/`: FastAPI microservice for scoring and feedback.
-   `extension/`: Chrome/Firefox MV3 extension.
-   `ml_engine/`: Machine learning model training and serving (placeholder).
-   `dashboard/`: Next.js admin dashboard.
-   `sandbox/`: Playwright-based URL analysis service.
-   `infrastructure/`: Docker Compose for Postgres, Redis, MinIO.

## Getting Started (Lite Mode - No Docker)

Since you are running without Docker, we will use **SQLite** and local storage.

### Prerequisites

-   Python 3.14+
-   Node.js 18+

### 1. Start Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 2. Start Dashboard

```bash
cd dashboard
npm install
npm run dev
```

The dashboard will be at `http://localhost:3000`.

### 3. Load Extension

1.  Open Chrome and go to `chrome://extensions`.
2.  Enable "Developer mode".
3.  Click "Load unpacked" and select the `extension` folder.

## Testing

Run the simple test script to verify the backend:

```bash
python tests/test_api.py
```
