"""
AI Chat Assistant for Prism - conversational interface to ask questions about feedback.
"Hey bot, what's our top priority issue?" → Returns answer with context.
"""

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import json
from queue_store import _conn
from datetime import datetime


CHAT_SYSTEM_PROMPT = """You are Prism, an AI assistant for the Prism feedback intelligence system.
You help teams understand and manage their feedback.

You have access to the following information about the feedback system:
{context}

Answer user questions about feedback, provide insights, suggest actions, and help with decision-making.
Be friendly, concise, and data-driven. If you don't have information to answer, say so honestly.

When suggesting actions, explain the reasoning. When giving statistics, cite the data.
"""


def get_context_for_chat() -> str:
    """Get current system state for chat context."""
    conn = _conn()
    cursor = conn.cursor()
    
    # Get summary stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN lane = 'Issues' THEN 1 ELSE 0 END) as issues,
            SUM(CASE WHEN lane = 'Features' THEN 1 ELSE 0 END) as features,
            SUM(CASE WHEN lane = 'Ideas' THEN 1 ELSE 0 END) as ideas,
            SUM(CASE WHEN lane = 'Marketing' THEN 1 ELSE 0 END) as marketing,
            SUM(CASE WHEN priority = 'critical' THEN 1 ELSE 0 END) as critical,
            SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority,
            SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
        FROM messages
        WHERE status != 'deleted'
    """)
    
    row = cursor.fetchone()
    if row:
        total, issues, features, ideas, marketing, critical, high_priority, closed = row
        context = f"""
Current Feedback System Status:
- Total items: {total}
- Issues: {issues}
- Features: {features}
- Ideas: {ideas}
- Marketing: {marketing}
- Critical priority: {critical}
- High priority: {high_priority}
- Closed/resolved: {closed}
"""
    else:
        context = "No feedback data yet."
    
    # Get recent items
    cursor.execute("""
        SELECT title, lane, priority, created_at
        FROM messages
        WHERE status != 'deleted'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    if recent:
        context += "\n\nRecent Items:\n"
        for title, lane, priority, created_at in recent:
            context += f"- [{priority.upper()}] {title} ({lane})\n"
    
    conn.close()
    return context


class ChatAssistant:
    """AI chat assistant for Prism."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """Initialize chat assistant."""
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.conversation_history = []
        self.context_last_updated = None
    
    def chat(self, user_message: str) -> str:
        """
        Have a conversation with the assistant.
        
        Example queries:
        - "What's our most critical issue?"
        - "How many features are pending?"
        - "Should I prioritize bugs or features?"
        - "What's the status of our inbox?"
        """
        
        # Add user message to history
        self.conversation_history.append(HumanMessage(content=user_message))
        
        # Get current context
        context = get_context_for_chat()
        
        # Create prompt with simple formatting
        formatted_prompt = CHAT_SYSTEM_PROMPT.format(context=context)
        
        # Build messages for LLM
        messages = [
            HumanMessage(content=formatted_prompt),
            *self.conversation_history
        ]
        
        # Get response from LLM
        try:
            response = self.llm.invoke(messages)
            assistant_message = response.content
            
            # Add to history
            self.conversation_history.append(AIMessage(content=assistant_message))
            
            # Keep history manageable (last 10 messages)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return assistant_message
        
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def ask_quick_question(self, query: str) -> str:
        """
        Ask a quick question without maintaining conversation history.
        Useful for one-off queries.
        """
        context = get_context_for_chat()
        
        formatted = (CHAT_SYSTEM_PROMPT + "\n\nUser question: {question}").format(
            context=context, question=query
        )
        
        try:
            response = self.llm.invoke([HumanMessage(content=formatted)])
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"


class ChatHistory:
    """Store and retrieve chat messages from database."""
    
    def __init__(self):
        """Initialize chat history storage."""
        self._init_table()
    
    def _init_table(self):
        """Create chat history table if it doesn't exist."""
        conn = _conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id TEXT PRIMARY KEY,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def save_message(self, user_msg: str, assistant_msg: str, session_id: str = "default"):
        """Save a chat exchange to history."""
        import uuid
        conn = _conn()
        conn.execute("""
            INSERT INTO chat_history (id, user_message, assistant_response, timestamp, session_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            user_msg,
            assistant_msg,
            datetime.now().isoformat(),
            session_id
        ))
        conn.commit()
        conn.close()
    
    def get_session_history(self, session_id: str = "default", limit: int = 10) -> list:
        """Get chat history for a session."""
        conn = _conn()
        cursor = conn.execute("""
            SELECT user_message, assistant_response, timestamp
            FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        return messages


# Global chat assistant
chat_assistant = ChatAssistant()
chat_history = ChatHistory()
