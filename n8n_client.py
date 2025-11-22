"""
n8n webhook integration module.
Handles communication with the n8n LangChain agent.
"""
import requests
from typing import Dict, Any, Optional


def call_n8n_webhook(
    webhook_url: str,
    user_id: str,
    session_id: str,
    message: str,
    profile_summary: Optional[str] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Send a message to the n8n webhook and receive the assistant's reply.
    
    Args:
        webhook_url: Full URL of the n8n webhook
        user_id: UUID of the user
        session_id: UUID of the current session
        message: User's message text
        profile_summary: Optional profile summary for personalization
        timeout: Request timeout in seconds
    
    Returns:
        Dictionary with 'reply' key containing assistant's response,
        or error information if the call failed.
    """
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "message": message
    }
    
    # Include profile summary if available
    if profile_summary:
        payload["profile_summary"] = profile_summary
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Validate response structure
        if "reply" in data:
            return {"reply": data["reply"], "success": True}
        else:
            # If reply field is missing, try to extract from other possible fields
            # n8n might return data in different formats
            if "output" in data:
                return {"reply": data["output"], "success": True}
            elif "text" in data:
                return {"reply": data["text"], "success": True}
            else:
                print(f"Unexpected response format - missing 'reply', 'output', or 'text' fields")
                return {
                    "reply": "I cannot find this in the available resources.",
                    "success": False,
                    "error": "Invalid response format"
                }
    
    except requests.exceptions.Timeout:
        print(f"Request timeout after {timeout} seconds")
        return {
            "reply": "I'm taking longer than expected to respond. Please try again.",
            "success": False,
            "error": "timeout"
        }
    
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return {
            "reply": "I'm having trouble connecting to the assistant service. Please check your configuration.",
            "success": False,
            "error": "connection_error"
        }
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return {
            "reply": "The assistant service returned an error. Please try again later.",
            "success": False,
            "error": f"http_error: {e.response.status_code}"
        }
    
    except ValueError as e:
        print(f"JSON decode error: {e}")
        return {
            "reply": "I cannot find this in the available resources.",
            "success": False,
            "error": "json_decode_error"
        }
    
    except Exception as e:
        print(f"Unexpected error calling n8n webhook: {e}")
        return {
            "reply": "An unexpected error occurred. Please try again.",
            "success": False,
            "error": str(e)
        }
