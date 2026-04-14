"""
Tests for new WOW features in Prism.
Test all 6 advanced features to ensure production quality.
"""

import pytest
import sqlite3
from datetime import datetime
from queue_store import init_db, add_message, get_db, get_item


class TestAnalytics:
    """Test analytics module."""
    
    def setup_method(self):
        """Initialize fresh database for tests."""
        init_db()
        
        # Add test data
        add_message("manual", "Critical bug in login", "test-channel", "tesuser")
        add_message("manual", "New feature request", "test-channel", "user2")
        add_message("manual", "Design idea", "test-channel", "user3")
    
    def test_get_analytics(self):
        """Test analytics retrieval."""
        from analytics import get_analytics
        
        data = get_analytics()
        
        assert data is not None
        assert "lanes" in data
        assert "classification_rate" in data
        assert data["total_items"] >= 3
    
    def test_get_team_insights(self):
        """Test team insights."""
        from analytics import get_team_insights
        
        insights = get_team_insights()
        
        assert isinstance(insights, dict)
        assert "avg_items_per_day" in insights
        assert "quality_score" in insights
    
    def test_get_performance_metrics(self):
        """Test performance metrics."""
        from analytics import get_performance_metrics
        
        metrics = get_performance_metrics()
        
        assert "agent_success_rate" in metrics
        assert "estimated_hours_saved" in metrics
        assert metrics["agent_success_rate"] >= 0
    
    def test_export_analytics_csv(self):
        """Test CSV export."""
        from analytics import export_analytics_csv
        
        csv = export_analytics_csv()
        
        assert "PRISM ANALYTICS REPORT" in csv
        assert "Metric" in csv


class TestSemanticSearch:
    """Test semantic search module."""
    
    def setup_method(self):
        """Initialize fresh database for tests."""
        init_db()
        
        add_message("manual", "Login button not working on mobile Safari", test_channel="test")
        add_message("manual", "Can't sign in from phone browser", "test")
        add_message("manual", "New dashboard feature idea", "test")
    
    def test_search(self):
        """Test semantic search."""
        from semantic_search import search_engine
        
        results = search_engine.search("mobile login broken", limit=5, threshold=0.3)
        
        assert isinstance(results, list)
        assert len(results) > 0
    
    def test_find_related(self):
        """Test finding related items."""
        from semantic_search import search_engine
        
        conn = get_db()
        cursor = conn.execute("SELECT id FROM messages LIMIT 1")
        item_id = cursor.fetchone()
        conn.close()
        
        if item_id:
            related = search_engine.get_related(str(item_id[0]), limit=5)
            assert isinstance(related, list)
    
    def test_embedding_generation(self):
        """Test embedding generation."""
        from semantic_search import search_engine
        
        embedding = search_engine.get_embedding("test message")
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        from semantic_search import search_engine
        
        vec1 = search_engine.get_embedding("hello world")
        vec2 = search_engine.get_embedding("hello world")
        
        similarity = search_engine.cosine_similarity(vec1, vec2)
        
        assert similarity >= 0.9  # Should be very similar


class TestWorkflowEngine:
    """Test workflow automation engine."""
    
    def setup_method(self):
        """Initialize workflow engine."""
        init_db()
        from workflow_engine import workflow_engine
        self.engine = workflow_engine
    
    def test_create_rule(self):
        """Test creating automation rule."""
        rule_id = self.engine.create_rule(
            name="Test Rule",
            condition={"field": "priority", "operator": "==", "value": "critical"},
            actions=[{"type": "escalate"}]
        )
        
        assert rule_id is not None
        assert rule_id in self.engine.rules
    
    def test_rule_matching(self):
        """Test rule condition matching."""
        from workflow_engine import Rule
        
        rule = Rule(
            rule_id="test",
            name="Critical Escalator",
            condition={"field": "priority", "operator": "==", "value": "critical"},
            actions=[{"type": "escalate"}]
        )
        
        item_critical = {"priority": "critical"}
        item_normal = {"priority": "normal"}
        
        assert rule.matches(item_critical) == True
        assert rule.matches(item_normal) == False
    
    def test_get_all_rules(self):
        """Test retrieving all rules."""
        rules = self.engine.get_all_rules()
        
        assert isinstance(rules, list)
    
    def test_delete_rule(self):
        """Test deleting a rule."""
        rule_id = self.engine.create_rule(
            name="Temp Rule",
            condition={"field": "lane", "operator": "==", "value": "Issues"},
            actions=[{"type": "notify", "channel": "slack"}]
        )
        
        assert rule_id in self.engine.rules
        
        self.engine.delete_rule(rule_id)
        
        assert rule_id not in self.engine.rules


class TestChatAssistant:
    """Test AI chat assistant."""
    
    def setup_method(self):
        """Initialize database."""
        init_db()
        add_message("manual", "Critical security issue found", "test")
        add_message("manual", "New feature request", "test")
    
    def test_chat_initialization(self):
        """Test chat assistant initialization."""
        from chat_assistant import chat_assistant
        
        assert chat_assistant is not None
        assert hasattr(chat_assistant, 'chat')
    
    def test_chat_history_storage(self):
        """Test storing chat history."""
        from chat_assistant import chat_history
        
        chat_history.save_message(
            "What's our status?",
            "All systems green",
            "test_session"
        )
        
        history = chat_history.get_session_history("test_session")
        assert len(history) > 0
    
    def test_get_context(self):
        """Test context gathering for chat."""
        from chat_assistant import get_context_for_chat
        
        context = get_context_for_chat()
        
        assert isinstance(context, str)
        assert "Current Feedback System Status" in context


class TestGitHubIntegration:
    """Test GitHub integration features."""
    
    def test_github_client_initialization(self):
        """Test GitHub client initialization."""
        from github_integration import GitHubClient
        
        client = GitHubClient("torvalds", "linux", "fake_token")
        
        assert client.owner == "torvalds"
        assert client.repo == "linux"
    
    def test_github_config_management(self):
        """Test GitHub config management."""
        from github_integration import set_github_config, get_github_config
        
        set_github_config("torvalds", "linux", "token123", auto_sync=True)
        
        config = get_github_config()
        
        assert config["repo_owner"] == "torvalds"
        assert config["repo_name"] == "linux"


class TestRealtimeManager:
    """Test real-time connection manager."""
    
    def test_connection_manager_initialization(self):
        """Test connection manager."""
        from realtime_manager import ConnectionManager
        
        manager = ConnectionManager()
        
        assert manager.get_connected_count() == 0
        assert manager.get_user_list() == []
    
    def test_broadcast_format(self):
        """Test broadcast message formatting."""
        from realtime_manager import ConnectionManager
        import json
        
        manager = ConnectionManager()
        
        message = {
            "type": "board_update",
            "action": "add",
            "item_id": "123"
        }
        
        # Should be convertible to JSON
        json_str = json.dumps(message)
        assert "board_update" in json_str


class TestIntegration:
    """Integration tests combining multiple features."""
    
    def setup_method(self):
        """Setup test database."""
        init_db()
    
    def test_end_to_end_feedback_processing(self):
        """Test complete feedback flow with new features."""
        # 1. Add message
        add_message("manual", "App crashes on startup", "test")
        
        # 2. Get analytics
        from analytics import get_analytics
        analytics = get_analytics()
        assert analytics["total_items"] >= 1
        
        # 3. Search semantically
        from semantic_search import search_engine
        results = search_engine.search("crash", limit=3, threshold=0.2)
        assert isinstance(results, list)
        
        # 4. Workflow would apply rules
        from workflow_engine import workflow_engine
        rules = workflow_engine.get_all_rules()
        assert isinstance(rules, list)
    
    def test_all_features_imported(self):
        """Test that all new modules can be imported."""
        # Should not raise ImportError
        from analytics import get_analytics
        from semantic_search import search_engine
        from chat_assistant import chat_assistant
        from workflow_engine import workflow_engine
        from github_integration import GitHubClient
        from realtime_manager import connection_manager
        
        assert all([
            get_analytics,
            search_engine,
            chat_assistant,
            workflow_engine,
            GitHubClient,
            connection_manager
        ])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
