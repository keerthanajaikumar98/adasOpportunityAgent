"""Test suite for ADAS Opportunity Mapping Agent."""

import pytest
import asyncio
from utils.api_client import AnthropicClient
from utils.source_validator import SourceValidator
from sources.source_rules import SourceRules

class TestSourceValidation:
    """Test source validation functionality."""
    
    def test_allowed_domain(self):
        rules = SourceRules()
        
        # Test IEEE (should be allowed)
        is_allowed, category, source = rules.is_allowed_domain('https://ieeexplore.ieee.org/document/123')
        assert is_allowed == True
        assert category == 'academic'
        assert source == 'ieee'
        
        # Test excluded domain (should be rejected)
        is_allowed, _, _ = rules.is_allowed_domain('https://medium.com/some-blog')
        assert is_allowed == False
    
    def test_excluded_patterns(self):
        rules = SourceRules()
        
        # Test blog exclusion
        is_excluded, pattern = rules.is_excluded('https://example.com/blog/post')
        assert is_excluded == True
        
        # Test valid URL
        is_excluded, _ = rules.is_excluded('https://ieee.org/paper')
        assert is_excluded == False
    
    def test_citation_validation(self):
        rules = SourceRules()
        
        valid_citation = {
            'url': 'https://ieee.org/paper/123',
            'claim': 'ADAS market growing at 15% CAGR',
            'date_accessed': '2025-01-15'
        }
        
        result = rules.validate_citation(valid_citation)
        assert result['valid'] == True
        assert result['source_category'] == 'academic'

class TestSourceValidator:
    """Test SourceValidator class."""
    
    def test_url_validation(self):
        validator = SourceValidator()
        
        # Test allowed URL
        is_valid, reason = validator.validate_url('https://ieee.org/paper')
        assert is_valid == True
        
        # Test excluded URL
        is_valid, reason = validator.validate_url('https://medium.com/blog')
        assert is_valid == False

# Run tests with: pytest tests/test_agents.py -v