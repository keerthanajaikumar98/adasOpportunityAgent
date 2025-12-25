"""Source validation rules engine."""

import json
from typing import Dict, List, Tuple
from pathlib import Path

class SourceRules:
    """Enforces source quality and validation rules."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / 'allowed_sources.json'
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def is_allowed_domain(self, url: str) -> Tuple[bool, str, str]:
        """
        Check if URL is from an allowed domain.
        
        Returns:
            (is_allowed, category, specific_source)
        """
        url_lower = url.lower()
        
        # Check academic sources
        for source_name, source_info in self.config['academic'].items():
            for domain in source_info['domains']:
                if domain in url_lower:
                    return True, 'academic', source_name
        
        # Check financial research
        for source_name, source_info in self.config['financial_research'].items():
            for domain in source_info['domains']:
                if domain in url_lower:
                    return True, 'financial_research', source_name
        
        # Check semiconductor vendors
        for vendor, domains in self.config['industry']['semiconductor_vendors'].items():
            for domain in domains:
                if domain in url_lower:
                    return True, 'semiconductor_vendor', vendor
        
        # Check OEMs
        for oem, domains in self.config['industry']['oems'].items():
            for domain in domains:
                if domain in url_lower:
                    return True, 'oem', oem
        
        # Check Tier-1 suppliers
        for tier1, domains in self.config['industry']['tier1'].items():
            for domain in domains:
                if domain in url_lower:
                    return True, 'tier1', tier1
        
        return False, '', ''
    
    def is_excluded(self, url: str) -> Tuple[bool, str]:
        """
        Check if URL matches excluded patterns.
        
        Returns:
            (is_excluded, matched_pattern)
        """
        url_lower = url.lower()
        
        for pattern in self.config['excluded_patterns']:
            if pattern in url_lower:
                return True, pattern
        
        return False, ''
    
    def validate_citation(self, citation: Dict) -> Dict:
        """
        Validate a complete citation.
        
        Returns validation result with details.
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'source_category': '',
            'source_name': '',
            'credibility': ''
        }
        
        # Check URL presence
        if 'url' not in citation or not citation['url']:
            result['valid'] = False
            result['errors'].append("Missing URL")
            return result
        
        # Check if excluded
        is_excl, pattern = self.is_excluded(citation['url'])
        if is_excl:
            result['valid'] = False
            result['errors'].append(f"Excluded pattern: {pattern}")
            return result
        
        # Check if allowed
        is_allowed, category, source = self.is_allowed_domain(citation['url'])
        if not is_allowed:
            result['valid'] = False
            result['errors'].append("Domain not in allowed list")
            return result
        
        result['source_category'] = category
        result['source_name'] = source
        
        # Get credibility if available
        if category == 'academic':
            result['credibility'] = self.config['academic'][source]['credibility']
        elif category == 'financial_research':
            result['credibility'] = self.config['financial_research'][source]['credibility']
        else:
            result['credibility'] = 'medium'
        
        # Check other required fields
        required_fields = ['claim', 'date_accessed']
        for field in required_fields:
            if field not in citation or not citation[field]:
                result['warnings'].append(f"Missing recommended field: {field}")
        
        return result