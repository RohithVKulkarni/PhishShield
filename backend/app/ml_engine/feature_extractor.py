import re
from urllib.parse import urlparse, parse_qs
import ipaddress
import math
from collections import Counter

class FeatureExtractor:
    def __init__(self, url):
        self.url = url
        self.parsed = urlparse(url)
        self.domain = self.parsed.netloc
        self.path = self.parsed.path
        self.query = self.parsed.query
        
    def extract_features(self):
        """Extract comprehensive feature set for phishing detection"""
        features = {}
        
        # Basic length features
        features.update(self._extract_length_features())
        
        # Statistical features
        features.update(self._extract_statistical_features())
        
        # Structural features
        features.update(self._extract_structural_features())
        
        # Character distribution features
        features.update(self._extract_character_features())
        
        # Pattern detection features
        features.update(self._extract_pattern_features())
        
        # Lexical features
        features.update(self._extract_lexical_features())
        
        # Security features
        features.update(self._extract_security_features())
        
        return features
    
    def _extract_length_features(self):
        """Length-based features with normalization"""
        return {
            "url_length": len(self.url),
            "domain_length": len(self.domain),
            "path_length": len(self.path),
            "query_length": len(self.query),
            # Normalized ratios
            "domain_url_ratio": len(self.domain) / max(len(self.url), 1),
            "path_url_ratio": len(self.path) / max(len(self.url), 1),
        }
    
    def _extract_statistical_features(self):
        """Statistical features: entropy, randomness"""
        return {
            "url_entropy": self._calculate_entropy(self.url),
            "domain_entropy": self._calculate_entropy(self.domain),
            "path_entropy": self._calculate_entropy(self.path),
        }
    
    def _extract_structural_features(self):
        """URL structure features"""
        subdomain_count = len(self.domain.split('.')) - 2 if len(self.domain.split('.')) > 2 else 0
        path_depth = len([p for p in self.path.split('/') if p])
        
        # Parse query parameters
        query_params = parse_qs(self.query)
        
        return {
            "subdomain_count": subdomain_count,
            "dot_count": self.domain.count("."),
            "dash_count": self.domain.count("-"),
            "underscore_count": self.domain.count("_"),
            "path_depth": path_depth,
            "query_param_count": len(query_params),
            "fragment_length": len(self.parsed.fragment),
        }
    
    def _extract_character_features(self):
        """Character distribution and ratio features"""
        url_lower = self.url.lower()
        domain_lower = self.domain.lower()
        
        # Count character types
        digit_count = sum(c.isdigit() for c in self.url)
        letter_count = sum(c.isalpha() for c in self.url)
        special_count = sum(not c.isalnum() for c in self.url)
        
        return {
            "digit_ratio": digit_count / max(len(self.url), 1),
            "letter_ratio": letter_count / max(len(self.url), 1),
            "special_char_ratio": special_count / max(len(self.url), 1),
            "uppercase_ratio": sum(c.isupper() for c in self.url) / max(len(self.url), 1),
            "digit_in_domain": sum(c.isdigit() for c in self.domain) / max(len(self.domain), 1),
        }
    
    def _extract_pattern_features(self):
        """Advanced pattern detection"""
        return {
            "is_ip": self._is_ip_address(),
            "has_at_symbol": int("@" in self.url),
            "double_slash_redirect": int(self.url.rfind("//") > 7),
            "suspicious_tld": self._is_suspicious_tld(),
            "typosquatting": self._check_typosquatting(),
            "homograph_attack": self._detect_homograph(),
            "url_shortening": self._is_url_shortener(),
            "has_port": int(bool(self.parsed.port)),
        }
    
    def _extract_lexical_features(self):
        """Lexical analysis features"""
        url_lower = self.url.lower()
        
        # Vowel/consonant ratio
        vowels = sum(url_lower.count(v) for v in 'aeiou')
        consonants = sum(url_lower.count(c) for c in 'bcdfghjklmnpqrstvwxyz')
        
        return {
            "suspicious_keywords": self._has_suspicious_keywords(),
            "brand_keywords": self._has_brand_keywords(),
            "vowel_ratio": vowels / max(len(url_lower), 1),
            "consonant_ratio": consonants / max(len(url_lower), 1),
        }
    
    def _extract_security_features(self):
        """Security-related features"""
        return {
            "https_token": int("https" in self.domain.lower()),
            "http_in_path": int("http" in self.path.lower()),
            "is_https": int(self.parsed.scheme == "https"),
            "url_encoded_chars": self._count_encoded_chars(),
        }
    
    # Helper methods
    
    def _calculate_entropy(self, text):
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        counter = Counter(text)
        length = len(text)
        entropy = 0.0
        
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _is_ip_address(self):
        """Check if domain is an IP address"""
        try:
            # Remove port if present
            domain = self.domain.split(':')[0]
            ipaddress.ip_address(domain)
            return 1
        except:
            return 0
    
    def _is_suspicious_tld(self):
        """Check for suspicious top-level domains"""
        suspicious_tlds = [
            '.xyz', '.top', '.club', '.win', '.gq', '.cn', '.tk', '.ml',
            '.ga', '.cf', '.buzz', '.link', '.download', '.stream', '.science',
            '.racing', '.party', '.review', '.trade', '.webcam', '.date'
        ]
        return int(any(self.domain.lower().endswith(tld) for tld in suspicious_tlds))
    
    def _check_typosquatting(self):
        """Enhanced typosquatting detection with expanded brand list"""
        targets = [
            'google', 'facebook', 'amazon', 'apple', 'microsoft', 'netflix', 
            'paypal', 'dropbox', 'twitter', 'instagram', 'linkedin', 'github',
            'yahoo', 'ebay', 'walmart', 'chase', 'bankofamerica', 'wellsfargo',
            'citibank', 'americanexpress', 'discover', 'adobe', 'spotify',
            'reddit', 'youtube', 'whatsapp', 'telegram', 'signal'
        ]
        
        domain_parts = self.domain.lower().split('.')
        main_domain = domain_parts[-2] if len(domain_parts) > 1 else domain_parts[0]
        
        for target in targets:
            if target == main_domain:
                return 0  # Exact match is safe
            
            # Check for typos (1-2 character difference)
            if len(main_domain) > 3 and self._levenshtein(target, main_domain) <= 2:
                return 1
            
            # Check for character substitution (e.g., 'paypa1' for 'paypal')
            if target in main_domain or main_domain in target:
                if len(main_domain) >= len(target) - 2:
                    return 1
        
        return 0
    
    def _detect_homograph(self):
        """Detect homograph/IDN attacks (lookalike characters)"""
        # Common homograph patterns
        suspicious_patterns = [
            ('rn', 'm'),  # 'rn' looks like 'm'
            ('vv', 'w'),  # 'vv' looks like 'w'
            ('l', '1'),   # lowercase L vs number 1
            ('o', '0'),   # letter O vs zero
        ]
        
        domain_lower = self.domain.lower()
        
        for pattern, lookalike in suspicious_patterns:
            if pattern in domain_lower:
                return 1
        
        # Check for non-ASCII characters (punycode)
        if 'xn--' in domain_lower:
            return 1
        
        return 0
    
    def _is_url_shortener(self):
        """Check if URL is from a known shortening service"""
        shorteners = [
            'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly', 'is.gd',
            'buff.ly', 'adf.ly', 'bit.do', 'short.link', 'tiny.cc'
        ]
        return int(any(shortener in self.domain.lower() for shortener in shorteners))
    
    def _has_suspicious_keywords(self):
        """Enhanced suspicious keyword detection"""
        keywords = [
            'login', 'verify', 'update', 'account', 'secure', 'banking', 
            'confirm', 'suspend', 'locked', 'unusual', 'click', 'urgent',
            'password', 'credential', 'signin', 'validate', 'restore',
            'limited', 'expire', 'immediately', 'action', 'required'
        ]
        url_lower = self.url.lower()
        return int(any(keyword in url_lower for keyword in keywords))
    
    def _has_brand_keywords(self):
        """Check for brand names in URL (potential impersonation)"""
        brands = [
            'paypal', 'amazon', 'google', 'microsoft', 'apple', 'facebook',
            'netflix', 'bank', 'chase', 'wellsfargo', 'citi', 'visa',
            'mastercard', 'ebay', 'walmart', 'fedex', 'ups', 'dhl'
        ]
        url_lower = self.url.lower()
        
        # Check if brand name appears but not in the main domain
        domain_parts = self.domain.lower().split('.')
        main_domain = domain_parts[-2] if len(domain_parts) > 1 else domain_parts[0]
        
        for brand in brands:
            if brand in url_lower and brand != main_domain:
                # Brand appears in path/query but not as main domain - suspicious
                if brand not in main_domain:
                    return 1
        
        return 0
    
    def _count_encoded_chars(self):
        """Count URL-encoded characters (e.g., %20, %3D)"""
        return self.url.count('%')
    
    def _levenshtein(self, s1, s2):
        """Calculate Levenshtein distance between two strings"""
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
