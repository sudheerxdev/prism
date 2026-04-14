"""
Advanced analytics dashboard for Prism.
Tracks productivity metrics, feedback patterns, and team insights.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import Counter
from queue_store import _conn


def get_analytics() -> Dict:
    """Get comprehensive analytics about the feedback system."""
    conn = _conn()
    cursor = conn.cursor()
    
    # Total items by lane
    cursor.execute("""
        SELECT lane, COUNT(*) as count 
        FROM messages 
        WHERE status != 'deleted'
        GROUP BY lane
    """)
    lanes = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Items processed today
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM messages 
        WHERE date(created_at) = date('now')
    """)
    result = cursor.fetchone()
    today_count = result[0] if result else 0
    
    # Average processing time
    cursor.execute("""
        SELECT AVG(julianday(classified_at) - julianday(created_at)) * 24 * 60 as avg_minutes
        FROM messages 
        WHERE classified_at IS NOT NULL 
        AND date(created_at) = date('now')
    """)
    avg_time_minutes = cursor.fetchone()[0] if cursor.fetchone()[0] else 0
    
    # Priority distribution
    cursor.execute("""
        SELECT priority, COUNT(*) as count 
        FROM messages 
        WHERE status != 'deleted'
        GROUP BY priority
    """)
    priorities = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Source breakdown (where feedback comes from)
    cursor.execute("""
        SELECT source, COUNT(*) as count 
        FROM messages 
        WHERE status != 'deleted'
        GROUP BY source
        ORDER BY count DESC
    """)
    sources = {row[0] or "Manual": row[1] for row in cursor.fetchall()}
    
    # Trend (last 7 days)
    cursor.execute("""
        SELECT date(created_at) as day, COUNT(*) as count
        FROM messages
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY day
        ORDER BY day
    """)
    trend = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Time to close (for issues marked as closed)
    cursor.execute("""
        SELECT AVG(julianday(updated_at) - julianday(created_at)) * 24 as avg_hours
        FROM messages
        WHERE status = 'closed' AND lane = 'Issues'
    """)
    avg_close_hours = cursor.fetchone()[0] if cursor.fetchone()[0] else 0
    
    # Most common feedback sources
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM messages
        GROUP BY source
        HAVING COUNT(*) > 0
        ORDER BY count DESC
        LIMIT 5
    """)
    top_sources = {row[0] or "Manual": row[1] for row in cursor.fetchall()}
    
    # Save rate (classified / total)
    cursor.execute("SELECT COUNT(*) FROM messages WHERE status != 'deleted'")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages WHERE status != 'deleted' AND classified_at IS NOT NULL")
    classified = cursor.fetchone()[0]
    classification_rate = (classified / total * 100) if total > 0 else 0
    
    conn.close()
    
    return {
        "lanes": lanes,
        "today_items": today_count,
        "avg_processing_minutes": round(avg_time_minutes, 2),
        "priorities": priorities,
        "sources": sources,
        "trend_7_days": trend,
        "avg_close_hours": round(avg_close_hours, 1),
        "top_sources": top_sources,
        "classification_rate": round(classification_rate, 1),
        "total_items": total,
        "classified_items": classified,
        "timestamp": datetime.now().isoformat()
    }


def get_team_insights() -> Dict:
    """Get insights about team productivity and feedback quality."""
    conn = _conn()
    cursor = conn.cursor()
    
    # Items per day (trend)
    cursor.execute("""
        SELECT date(created_at) as day, COUNT(*) as count
        FROM messages
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY day
    """)
    daily_counts = [row[1] for row in cursor.fetchall()]
    avg_per_day = sum(daily_counts) / len(daily_counts) if daily_counts else 0
    
    # Most active source channel
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM messages
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY source
        ORDER BY count DESC
        LIMIT 1
    """)
    busiest_source = cursor.fetchone()
    
    # Critical items still pending
    cursor.execute("""
        SELECT COUNT(*) FROM messages
        WHERE priority = 'critical' AND status IN ('pending', 'in_progress')
    """)
    critical_pending = cursor.fetchone()[0]
    
    # Quality score (based on classification rate, closure rate, thoroughness)
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN classified_at IS NOT NULL THEN 1 ELSE 0 END) as classified,
            SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
        FROM messages
        WHERE created_at >= datetime('now', '-30 days')
    """)
    stats = cursor.fetchone()
    total, classified, closed = stats if stats else (0, 0, 0)
    quality_score = 0
    if total > 0:
        classification_score = (classified / total) * 40  # 40% weight
        closure_score = (closed / total) * 30  # 30% weight
        volume_score = min(total / 10, 30)  # 30% weight (capped at 30)
        quality_score = (classification_score + closure_score + volume_score) / 100 * 100
    
    conn.close()
    
    return {
        "avg_items_per_day": round(avg_per_day, 1),
        "busiest_source": busiest_source[0] if busiest_source else "Unknown",
        "critical_pending": critical_pending,
        "quality_score": round(quality_score, 1),
        "timestamp": datetime.now().isoformat()
    }


def get_performance_metrics() -> Dict:
    """Get system performance and efficiency metrics."""
    conn = _conn()
    cursor = conn.cursor()
    
    # Agent success rate (items successfully processed)
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN tech_plan IS NOT NULL THEN 1 ELSE 0 END) as with_plan
        FROM messages
        WHERE classified_at IS NOT NULL
    """)
    total_processed, with_plan = cursor.fetchone()
    success_rate = (with_plan / total_processed * 100) if total_processed > 0 else 0
    
    # Time saved (estimated hours if manual vs AI)
    # Assumption: each item takes 15 min to manually process, AI takes 30 sec
    time_saved_hours = total_processed * (15 - 0.5) / 60
    
    # Items saved per hour efficiency
    cursor.execute("SELECT COUNT(*) FROM messages WHERE date(created_at) = date('now')")
    today = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "agent_success_rate": round(success_rate, 1),
        "estimated_hours_saved": round(time_saved_hours, 1),
        "items_processed_today": today,
        "avg_processing_speed_sec": 30,
        "timestamp": datetime.now().isoformat()
    }


def export_analytics_csv() -> str:
    """Export analytics to CSV format."""
    import csv
    from io import StringIO
    
    analytics = get_analytics()
    insights = get_team_insights()
    perf = get_performance_metrics()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write analytics section
    writer.writerow(["PRISM ANALYTICS REPORT", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    
    for key, value in analytics.items():
        if key != "timestamp":
            if isinstance(value, dict):
                for sub_key, sub_val in value.items():
                    writer.writerow([f"{key}.{sub_key}", sub_val])
            else:
                writer.writerow([key, value])
    
    writer.writerow([])
    writer.writerow(["Team Insights", "Value"])
    for key, value in insights.items():
        if key != "timestamp":
            writer.writerow([key, value])
    
    writer.writerow([])
    writer.writerow(["Performance", "Value"])
    for key, value in perf.items():
        if key != "timestamp":
            writer.writerow([key, value])
    
    return output.getvalue()
