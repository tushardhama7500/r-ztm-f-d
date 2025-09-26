# tests/test_core/test_stamp.py
import pytest
from datetime import datetime
from app.core.stamp import Stamp

class TestStamp:
    def test_stamp_returns_string(self):
        """Test that Stamp returns a string"""
        result = Stamp()
        assert isinstance(result, str)
    
    def test_stamp_contains_timestamp(self):
        """Test that Stamp contains a timestamp"""
        result = Stamp()
        # Should contain date format YYYY-MM-DD
        assert '-' in result
        assert ':' in result
    
    def test_stamp_contains_event_number(self):
        """Test that Stamp contains event number in brackets"""
        result = Stamp()
        assert '[' in result and ']' in result
    
    def test_stamp_unique_values(self):
        """Test that multiple stamps are different (mostly unique due to random)"""
        stamp1 = Stamp()
        stamp2 = Stamp()
        # They should be different due to random component
        assert stamp1 != stamp2
    
    def test_stamp_format(self):
        """Test that Stamp follows expected format"""
        result = Stamp()
        parts = result.split(' ')
        # Should have at least date, time, and [number]
        assert len(parts) >= 3
        # Check timestamp format
        date_part = ' '.join(parts[0:2])
        try:
            datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')
            format_valid = True
        except ValueError:
            format_valid = False
        assert format_valid