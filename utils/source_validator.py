# Source Validation and Credibility Checking

import re
from typing import List, Dict, Tuple
from datetime import datetime

class SourceValidator: 
    # Validates sources against the criteria I set

    ALLOWED_DOMAINS = [
        # Academic
        'ieee.org', 'arxiv.org', 'acm.org', 'sae.org',
        #Financial/Market Research
        'jpmorgan.com', 'goldmansachs.com', 'morganstanley.com',
        #Industry
        'ti.com', 'nxp.com', 'infineon.com', 'qualcomm.com', 'nvidia.com', 'intel.com', 'amd.com'
        #OEMS
        'tesla.com', 'gm.com', 'ford.com', 'rivian.com'
    ]

    EXCLUDED_PATTERNS = [
        r'blog\.',
        r'/blog/',
        r'medium\.com',
        r'linkedin\.com/pulse',
        r'twitter\.com',
        r'facebook\.com'
    ]

    def __init__(self):
        self.validation_log = []

    def validate_url(self, url: str) -> Tuple[bool, str]:
        """ Validate a single URL

        Returns:
            (is_valid, reason)
        """
        # Check excluded patterns 
        for pattern in self.EXCLUDED_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return False, f"Matches excluded pattern: {pattern}"
        
        # Check allowed domains
        for domain in self.ALLOWED_DOMAINS:
            if domain in url.lower():
                return True, f"Matches allowed domain: {domain}"

        return False, "Domain not allowed list"

    def validate_citation(self, citation: Dict) -> Dict:
        """
        Validate a citation with required fields.

        Required fields: source, url, date_accessed, claim
        """
        required_fields = ['source', 'url', 'date_accessed', 'claim ']

        validation_result = {
            'valid': True,
            'missing_fields': [],
            'url_valid': True,
            'url_reason':''
        }

        for field in required_fields:
            if field not in citation or not citation[field]:
                validation_result['valid'] = False 
                validation_result['missing_fields'].append(field)
        
        if 'url' in citation: 
            url_valid, url_reason = self.validate_url(citation['url'])
            validation_result['url_valid'] = url_valid
            validation_result['url_reason'] = url_reason

            if not url_valid:
                validation_result['valid'] = False
        
        return validation_result

    def validate_batch(self, citations: List[Dict]) -> Dict:
        """Validate multiple citations and return summary"""

        results = {
            'total': len(citations),
            'valid': 0,
            'invalid': 0,
            'details': []
        }

        for citation in citations: 
            result = self.validate_citation(citation)
            results['details'].append(result)

            if result['valid']:
                results['valid'] += 1
            else: 
                results['invalid'] += 1

        return results

