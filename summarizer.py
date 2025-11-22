"""
Profile summary generation module.
Initial implementation uses simple frequency-based word extraction.
This can be replaced with LLM-based summarization via n8n webhook later.
"""
from typing import List, Dict
from collections import Counter
import re


def generate_simple_summary(messages: List[str], top_n: int = 5) -> str:
    """
    Generate a simple frequency-based summary from recent user messages.
    
    Args:
        messages: List of recent user message texts
        top_n: Number of top words to include in summary
    
    Returns:
        Summary string like "User often discusses: word1, word2, word3..."
    """
    if not messages:
        return ""
    
    # Combine all messages
    combined_text = " ".join(messages).lower()
    
    # Tokenize: split by non-alphanumeric characters
    words = re.findall(r'\b[a-z]+\b', combined_text)
    
    # Filter words: keep only words with 4+ characters
    filtered_words = [w for w in words if len(w) >= 4]
    
    if not filtered_words:
        return ""
    
    # Common stop words to exclude
    stop_words = {
        "what", "when", "where", "which", "this", "that", "these", "those",
        "with", "from", "have", "would", "could", "should", "about", "more",
        "some", "than", "into", "very", "after", "there", "their", "they",
        "been", "being", "were", "will", "your", "also", "just", "only",
        "like", "know", "want", "need", "make", "help", "tell", "show"
    }
    
    # Remove stop words
    meaningful_words = [w for w in filtered_words if w not in stop_words]
    
    if not meaningful_words:
        # If all words were filtered out, return empty
        return ""
    
    # Count frequencies
    word_counts = Counter(meaningful_words)
    
    # Get top N most common words
    top_words = [word for word, count in word_counts.most_common(top_n)]
    
    if not top_words:
        return ""
    
    # Format as summary
    summary = f"User often discusses: {', '.join(top_words)}"
    
    return summary


def should_update_summary(message_count: int, threshold: int) -> bool:
    """
    Determine if profile summary should be updated based on message count.
    
    Args:
        message_count: Total number of user messages in current session
        threshold: Number of messages before triggering summary update
    
    Returns:
        True if summary should be updated
    """
    return message_count > 0 and message_count % threshold == 0


def get_recent_user_messages(all_messages: List[Dict], limit: int = 12) -> List[str]:
    """
    Extract recent user messages from message list.
    
    Args:
        all_messages: List of all messages (dicts with 'role' and 'content')
        limit: Maximum number of recent messages to return
    
    Returns:
        List of recent user message content strings
    """
    user_messages = [
        msg["content"] for msg in all_messages
        if msg.get("role") == "user"
    ]
    
    # Return last N messages
    return user_messages[-limit:] if len(user_messages) > limit else user_messages


# Placeholder for future LLM-based summarization
def generate_llm_summary(webhook_url: str, messages: List[str]) -> str:
    """
    Future implementation: Call n8n webhook for LLM-based summarization.
    
    Args:
        webhook_url: n8n summarization webhook URL
        messages: List of recent user messages
    
    Returns:
        LLM-generated summary string
    """
    # TODO: Implement when n8n summarization webhook is ready
    # For now, fall back to simple summary
    return generate_simple_summary(messages)
