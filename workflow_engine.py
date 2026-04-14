"""
Automated workflow rules engine for Prism.
Create IFTTT-style rules: IF [condition] THEN [action]
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
from queue_store import _conn


class Rule:
    """A single automation rule."""
    
    def __init__(self, rule_id: str, name: str, condition: Dict, actions: List[Dict], enabled: bool = True):
        self.rule_id = rule_id
        self.name = name
        self.condition = condition  # {'field': 'priority', 'operator': '==', 'value': 'critical'}
        self.actions = actions     # [{'type': 'escalate'}, {'type': 'notify', 'channel': 'slack'}]
        self.enabled = enabled
        self.created_at = datetime.now().isoformat()
    
    def matches(self, item: Dict) -> bool:
        """Check if item matches this rule's condition."""
        field = self.condition.get("field")
        operator = self.condition.get("operator")
        value = self.condition.get("value")
        
        item_value = item.get(field)
        
        if operator == "==":
            return item_value == value
        elif operator == "!=":
            return item_value != value
        elif operator == ">":
            return item_value > value
        elif operator == "<":
            return item_value < value
        elif operator == "contains":
            return value in str(item_value)
        elif operator == "in":
            return item_value in value
        
        return False
    
    def to_dict(self) -> Dict:
        """Convert rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "condition": self.condition,
            "actions": self.actions,
            "enabled": self.enabled,
            "created_at": self.created_at
        }


class WorkflowEngine:
    """Manage and execute automation rules."""
    
    def __init__(self):
        """Initialize the workflow engine."""
        self.rules: Dict[str, Rule] = {}
        self.action_handlers: Dict[str, Callable] = {
            "escalate": self._action_escalate,
            "notify": self._action_notify,
            "auto_assign": self._action_auto_assign,
            "add_label": self._action_add_label,
            "move_lane": self._action_move_lane,
            "close": self._action_close,
            "create_task": self._action_create_task,
        }
        self.load_rules()
    
    def load_rules(self):
        """Load rules from database."""
        conn = _conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                condition TEXT NOT NULL,
                actions TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor = conn.execute("SELECT rule_id, name, condition, actions, enabled, created_at FROM workflow_rules WHERE enabled = 1")
        
        for row in cursor.fetchall():
            rule_id, name, condition_json, actions_json, enabled, created_at = row
            rule = Rule(
                rule_id=rule_id,
                name=name,
                condition=json.loads(condition_json),
                actions=json.loads(actions_json),
                enabled=bool(enabled)
            )
            self.rules[rule_id] = rule
        
        conn.close()
    
    def create_rule(self, name: str, condition: Dict, actions: List[Dict]) -> str:
        """Create a new automation rule."""
        import uuid
        rule_id = str(uuid.uuid4())
        
        rule = Rule(rule_id, name, condition, actions, enabled=True)
        self.rules[rule_id] = rule
        
        # Save to database
        conn = _conn()
        conn.execute("""
            INSERT INTO workflow_rules (rule_id, name, condition, actions, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rule_id,
            name,
            json.dumps(condition),
            json.dumps(actions),
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        return rule_id
    
    def delete_rule(self, rule_id: str):
        """Delete a rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
        
        conn = _conn()
        conn.execute("DELETE FROM workflow_rules WHERE rule_id = ?", (rule_id,))
        conn.commit()
        conn.close()
    
    def get_all_rules(self) -> List[Dict]:
        """Get all active rules."""
        return [rule.to_dict() for rule in self.rules.values()]
    
    def apply_rules(self, item_id: str, item_data: Dict) -> List[str]:
        """Apply matching rules to an item and execute actions."""
        matched_rules = []
        executed_actions = []
        
        for rule_id, rule in self.rules.items():
            if rule.enabled and rule.matches(item_data):
                matched_rules.append(rule_id)
                
                # Execute all actions for this rule
                for action in rule.actions:
                    action_type = action.get("type")
                    if action_type in self.action_handlers:
                        try:
                            self.action_handlers[action_type](item_id, action)
                            executed_actions.append(f"{rule.name}:{action_type}")
                        except Exception as e:
                            print(f"✗ Error executing {action_type}: {e}")
        
        return executed_actions
    
    # Action handlers
    
    def _action_escalate(self, item_id: str, action: Dict):
        """Escalate item to critical priority."""
        conn = _conn()
        conn.execute(
            "UPDATE messages SET priority = 'critical', updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), item_id)
        )
        conn.commit()
        conn.close()
    
    def _action_notify(self, item_id: str, action: Dict):
        """Send notification to a channel."""
        channel = action.get("channel", "slack")  # slack, discord, email
        print(f"→ Notify: {channel} about item {item_id}")
    
    def _action_auto_assign(self, item_id: str, action: Dict):
        """Auto-assign to a team member."""
        assignee = action.get("assignee")
        conn = _conn()
        conn.execute(
            "UPDATE messages SET assigned_to = ?, updated_at = ? WHERE id = ?",
            (assignee, datetime.now().isoformat(), item_id)
        )
        conn.commit()
        conn.close()
    
    def _action_add_label(self, item_id: str, action: Dict):
        """Add label/tag to item."""
        label = action.get("label")
        # In a real system, this would update a labels table
        print(f"→ Add label '{label}' to item {item_id}")
    
    def _action_move_lane(self, item_id: str, action: Dict):
        """Move item to a different lane."""
        lane = action.get("lane")  # Issues, Features, Ideas, Marketing
        conn = _conn()
        conn.execute(
            "UPDATE messages SET lane = ?, updated_at = ? WHERE id = ?",
            (lane, datetime.now().isoformat(), item_id)
        )
        conn.commit()
        conn.close()
    
    def _action_close(self, item_id: str, action: Dict):
        """Automatically close/archive item."""
        conn = _conn()
        conn.execute(
            "UPDATE messages SET status = 'closed', updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), item_id)
        )
        conn.commit()
        conn.close()
    
    def _action_create_task(self, item_id: str, action: Dict):
        """Create a followup task."""
        task_title = action.get("title", "Follow-up task")
        # In a real system, create a subtask or linked item
        print(f"→ Create task '{task_title}' for item {item_id}")


# Example rules for common scenarios
def create_default_rules(engine: WorkflowEngine):
    """Create default automation rules."""
    
    # Rule 1: Auto-escalate security issues
    engine.create_rule(
        name="Auto-escalate security issues",
        condition={"field": "content", "operator": "contains", "value": "security"},
        actions=[
            {"type": "escalate"},
            {"type": "notify", "channel": "slack"}
        ]
    )
    
    # Rule 2: Move bugs to issues lane
    engine.create_rule(
        name="Bug → Issues lane",
        condition={"field": "title", "operator": "contains", "value": "bug"},
        actions=[{"type": "move_lane", "lane": "Issues"}]
    )
    
    # Rule 3: Close old archived items
    engine.create_rule(
        name="Auto-archive old ideas",
        condition={"field": "lane", "operator": "==", "value": "Ideas"},
        actions=[{"type": "close"}]
    )


# Global workflow engine
workflow_engine = WorkflowEngine()
