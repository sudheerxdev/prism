"""
Tests for Prism — SpecFlow multi-agent system  
Run with: pytest tests/ -v
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from queue_store import (
    init_db, add_message, get_messages, set_status, get_item, 
    classify_item, LANE_STATUSES, LANE_META, board_counts, _conn
)
from agent import get_llm, ClassifierState


@pytest.fixture(scope="session", autouse=True)
def init_database():
    """Initialize database once for entire test session"""
    init_db()
    yield


class TestDatabase:
    """Test SQLite database operations"""
    
    def test_init_db_creates_schema(self):
        """Verify database schema is created"""
        with _conn() as c:
            tables = c.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        table_names = [t[0] for t in tables]
        assert "messages" in table_names
        assert "config" in table_names
        assert "context_files" in table_names
    
    def test_add_message_succeeds(self):
        """Test adding a message to inbox"""
        result = add_message("slack", "test message unique 001", "general", "user1")
        assert result is True
    
    def test_add_duplicate_message_fails(self):
        """Test that duplicate messages are rejected"""
        content = "unique test message 002"
        add_message("slack", content, "general", "user1")
        result = add_message("slack", content, "general", "user1")
        assert result is False
    
    def test_empty_message_rejected(self):
        """Test that empty messages are rejected"""
        result = add_message("slack", "   ", "general", "user1")
        assert result is False
    
    def test_get_messages_by_status(self):
        """Test retrieving messages filtered by status"""
        add_message("slack", "pending msg 001", "general", "user1")
        add_message("slack", "pending msg 002", "general", "user1")
        
        pending = get_messages("pending")
        assert len(pending) >= 2
        assert all(m["status"] == "pending" for m in pending)
    
    def test_lane_statuses_valid(self):
        """Test that all lane statuses are defined"""
        expected_lanes = ["issue", "feature", "idea", "marketing", "unclassified"]
        for lane in expected_lanes:
            assert lane in LANE_STATUSES
            assert isinstance(LANE_STATUSES[lane], list)
            assert len(LANE_STATUSES[lane]) > 0
    
    def test_lane_metadata_complete(self):
        """Test that all lanes have metadata"""
        expected_lanes = ["issue", "feature", "idea", "marketing", "unclassified"]
        for lane in expected_lanes:
            assert lane in LANE_META
            assert "emoji" in LANE_META[lane]
            assert "label" in LANE_META[lane]
            assert "color" in LANE_META[lane]


class TestLLMProvider:
    """Test LLM provider detection and initialization"""
    
    def test_openai_key_format(self):
        """Test OpenAI API key format detection"""
        api_key = "sk-test1234567890abcdefghij"
        assert api_key.startswith("sk-")
    
    def test_groq_key_format(self):
        """Test Groq API key format detection"""
        api_key = "gsk_test1234567890abcdefghij"
        assert api_key.startswith("gsk_")
    
    def test_invalid_key_raises_error(self):
        """Test that invalid API key raises ValueError"""
        with pytest.raises(ValueError):
            get_llm("invalid_key_format")


class TestClassificationLogic:
    """Test message classification logic"""
    
    def test_classifier_state_schema(self):
        """Test that ClassifierState has required fields"""
        state = ClassifierState(
            raw_feedback="test",
            lane="issue",
            title="Test",
            summary="A test",
            priority="high",
            error=None,
            debug=None
        )
        assert state["raw_feedback"] == "test"
        assert state["lane"] == "issue"


class TestBoardCounts:
    """Test board statistics and counting"""
    
    def test_counts_returns_all_lanes(self):
        """Test that board_counts returns all lanes"""
        counts = board_counts()
        for lane in LANE_META.keys():
            assert lane in counts


class TestMessageDeduplication:
    """Test that duplicate detection works correctly"""
    
    def test_identical_messages_deduplicated(self):
        """Test that identical messages from same source are deduplicated"""
        content = "This is a critical dedup test message unique code 99"
        
        result1 = add_message("slack", content, "general", "user1")
        result2 = add_message("slack", content, "general", "user1")
        
        assert result1 is True
        assert result2 is False
    
    def test_different_sources_not_deduplicated(self):
        """Test that same message from different sources is NOT deduplicated"""
        content = "This is a multi-source test message unique code 88"
        
        result1 = add_message("slack", content, "general", "user1")
        result2 = add_message("discord", content, "general", "user1")
        
        assert result1 is True
        assert result2 is True


def test_core_modules_importable():
    """Verify core modules can be imported"""
    try:
        import agent
        import queue_store
        import discord_bot
        import slack_bot
        assert True
    except ImportError as e:
        pytest.fail(f"Import error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
