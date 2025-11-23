import os
import requests
from typing import List, Dict, Any
import streamlit as st

BACKEND_URL = os.getenv("FRONTEND_BACKEND_URL", "http://localhost:8000")

def _handle_request_error(error: Exception, action: str):
    """Centralized error handling with user-friendly messages"""
    error_msg = str(error)
    
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error(f" **Connection Error**: Cannot reach backend at {BACKEND_URL}")
        st.info(" **Tip**: Make sure your backend server is running!")
    elif isinstance(error, requests.exceptions.Timeout):
        st.error(f" **Timeout Error**: Backend took too long to respond")
        st.info(" **Tip**: The server might be busy. Try again in a moment.")
    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = error.response.status_code if hasattr(error, 'response') else 'Unknown'
        st.error(f" **HTTP Error {status_code}**: {action} failed")
        st.info(f" **Details**: {error_msg}")
    else:
        st.error(f"⚠️ **Unexpected Error**: {error_msg}")
    
    raise error


def get_actions() -> List[Dict[str, Any]]:
    """
    Get staged actions from the backend.
    
    Returns:
        List of action dictionaries with fields:
        - id: Action identifier
        - type: Action type (email, jira, calendar)
        - summary/title: Brief description
        - assignee: Person responsible
        - due_date: When action should be completed
        - confidence: AI confidence score (0-1 or 0-100)
        - status: Current status (staged, executed, failed)
        - snippet: Original transcript snippet
    
    Raises:
        requests.exceptions.RequestException: If request fails
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/actions", 
            timeout=10,
            headers={"Accept": "application/json"}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        _handle_request_error(e, "Fetching actions")


def execute_action(action_id: str) -> Dict[str, Any]:
    """
    Execute a single action by ID.
    
    Args:
        action_id: The unique identifier of the action to execute
    
    Returns:
        Response dictionary from backend
    
    Raises:
        requests.exceptions.RequestException: If request fails
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/actions/{action_id}/execute", 
            timeout=10,
            headers={"Accept": "application/json"}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        _handle_request_error(e, f"Executing action {action_id}")


def execute_all_actions() -> Dict[str, Any]:
    """
    Execute all staged actions at once.
    
    Returns:
        Response dictionary from backend
    
    Raises:
        requests.exceptions.RequestException: If request fails
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/actions/execute_all", 
            timeout=30,  # Longer timeout for batch operations
            headers={"Accept": "application/json"}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        _handle_request_error(e, "Executing all actions")


def simulate_meeting_end(demo_flag: bool = True) -> Dict[str, Any]:
    """
    Simulate a meeting end event to generate demo actions.
    
    For demo purposes, the backend can ignore meeting_id and generate 
    sample actions based on predefined templates.
    
    Args:
        demo_flag: If True, use demo/mock data
    
    Returns:
        Response dictionary from backend
    
    Raises:
        requests.exceptions.RequestException: If request fails
    """
    try:
        payload = {
            "meeting_id": "demo-meeting-123", 
            "demo": demo_flag,
            "timestamp": requests.utils.default_headers()  # Add timestamp for uniqueness
        }
        resp = requests.post(
            f"{BACKEND_URL}/api/hooks/meeting", 
            json=payload, 
            timeout=15,
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        _handle_request_error(e, "Simulating meeting end")


def check_backend_health() -> bool:
    """
    Check if backend is reachable and healthy.
    
    Returns:
        True if backend is healthy, False otherwise
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/health", 
            timeout=5
        )
        return resp.status_code == 200
    except:
        return False


def get_backend_info() -> Dict[str, Any]:
    """
    Get backend service information (version, status, etc.)
    
    Returns:
        Dictionary with backend info, or empty dict if unavailable
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/info", 
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()
    except:
        return {}
