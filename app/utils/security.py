"""Security utilities and helpers."""

import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta

import structlog
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class APIKeyAuth(HTTPBearer):
    """API Key authentication."""
    
    def __init__(self):
        super().__init__(auto_error=False)
        self.settings = get_settings()
    
    async def __call__(self, request: Request) -> Optional[str]:
        """Validate API key."""
        
        # In development, allow unauthenticated requests
        if self.settings.environment == "development":
            return "development"
        
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            # Check for API key in headers
            api_key = request.headers.get(self.settings.api_key_header)
            if not api_key:
                raise HTTPException(
                    status_code=401,
                    detail="API key required"
                )
        else:
            api_key = credentials.credentials
        
        # Validate API key (implement your validation logic)
        if not self._validate_api_key(api_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        return api_key
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key format and existence."""
        
        # Basic validation
        if not api_key or len(api_key) < 20:
            return False
        
        # Add your API key validation logic here
        # For example, check against database or external service
        
        return True


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit."""
        
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old entries
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True


class SecurityUtils:
    """Security utility functions."""
    
    @staticmethod
    def generate_secret_key(length: int = 32) -> str:
        """Generate a secure random secret key."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_string(value: str, salt: str = "") -> str:
        """Hash a string with optional salt."""
        combined = f"{value}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def validate_content(content: str) -> bool:
        """Validate content for potential security issues."""
        
        # Basic XSS prevention
        dangerous_patterns = [
            "<script>", "</script>", "javascript:", 
            "onload=", "onerror=", "eval(", "exec("
        ]
        
        content_lower = content.lower()
        return not any(pattern in content_lower for pattern in dangerous_patterns)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize a filename for safe filesystem operations."""
        import re
        
        # Remove dangerous characters
        safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Prevent directory traversal
        safe_filename = safe_filename.replace('..', '_')
        
        # Limit length
        return safe_filename[:255]
    
    @staticmethod
    def log_security_event(event_type: str, details: dict, request: Optional[Request] = None):
        """Log security-related events."""
        
        log_data = {
            "security_event": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if request:
            log_data.update({
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "path": str(request.url.path) if request.url else "unknown"
            })
        
        logger.warning("security_event_detected", **log_data)