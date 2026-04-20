"""
PhishShield AI - HTML Content Analyzer

Analyzes the actual HTML content of a webpage to detect phishing indicators
that cannot be found by URL analysis alone.

This module can:
  1. Accept pre-fetched HTML from the browser extension (preferred — faster,
     works on JS-rendered pages, avoids CORS).
  2. Fetch the HTML itself by making an HTTP request to the URL.

Indicators checked:
  - Password field submitted over HTTP
  - Form action pointing to an external/different domain
  - Hidden iframes
  - Excessive <script> tags
  - JavaScript obfuscation (eval, atob, unescape)
  - Right-click / devtools disabling
  - Favicon domain mismatch
  - Meta-refresh redirect
  - Copyright text mentioning a different brand
  - Suspicious hidden input field names
  - <title> contains a brand name that doesn't match the domain
  - Very low text-to-HTML ratio (mostly invisible content)
  - Majority of links pointing to external domains
  - Missing privacy/terms links (common on fake pages)

Author: PhishShield Team
"""

import re
import logging
from typing import Optional
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional imports — gracefully degrade if BeautifulSoup not installed
# ---------------------------------------------------------------------------
try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False
    logger.warning("beautifulsoup4 not installed — HTML analysis disabled. Run: pip install beautifulsoup4 lxml")

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Known major brands whose name in <title> but not in domain is suspicious
KNOWN_BRANDS = [
    "paypal", "amazon", "google", "microsoft", "apple", "facebook", "instagram",
    "netflix", "bank", "chase", "wellsfargo", "citibank", "visa", "mastercard",
    "ebay", "walmart", "fedex", "dhl", "ups", "linkedin", "twitter", "dropbox",
    "spotify", "adobe", "yahoo", "steam", "epic games", "roblox"
]

# Sensitive hidden input field names used by phishing kits to harvest data
SENSITIVE_INPUT_NAMES = ["cc", "cvv", "ssn", "card", "credit", "debit", "pin", "otp", "dob"]

# Legitimate-page boilerplate — phishing pages almost never include these
LEGIT_LINK_KEYWORDS = ["privacy", "terms", "legal", "policy", "about", "contact"]

_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Score weights for each check (each adds this amount to the total html_score)
WEIGHTS = {
    "password_over_http":        0.25,
    "external_form_action":      0.20,
    "hidden_iframe":             0.15,
    "excessive_scripts":         0.10,
    "js_obfuscation":            0.20,
    "rightclick_disabled":       0.10,
    "favicon_mismatch":          0.10,
    "meta_refresh":              0.10,
    "copyright_mismatch":        0.10,
    "sensitive_hidden_inputs":   0.20,
    "title_brand_mismatch":      0.15,
    "low_text_ratio":            0.10,
    "mostly_external_links":     0.10,
    "no_legit_links":            0.10,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_html(url: str, html_content: Optional[str] = None) -> dict:
    """
    Analyze HTML content for phishing indicators.

    Args:
        url:          The URL of the page (used for domain comparison, always required).
        html_content: Raw HTML string. If provided, skips HTTP fetch. If None,
                      the function will attempt to fetch the page itself.

    Returns:
        {
            "html_score":   float   # 0.0 (clean) – 1.0 (very suspicious)
            "html_reasons": List[str]
        }
        On failure or if BS4 is unavailable, returns score 0.0 and an empty list.
    """
    if not _BS4_AVAILABLE:
        return {"html_score": 0.0, "html_reasons": []}

    # --- Obtain HTML ---
    if html_content is None:
        html_content = _fetch_html(url)
        if html_content is None:
            return {"html_score": 0.0, "html_reasons": []}

    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception as exc:
            logger.error("Failed to parse HTML: %s", exc)
            return {"html_score": 0.0, "html_reasons": []}

    parsed_url = urlparse(url)
    page_domain = _base_domain(parsed_url.netloc)
    is_https = parsed_url.scheme.lower() == "https"

    reasons: list[str] = []
    score: float = 0.0

    # Run every check and accumulate
    checks = [
        _check_password_over_http(soup, is_https),
        _check_external_form_action(soup, page_domain, url),
        _check_hidden_iframes(soup),
        _check_excessive_scripts(soup),
        _check_js_obfuscation(soup),
        _check_rightclick_disabled(soup),
        _check_favicon_mismatch(soup, page_domain, url),
        _check_meta_refresh(soup),
        _check_copyright_mismatch(soup, page_domain),
        _check_sensitive_hidden_inputs(soup),
        _check_title_brand_mismatch(soup, page_domain),
        _check_low_text_ratio(soup, html_content),
        _check_mostly_external_links(soup, page_domain),
        _check_no_legit_links(soup),
    ]

    for (flag, reason, weight) in checks:
        if flag:
            score += weight
            reasons.append(reason)

    # Clamp to [0, 1]
    score = round(min(score, 1.0), 4)

    return {"html_score": score, "html_reasons": reasons}


# ---------------------------------------------------------------------------
# Individual checks — each returns (triggered: bool, reason: str, weight: float)
# ---------------------------------------------------------------------------

def _check_password_over_http(soup, is_https: bool):
    """Password input present on non-HTTPS page."""
    if is_https:
        return (False, "", WEIGHTS["password_over_http"])
    pw_inputs = soup.find_all("input", {"type": "password"})
    if pw_inputs:
        return (True, "WARNING: Password field present on non-HTTPS page (credentials at risk)", WEIGHTS["password_over_http"])
    return (False, "", WEIGHTS["password_over_http"])


def _check_external_form_action(soup, page_domain: str, page_url: str):
    """Form action submits to a domain different from the page's domain."""
    for form in soup.find_all("form"):
        action = form.get("action", "")
        if not action or action.startswith("#") or action.startswith("javascript"):
            continue
        # Resolve relative URLs
        full_action = urljoin(page_url, action)
        action_domain = _base_domain(urlparse(full_action).netloc)
        if action_domain and action_domain != page_domain:
            return (True,
                    f"WARNING: Form submits credentials to external domain: {action_domain}",
                    WEIGHTS["external_form_action"])
    return (False, "", WEIGHTS["external_form_action"])


def _check_hidden_iframes(soup):
    """Iframes hidden via style attribute."""
    for iframe in soup.find_all("iframe"):
        style = iframe.get("style", "").replace(" ", "").lower()
        if "display:none" in style or "visibility:hidden" in style:
            return (True, "WARNING: Hidden iframe detected (invisible embedded content)", WEIGHTS["hidden_iframe"])
        # Zero-dimension iframe
        w = iframe.get("width", "1")
        h = iframe.get("height", "1")
        try:
            if int(w) == 0 or int(h) == 0:
                return (True, "WARNING: Zero-dimension iframe detected", WEIGHTS["hidden_iframe"])
        except ValueError:
            pass
    return (False, "", WEIGHTS["hidden_iframe"])


def _check_excessive_scripts(soup):
    """Unusually high number of <script> tags (obfuscation/evasion)."""
    script_count = len(soup.find_all("script"))
    if script_count > 15:
        return (True,
                f"WARNING: Excessive JavaScript tags detected ({script_count} scripts)",
                WEIGHTS["excessive_scripts"])
    return (False, "", WEIGHTS["excessive_scripts"])


def _check_js_obfuscation(soup):
    """Scripts contain common obfuscation functions."""
    OBFUSCATION_PATTERNS = ["eval(", "unescape(", "atob(", "String.fromCharCode(", "document.write(unescape"]
    for script in soup.find_all("script"):
        text = script.get_text() or ""
        for pattern in OBFUSCATION_PATTERNS:
            if pattern in text:
                return (True,
                        f"WARNING: JavaScript obfuscation detected ({pattern.strip('(')})",
                        WEIGHTS["js_obfuscation"])
    return (False, "", WEIGHTS["js_obfuscation"])


def _check_rightclick_disabled(soup):
    """Page disables right-click to prevent inspection."""
    PATTERNS = ["oncontextmenu", "contextmenu", "return false"]
    body = soup.find("body")
    if body and body.get("oncontextmenu"):
        return (True, "WARNING: Right-click disabled (prevents page inspection)", WEIGHTS["rightclick_disabled"])
    for script in soup.find_all("script"):
        text = (script.get_text() or "").lower()
        if "contextmenu" in text and "preventdefault" in text.replace(" ", ""):
            return (True, "WARNING: Right-click disabled via JavaScript", WEIGHTS["rightclick_disabled"])
    return (False, "", WEIGHTS["rightclick_disabled"])


def _check_favicon_mismatch(soup, page_domain: str, page_url: str):
    """Favicon is loaded from a different (possibly legitimate) domain — brand spoofing."""
    link = soup.find("link", rel=lambda r: r and "icon" in r)
    if link:
        href = link.get("href", "")
        if href.startswith("http"):
            favicon_domain = _base_domain(urlparse(href).netloc)
            if favicon_domain and favicon_domain != page_domain:
                return (True,
                        f"WARNING: Favicon loaded from different domain ({favicon_domain}) — possible brand spoofing",
                        WEIGHTS["favicon_mismatch"])
    return (False, "", WEIGHTS["favicon_mismatch"])


def _check_meta_refresh(soup):
    """Page uses <meta http-equiv='refresh'> for automatic redirect."""
    for meta in soup.find_all("meta"):
        equiv = (meta.get("http-equiv") or "").lower()
        if equiv == "refresh":
            content = meta.get("content", "")
            # Redirects with a URL are suspicious (delay=0 especially)
            if "url=" in content.lower():
                return (True,
                        "WARNING: Automatic page redirect via meta-refresh detected",
                        WEIGHTS["meta_refresh"])
    return (False, "", WEIGHTS["meta_refresh"])


def _check_copyright_mismatch(soup, page_domain: str):
    """Copyright footer text mentions a brand not matching the page domain."""
    footer_text = ""
    footer = soup.find("footer")
    if footer:
        footer_text = footer.get_text(separator=" ").lower()
    else:
        # Fall back to full body text (last 500 chars — footers are usually at the bottom)
        body = soup.find("body")
        if body:
            footer_text = body.get_text(separator=" ").lower()[-500:]

    if "©" in footer_text or "copyright" in footer_text:
        for brand in KNOWN_BRANDS:
            if brand in footer_text and brand not in page_domain:
                return (True,
                        f"WARNING: Copyright text mentions '{brand}' but domain is '{page_domain}'",
                        WEIGHTS["copyright_mismatch"])
    return (False, "", WEIGHTS["copyright_mismatch"])


def _check_sensitive_hidden_inputs(soup):
    """Hidden input fields with names that suggest sensitive data collection."""
    for inp in soup.find_all("input", {"type": "hidden"}):
        name = (inp.get("name") or "").lower()
        if any(s in name for s in SENSITIVE_INPUT_NAMES):
            return (True,
                    f"WARNING: Hidden sensitive input field detected (name='{inp.get('name')}')",
                    WEIGHTS["sensitive_hidden_inputs"])
    return (False, "", WEIGHTS["sensitive_hidden_inputs"])


def _check_title_brand_mismatch(soup, page_domain: str):
    """<title> contains a well-known brand but the domain doesn't match."""
    title_tag = soup.find("title")
    if not title_tag:
        return (False, "", WEIGHTS["title_brand_mismatch"])
    title_text = title_tag.string or title_tag.get_text()
    if not title_text:
        return (False, "", WEIGHTS["title_brand_mismatch"])
    title = title_text.lower()
    
    for brand in KNOWN_BRANDS:
        if brand in title and brand not in page_domain:
            return (True,
                    f"WARNING: Page title claims to be '{brand}' but domain is '{page_domain}'",
                    WEIGHTS["title_brand_mismatch"])
    return (False, "", WEIGHTS["title_brand_mismatch"])


def _check_low_text_ratio(soup, raw_html: str):
    """Visible text is very small relative to total HTML size (mostly invisible content)."""
    body = soup.find("body")
    if not body:
        return (False, "", WEIGHTS["low_text_ratio"])
    visible_text = body.get_text(separator=" ")
    text_len = len(visible_text.strip())
    html_len = max(len(raw_html), 1)
    ratio = text_len / html_len
    if ratio < 0.05 and html_len > 500:
        return (True,
                f"WARNING: Very low text-to-HTML ratio ({ratio:.1%}) — page mostly hidden content",
                WEIGHTS["low_text_ratio"])
    return (False, "", WEIGHTS["low_text_ratio"])


def _check_mostly_external_links(soup, page_domain: str):
    """Majority of hyperlinks point to a domain other than the page's domain."""
    links = soup.find_all("a", href=True)
    if len(links) < 5:
        return (False, "", WEIGHTS["mostly_external_links"])

    external = sum(
        1 for a in links
        if _base_domain(urlparse(a["href"]).netloc) not in ("", page_domain)
    )
    ratio = external / len(links)
    if ratio > 0.80:
        return (True,
                f"WARNING: {ratio:.0%} of page links point to external domains (fake page shell)",
                WEIGHTS["mostly_external_links"])
    return (False, "", WEIGHTS["mostly_external_links"])


def _check_no_legit_links(soup):
    """Page has no privacy, terms, or contact links — absent on most phishing pages."""
    all_text = " ".join(
        (a.get_text() + " " + a.get("href", "")).lower()
        for a in soup.find_all("a", href=True)
    )
    for keyword in LEGIT_LINK_KEYWORDS:
        if keyword in all_text:
            return (False, "", WEIGHTS["no_legit_links"])
    return (True,
            "INFO: No privacy, terms, or contact links found (uncommon on legitimate sites)",
            WEIGHTS["no_legit_links"])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fetch_html(url: str) -> Optional[str]:
    """Fetch page HTML. Returns None on any failure."""
    if not _REQUESTS_AVAILABLE:
        return None
    try:
        resp = _requests.get(url, headers=_FETCH_HEADERS, timeout=5, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        logger.warning("HTML fetch failed for %s: %s", url, exc)
        return None


def _base_domain(netloc: str) -> str:
    """Return the registrable domain from a netloc string (strips subdomains)."""
    if not netloc:
        return ""
    # Strip port
    netloc = netloc.split(":")[0].lower()
    parts = netloc.split(".")
    # Return last two labels (e.g. 'paypal.com' from 'secure.paypal.com')
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return netloc
