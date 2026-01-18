from fastapi import WebSocket, HTTPException, status
from backend.app.auth.auth_utils import verify_token, get_user_by_email_or_phone
from backend.app.user.user_model import User

async def get_user_from_websocket(websocket: WebSocket) -> User:
    """
    Authenticate WebSocket connection using token from query params or headers.
    
    Args:
        websocket: WebSocket connection
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: If authentication fails
    """
    # Try to get token from query params first (common for WebSocket)
    token = websocket.query_params.get("token")
    
    # If not in query params, try to get from headers
    if not token:
        # WebSocket headers are accessed differently
        headers = dict(websocket.headers)
        auth_header = headers.get("authorization") or headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    
    try:
        # Verify and decode token
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise
    
    # Get user from database
    user = get_user_by_email_or_phone(email)
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

