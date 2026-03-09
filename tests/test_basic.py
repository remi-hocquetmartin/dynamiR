"""
Basic integration tests for DynamiR
Run with: python -m pytest tests/
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestImports:
    """Test that all modules can be imported successfully."""
    
    def test_import_backend(self):
        """Test backend module imports."""
        from backend.stub_backend import (
            backend_match_micro_to_mrna,
            backend_dynamite_on_mrna,
        )
        assert callable(backend_match_micro_to_mrna)
        assert callable(backend_dynamite_on_mrna)
    
    def test_import_ui(self):
        """Test UI module imports."""
        from ui.matching_tab import MatchingTab
        from ui.dynamite_tab import DynamiteTab
        assert MatchingTab is not None
        assert DynamiteTab is not None
    
    def test_import_utils(self):
        """Test utils module imports."""
        from utils.file_readers import read_sequence_from_file
        from utils.parsers import parse_range_text
        assert callable(read_sequence_from_file)
        assert callable(parse_range_text)
    
    def test_import_config(self):
        """Test config module imports."""
        import config
        assert hasattr(config, 'APP_NAME')
        assert hasattr(config, 'COLORS')
        assert hasattr(config, 'WATSON_CRICK_PAIRS')


class TestParsers:
    """Test parsing utilities."""
    
    def test_parse_range_text_valid(self):
        """Test parsing valid range strings."""
        from utils.parsers import parse_range_text
        start, end = parse_range_text("2-7")
        assert start == 2
        assert end == 7
    
    def test_parse_range_text_invalid(self):
        """Test parsing invalid range strings."""
        from utils.parsers import parse_range_text
        with pytest.raises(ValueError):
            parse_range_text("invalid")


class TestSequenceProcessing:
    """Test sequence processing functions."""
    
    def test_base_pairing_watson_crick(self):
        """Test Watson-Crick base pair detection."""
        import config
        pairs = config.WATSON_CRICK_PAIRS
        
        assert ("A", "U") in pairs
        assert ("U", "A") in pairs
        assert ("C", "G") in pairs
        assert ("G", "C") in pairs
    
    def test_base_pairing_wobble(self):
        """Test wobble pair detection."""
        import config
        pairs = config.WOBBLE_PAIRS
        
        assert ("G", "U") in pairs
        assert ("U", "G") in pairs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
