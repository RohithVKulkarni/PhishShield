import re
from urllib.parse import urlparse
import ipaddress

class FeatureExtractor:
    def __init__(self, url):
        self.url = url
        self.parsed = urlparse(url)
        self.domain = self.parsed.netloc

    def extract_features(self):
        features = {
            "url_length": len(self.url),
            "domain_length": len(self.domain),
            "is_ip": self._is_ip_address(),
            "has_at_symbol": "@" in self.url,
            "double_slash_redirect": self.url.rfind("//") > 7,
            "dash_count": self.domain.count("-"),
            "dot_count": self.domain.count("."),
            "https_token": "https" in self.domain,
            "suspicious_tld": self._is_suspicious_tld(),
            "suspicious_keywords": self._has_suspicious_keywords(),
            "typosquatting": self._check_typosquatting()
        }
        return features

    def _check_typosquatting(self):
        targets = ['google', 'facebook', 'amazon', 'apple', 'microsoft', 'netflix', 'paypal', 'dropbox', 'twitter', 'instagram', 'linkedin', 'github']
        domain_parts = self.domain.split('.')
        main_domain = domain_parts[-2] if len(domain_parts) > 1 else domain_parts[0]
        
        # Simple check: if it's not in targets but looks like one
        for target in targets:
            if target == main_domain:
                return 0 # Exact match is safe (e.g. google.com)
            
            # Check for simple typos (1-2 char difference)
            if self._levenshtein(target, main_domain) <= 2:
                return 1
        return 0

    def _levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def _is_ip_address(self):
        try:
            ipaddress.ip_address(self.domain)
            return 1
        except:
            return 0

    def _is_suspicious_tld(self):
        suspicious_tlds = ['.xyz', '.top', '.club', '.win', '.gq', '.cn']
        return 1 if any(self.domain.endswith(tld) for tld in suspicious_tlds) else 0

    def _has_suspicious_keywords(self):
        keywords = ['login', 'verify', 'update', 'account', 'secure', 'banking', 'confirm']
        return 1 if any(keyword in self.url.lower() for keyword in keywords) else 0
