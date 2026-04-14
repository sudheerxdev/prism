"""
Semantic search for Prism - find feedback by meaning, not just keywords.
Uses embeddings to understand intent and find similar issues.
"""

import sqlite3
import numpy as np
from typing import List, Dict, Tuple
from queue_store import _conn


class SemanticSearchEngine:
    """Search for similar feedback items using embeddings."""
    
    def __init__(self):
        """Initialize the search engine."""
        self.embeddings_cache = {}
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using a lightweight model.
        For MVP, use a simple TF-IDF style approach.
        For production, integrate sentence-transformers.
        """
        try:
            # Try to use sentence-transformers if available
            from sentence_transformers import SentenceTransformer
            if not hasattr(self, "model"):
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except ImportError:
            # Fallback: simple keyword-based embedding
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding using term frequency."""
        words = text.lower().split()
        # Create a simple 100-d embedding from word frequencies
        embedding = [0.0] * 100
        for word in words:
            idx = hash(word) % 100
            embedding[idx] += 1.0
        # Normalize
        magnitude = sum(x**2 for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        return embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        a = np.array(vec1)
        b = np.array(vec2)
        
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def search(self, query: str, limit: int = 5, threshold: float = 0.5) -> List[Dict]:
        """
        Search for items similar to query.
        Returns list of matching items with similarity scores.
        """
        conn = _conn()
        cursor = conn.execute("""
            SELECT id, content, title, lane, priority, created_at
            FROM messages
            WHERE status != 'deleted'
            ORDER BY created_at DESC
        """)
        
        items = cursor.fetchall()
        conn.close()
        
        if not items:
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Calculate similarity for each item
        results = []
        for item_id, content, title, lane, priority, created_at in items:
            # Combine title and content for search
            text = f"{title or ''} {content or ''}".strip()
            text_embedding = self.get_embedding(text)
            
            similarity = self.cosine_similarity(query_embedding, text_embedding)
            
            if similarity >= threshold:
                results.append({
                    "id": item_id,
                    "title": title,
                    "content": content[:100] + "..." if content and len(content) > 100 else content,
                    "lane": lane,
                    "priority": priority,
                    "similarity": round(similarity, 3),
                    "created_at": created_at
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:limit]
    
    def find_duplicates(self, item_id: str, threshold: float = 0.85) -> List[Dict]:
        """Find potential duplicate items."""
        conn = _conn()
        cursor = conn.cursor()
        
        # Get the reference item
        cursor.execute("""
            SELECT content, title FROM messages WHERE id = ?
        """, (item_id,))
        
        ref = cursor.fetchone()
        if not ref:
            conn.close()
            return []
        
        query = f"{ref[1] or ''} {ref[0] or ''}".strip()
        conn.close()
        
        # Search with high threshold
        duplicates = self.search(query, limit=10, threshold=threshold)
        
        # Filter out the original item
        duplicates = [d for d in duplicates if d["id"] != item_id]
        
        return duplicates
    
    def get_related(self, item_id: str, limit: int = 5) -> List[Dict]:
        """Get related items (same topic/domain)."""
        conn = _conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content, title FROM messages WHERE id = ?
        """, (item_id,))
        
        item = cursor.fetchone()
        conn.close()
        
        if not item:
            return []
        
        query = f"{item[1] or ''} {item[0] or ''}".strip()
        
        # Use lower threshold for "related" vs "duplicates"
        related = self.search(query, limit=limit + 1, threshold=0.3)
        
        # Filter out the original
        related = [r for r in related if r["id"] != item_id]
        
        return related[:limit]


# Global search engine
search_engine = SemanticSearchEngine()
