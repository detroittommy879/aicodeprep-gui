# GitHub Sponsor Verification System for aicodeprep-gui

## Overview

This document outlines various approaches to implement GitHub sponsor verification for enabling pro features in aicodeprep-gui. The system should verify if a user is sponsoring you on GitHub and unlock pro features accordingly.

## Current App Architecture Analysis

Based on the codebase analysis:
- **Current Pro System**: Uses a simple `pro_enabled` file or `--pro` flag
- **Network Capabilities**: Already has `requests` library and update checking via `update_checker.py`
- **Pro Features**: Located in `aicodeprep_gui/pro/` with preview window, level delegates, and patches
- **Settings**: Uses QSettings for persistent storage (`ButtonPresets`, `PromptOptions`, `UserIdentity`)

## Approach 1: Direct GitHub API Integration (SECURITY ISSUE - NOT RECOMMENDED)

### How It Works
1. User provides their GitHub username in the app
2. App makes API calls to GitHub's GraphQL API to check sponsorship status
3. Results are cached locally with expiration

### **CRITICAL SECURITY FLAW**
**This approach has a major security vulnerability**: Users can simply enter any sponsor's GitHub username to gain access to pro features. GitHub's sponsorship API allows you to check if ANY user is a sponsor, but it doesn't verify that the person using your app is actually that GitHub user.

**Example Attack:**
1. Alice sponsors you on GitHub
2. Bob finds out Alice's GitHub username (public information)
3. Bob enters Alice's username in your app
4. Bob gets pro features without paying

### Why This Doesn't Work
- **Sponsorship lists are often public** or discoverable
- **No identity verification** - anyone can claim to be any GitHub user
- **Username enumeration** - attackers could try common usernames of known sponsors

### Pros
- No server infrastructure needed
- Real-time verification
- Uses official GitHub API

### Cons
- **MAJOR SECURITY FLAW** - Anyone can use any sponsor's username
- Requires users to provide GitHub username
- API rate limits
- Requires internet connection

## Approach 2: Server-Based Verification with Webhook

### How It Works
1. GitHub webhook notifies your server when sponsorships change
2. Server maintains a database of current sponsors
3. App queries your server for verification

### Implementation Details

#### Backend Requirements (Ubuntu Server + Docker)
```dockerfile
# Dockerfile for verification service
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Server Components
- **FastAPI** web service
- **PostgreSQL** or **SQLite** database
- **GitHub webhook** endpoint
- **API endpoint** for verification

#### Files to Create

**Server Side:**
- `server/main.py` - FastAPI application
- `server/models.py` - Database models
- `server/github_webhook.py` - Webhook handler
- `server/verification_api.py` - Verification endpoints
- `server/docker-compose.yml` - Docker setup

**Client Side:**
- `aicodeprep_gui/server_verification.py` - Server communication
- Update existing pro system files

#### Server API Design
```python
# Endpoints
POST /webhook/github  # Receives GitHub webhook events
GET /verify/{username}  # Check if user is sponsor
GET /health  # Health check
```

### Pros
- Real-time updates via webhooks
- Can handle complex sponsorship logic
- Centralized verification
- Better for scaling

### Cons
- Requires server infrastructure
- More complex setup
- Additional maintenance overhead

## Approach 3: Hybrid Token-Based System

### How It Works
1. Server generates unique tokens for verified sponsors
2. Users enter token in the app
3. App validates token with server

### Implementation Details

#### Token Generation Process
1. GitHub webhook updates sponsor database
2. Server generates unique tokens for active sponsors
3. Tokens sent via email or GitHub issue/discussion

#### Client Implementation
```python
class TokenVerifier:
    def verify_token(self, token: str) -> bool:
        """Verify token with server"""
        response = requests.post(
            "https://your-server.com/verify-token",
            json={"token": token}
        )
        return response.json().get("valid", False)
```

### Pros
- Simple user experience (just enter token)
- No need to share GitHub username
- Works offline after initial verification

### Cons
- Manual token distribution
- Requires server infrastructure
- Token management complexity

## Approach 4: GitHub OAuth Integration (NOW RECOMMENDED)

### How It Works
1. Create a GitHub App or OAuth App
2. User clicks "Verify with GitHub" in your app
3. Browser opens to GitHub OAuth authorization
4. User authorizes your app to read their sponsorship data
5. App receives OAuth token and verifies sponsorship using authenticated API calls
6. **Identity is verified** because the user must log into their actual GitHub account

### Implementation Details

#### GitHub App Setup
```
1. Go to GitHub Settings > Developer settings > GitHub Apps
2. Create new GitHub App with these permissions:
   - Repository permissions: None needed
   - Account permissions: 
     - Sponsorships: Read (to check if user sponsors you)
   - User permissions:
     - Profile: Read (to get user info)
```

#### OAuth Flow
```python
# aicodeprep_gui/github_oauth.py
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class GitHubOAuth:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = "http://localhost:8080/callback"
        
    def start_oauth_flow(self):
        """Opens browser for GitHub OAuth and starts local server for callback"""
        # Start local server to receive callback
        # Open browser to GitHub OAuth URL
        # Wait for callback with authorization code
        # Exchange code for access token
        # Verify sponsorship with authenticated API call
```

#### Security Benefits
- **Identity Verification**: User must actually log into their GitHub account
- **Tamper Proof**: OAuth tokens are cryptographically signed
- **Official Process**: Uses GitHub's standard authentication flow
- **Revocable**: Users can revoke access anytime in GitHub settings

#### Files to Create/Modify
- `aicodeprep_gui/github_oauth.py` - OAuth flow handling
- `aicodeprep_gui/gui/oauth_dialog.py` - OAuth authorization UI
- `aicodeprep_gui/oauth_config.py` - Store OAuth credentials securely
- Update pro system integration

### Pros
- **Secure identity verification** - solves the username spoofing problem
- Official GitHub integration
- Users control access via GitHub settings
- Can access private sponsorship data
- No server infrastructure needed initially

### Cons
- More complex implementation than simple API calls
- Requires GitHub App creation and approval
- Users must authorize app (but this is actually a security feature)
- Requires handling OAuth callback (local HTTP server)

## Recommended Implementation Plan

### Phase 1: GitHub OAuth Integration (Approach 4) - UPDATED RECOMMENDATION

**Why This First:**
- Provides actual identity verification
- Uses official GitHub authentication
- Secure and tamper-proof
- Can be implemented without server infrastructure initially

**Implementation Steps:**

1. **Create GitHub App**
```
1. Go to https://github.com/settings/apps
2. Click "New GitHub App"
3. Fill in details:
   - Name: "aicodeprep-gui Sponsor Verification"
   - Homepage URL: Your GitHub repo URL
   - Callback URL: http://localhost:8080/callback
   - Permissions: Sponsorships (Read), Profile (Read)
4. Generate client secret
5. Note down Client ID and Client Secret
```

2. **Create OAuth Handler**
```python
# aicodeprep_gui/github_oauth.py
import webbrowser
import urllib.parse
import requests
import secrets
import hashlib
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from PySide6.QtCore import QObject, pyqtSignal

class GitHubOAuthHandler(QObject):
    authentication_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, client_id: str):
        super().__init__()
        self.client_id = client_id
        self.state = secrets.token_urlsafe(32)
        self.code_verifier = secrets.token_urlsafe(32)
        self.code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self.code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
    def start_oauth_flow(self):
        """Start the OAuth flow"""
        # Implementation for PKCE OAuth flow
        # Opens browser, starts local server, handles callback
```

3. **Create Verification Dialog**
```python
# aicodeprep_gui/gui/oauth_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QProgressBar
from PySide6.QtCore import QTimer

class GitHubOAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.oauth_handler = GitHubOAuthHandler(CLIENT_ID)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.info_label = QLabel(
            "To enable Pro features, verify your GitHub sponsorship.\n"
            "This will open GitHub in your browser for secure authentication."
        )
        
        self.verify_button = QPushButton("Verify with GitHub")
        self.verify_button.clicked.connect(self.start_verification)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        
        layout.addWidget(self.info_label)
        layout.addWidget(self.verify_button)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
```

4. **Update Pro System**
```python
# Modify aicodeprep_gui/pro/__init__.py
from ..github_oauth import is_verified_sponsor

def is_pro_enabled():
    # Check traditional methods first
    if '--pro' in sys.argv or os.path.isfile('pro_enabled'):
        return True
        
    # Check OAuth verification
    return is_verified_sponsor()
```

5. **Add Secure Token Storage**
```python
# aicodeprep_gui/secure_storage.py
from PySide6.QtCore import QSettings
import json
import base64
from cryptography.fernet import Fernet
import os

class SecureTokenStorage:
    def __init__(self):
        self.settings = QSettings("aicodeprep-gui", "SecureTokens")
        self.key = self._get_or_create_key()
        
    def store_oauth_token(self, token_data: dict):
        """Securely store OAuth token"""
        # Encrypt and store token
        
    def get_oauth_token(self) -> dict:
        """Retrieve and decrypt OAuth token"""
        # Decrypt and return token
```

### Phase 2: Server Enhancement (Optional)

If the direct API approach has limitations, implement server-based verification:

1. **Deploy Simple Verification Server**
```python
# server/main.py
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/verify/{username}")
async def verify_sponsor(username: str):
    # Server-side verification logic
    # Can include caching, rate limiting, etc.
```

2. **Update Client to Use Server**
```python
# Modify sponsor_verification.py to use server endpoint
def verify_via_server(self, username: str) -> dict:
    response = requests.get(f"https://your-server.com/verify/{username}")
    return response.json()
```

## Configuration Options

### Sponsorship Tiers
```python
# sponsor_verification.py
SPONSORSHIP_TIERS = {
    "any": 0,      # Any amount qualifies
    "basic": 5,    # $5/month minimum
    "premium": 25, # $25/month minimum
}

def check_sponsorship_tier(self, amount: float) -> str:
    if amount >= SPONSORSHIP_TIERS["premium"]:
        return "premium"
    elif amount >= SPONSORSHIP_TIERS["basic"]:
        return "basic"
    elif amount > 0:
        return "any"
    return "none"
```

### Cache Management
```python
CACHE_DURATION = timedelta(hours=24)  # Re-verify every 24 hours
RETRY_FAILED_AFTER = timedelta(hours=1)  # Retry failed verifications after 1 hour
```

## Security Considerations

1. **API Rate Limiting**: Implement client-side rate limiting
2. **Cache Security**: Store verification cache in user directory with appropriate permissions
3. **Error Handling**: Graceful degradation when verification fails
4. **Privacy**: Only store necessary data, allow cache clearing

## User Experience Flow

1. **First Time Setup**:
   - User tries to access pro feature
   - App shows "Pro features require GitHub sponsorship"
   - User clicks "Verify Sponsorship"
   - Dialog asks for GitHub username
   - App verifies and caches result

2. **Ongoing Usage**:
   - App checks cached verification (valid for 24 hours)
   - If cache expired, re-verify in background
   - Show sponsorship status in UI

3. **Error Handling**:
   - Network errors: Use cached result if available
   - Invalid username: Show helpful error message
   - API rate limits: Implement exponential backoff

## Testing Strategy

1. **Mock GitHub API** for development
2. **Test with actual GitHub accounts** (your own sponsors)
3. **Error condition testing** (network failures, invalid usernames)
4. **Cache behavior testing** (expiration, corruption)

## Deployment Considerations

1. **Client Updates**: Verification system should be updateable
2. **Backward Compatibility**: Don't break existing `--pro` flag
3. **Graceful Degradation**: App should work even if verification fails
4. **User Communication**: Clear messaging about sponsorship requirements

This approach provides a solid foundation that can be enhanced over time while maintaining simplicity and reliability.
## Al
ternative Secure Approaches (If OAuth is Too Complex)

### Approach 5: Email-Based Verification

**How It Works:**
1. User enters their email address
2. App sends verification request to your server
3. Server checks if that email is associated with a GitHub sponsor
4. Server sends unique verification code to the email
5. User enters code in app to unlock pro features

**Pros:**
- Simple user experience
- Secure (requires access to sponsor's email)
- No OAuth complexity

**Cons:**
- Requires server infrastructure
- Need to collect sponsor emails somehow
- Email delivery issues

### Approach 6: GitHub Issue/Discussion Token System

**How It Works:**
1. When someone sponsors you, GitHub notifies you
2. You manually create a GitHub issue or discussion with a unique token
3. Only the sponsor can see/access this token (private repo or mention them)
4. Sponsor enters token in your app
5. App validates token with your server

**Pros:**
- Uses GitHub's existing notification system
- Secure (only sponsor has access to token)
- No complex OAuth implementation

**Cons:**
- Manual process for you
- Requires server for token validation
- Not automated

## Security Comparison

| Approach | Identity Verification | Automation | Server Required | Complexity |
|----------|----------------------|------------|-----------------|------------|
| Direct API (Approach 1) | ❌ None | ✅ Full | ❌ No | 🟢 Low |
| Server + Webhook (Approach 2) | ❌ None | ✅ Full | ✅ Yes | 🟡 Medium |
| Token System (Approach 3) | ❌ None | 🟡 Partial | ✅ Yes | 🟡 Medium |
| GitHub OAuth (Approach 4) | ✅ Strong | ✅ Full | ❌ No* | 🔴 High |
| Email Verification (Approach 5) | 🟡 Medium | 🟡 Partial | ✅ Yes | 🟡 Medium |
| GitHub Issue Token (Approach 6) | ✅ Strong | ❌ Manual | ✅ Yes | 🟢 Low |

*OAuth can work without server initially, but may need server for production

## Final Recommendation

Given the security requirements, I recommend **Approach 4 (GitHub OAuth)** because:

1. **Solves the identity problem** - Users must actually log into their GitHub account
2. **Official and secure** - Uses GitHub's standard authentication
3. **Future-proof** - Can be enhanced with server components later
4. **User-friendly** - Familiar OAuth flow that users trust

The implementation can start simple (desktop OAuth with local callback server) and be enhanced later with proper server infrastructure if needed.

Would you like me to create a detailed implementation guide for the OAuth approach, or would you prefer to explore one of the other secure alternatives?