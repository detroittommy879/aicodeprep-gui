# Self-Hosted Authentication Solutions for aicodeprep-gui PySide6 App

**Date:** January 2, 2026  
**Analysis for:** aicodeprep-gui (PySide6 desktop application)

---

## Executive Summary

Your aicodeprep-gui is currently a **desktop application** that uses QSettings for local configuration. Adding authentication will require:

1. A backend server for user management
2. Integration between your PySide6 app and the auth server
3. A method to verify user licenses/subscriptions

The key consideration: **Desktop apps need an API-based auth approach** since they can't directly use traditional web session cookies.

---

## 🎯 Recommended Solution: Authentik + FastAPI Backend

### Why This Combination?

**Authentik** (self-hosted identity provider):

- ✅ Docker one-liner deployment
- ✅ Supports OAuth2/OIDC out of the box
- ✅ Built-in WebAuthn/Passkey support
- ✅ TOTP (Google Authenticator) 2FA
- ✅ Email verification (configurable, not required)
- ✅ Beautiful modern UI
- ✅ Free and open source
- ✅ Excellent documentation

**FastAPI Backend** (your custom API):

- Handles license validation
- Stores user subscriptions/pro status
- Communicates with Authentik for auth
- Serves as the bridge between your PySide6 app and Authentik

---

## 🚀 Quick Start: One-Command Deployment

### Option 1: Docker Compose (Recommended)

Create `docker-compose.yml` on your Ubuntu server:

```yaml
version: "3.8"

services:
  # PostgreSQL for both Authentik and your API
  postgresql:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${PG_PASS}
      POSTGRES_USER: authentik
      POSTGRES_DB: authentik
    volumes:
      - database:/var/lib/postgresql/data
    networks:
      - auth-network

  # Redis for Authentik caching
  redis:
    image: redis:alpine
    restart: unless-stopped
    networks:
      - auth-network

  # Authentik Server
  authentik-server:
    image: ghcr.io/goauthentik/server:latest
    restart: unless-stopped
    command: server
    environment:
      AUTHENTIK_SECRET_KEY: ${AUTHENTIK_SECRET_KEY}
      AUTHENTIK_ERROR_REPORTING__ENABLED: "false"
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS}
    volumes:
      - ./media:/media
      - ./custom-templates:/templates
    ports:
      - "9000:9000"
      - "9443:9443"
    depends_on:
      - postgresql
      - redis
    networks:
      - auth-network

  # Authentik Worker
  authentik-worker:
    image: ghcr.io/goauthentik/server:latest
    restart: unless-stopped
    command: worker
    environment:
      AUTHENTIK_SECRET_KEY: ${AUTHENTIK_SECRET_KEY}
      AUTHENTIK_ERROR_REPORTING__ENABLED: "false"
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS}
    volumes:
      - ./media:/media
      - ./certs:/certs
      - ./custom-templates:/templates
    depends_on:
      - postgresql
      - redis
    networks:
      - auth-network

  # Your FastAPI backend
  api-backend:
    build: ./api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://api_user:${API_DB_PASS}@postgresql:5432/aicp_users
      AUTHENTIK_URL: http://authentik-server:9000
      AUTHENTIK_CLIENT_ID: ${AUTHENTIK_CLIENT_ID}
      AUTHENTIK_CLIENT_SECRET: ${AUTHENTIK_CLIENT_SECRET}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - postgresql
      - authentik-server
    networks:
      - auth-network

volumes:
  database:

networks:
  auth-network:
    driver: bridge
```

Create `.env` file:

```bash
PG_PASS=your_secure_postgres_password
AUTHENTIK_SECRET_KEY=your_random_50_char_string
API_DB_PASS=your_api_db_password
AUTHENTIK_CLIENT_ID=will_be_generated
AUTHENTIK_CLIENT_SECRET=will_be_generated
JWT_SECRET=your_jwt_secret_key
```

**Deploy:**

```bash
docker-compose up -d
```

That's it! Authentik will be running on `http://your-server:9000`

---

## 🔐 How It Works: Authentication Flow

### Initial Setup (One-time)

1. User launches aicodeprep-gui
2. App shows "Login" dialog
3. Opens browser to your auth server
4. User logs in with email + passkey/password + 2FA
5. Server returns auth token
6. App stores token securely in QSettings (encrypted)

### Subsequent App Launches

1. App reads stored token
2. Validates token with backend API
3. If valid → app starts normally
4. If invalid/expired → show login dialog

### Pro License Verification

1. After login, app checks `/api/v1/user/license`
2. Backend returns: `{"has_pro": true, "expires": "2027-01-01"}`
3. App enables/disables pro features accordingly

---

## 🛠️ Implementation Details

### Part 1: FastAPI Backend (`api/main.py`)

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import httpx
import jwt
from typing import Optional

app = FastAPI(title="AICodePrep Auth API")

# Configuration
AUTHENTIK_URL = os.getenv("AUTHENTIK_URL", "http://localhost:9000")
AUTHENTIK_CLIENT_ID = os.getenv("AUTHENTIK_CLIENT_ID")
AUTHENTIK_CLIENT_SECRET = os.getenv("AUTHENTIK_CLIENT_SECRET")
JWT_SECRET = os.getenv("JWT_SECRET")

# Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserInfo(BaseModel):
    email: str
    user_id: str
    has_pro: bool
    pro_expires: Optional[datetime]

# OAuth2 scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{AUTHENTIK_URL}/application/o/authorize/",
    tokenUrl=f"{AUTHENTIK_URL}/application/o/token/"
)

# Database (simple SQLite for demo, use PostgreSQL in production)
import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY,
                  email TEXT UNIQUE,
                  has_pro BOOLEAN DEFAULT 0,
                  pro_expires TIMESTAMP,
                  gumroad_license TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.post("/api/v1/auth/token")
async def exchange_token(code: str, redirect_uri: str):
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTHENTIK_URL}/application/o/token/",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": AUTHENTIK_CLIENT_ID,
                "client_secret": AUTHENTIK_CLIENT_SECRET,
            }
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange token")

        token_data = response.json()

        # Get user info from Authentik
        user_response = await client.get(
            f"{AUTHENTIK_URL}/application/o/userinfo/",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )

        user_info = user_response.json()

        # Store/update user in database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("""INSERT INTO users (user_id, email) VALUES (?, ?)
                     ON CONFLICT(user_id) DO UPDATE SET email=excluded.email""",
                  (user_info['sub'], user_info['email']))
        conn.commit()
        conn.close()

        # Create our own JWT with user info
        our_token = jwt.encode({
            "sub": user_info['sub'],
            "email": user_info['email'],
            "exp": datetime.utcnow() + timedelta(days=30)
        }, JWT_SECRET, algorithm="HS256")

        return TokenResponse(
            access_token=our_token,
            token_type="bearer",
            expires_in=2592000  # 30 days
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInfo:
    """Validate token and return user info"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        email = payload.get("email")

        # Get user's pro status from database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT has_pro, pro_expires FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()

        if not row:
            has_pro, pro_expires = False, None
        else:
            has_pro, pro_expires = row
            if pro_expires:
                pro_expires = datetime.fromisoformat(pro_expires)
                # Check if expired
                if pro_expires < datetime.utcnow():
                    has_pro = False

        return UserInfo(
            email=email,
            user_id=user_id,
            has_pro=has_pro,
            pro_expires=pro_expires
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/v1/user/info")
async def get_user_info(user: UserInfo = Depends(get_current_user)):
    """Get current user information and license status"""
    return user

@app.post("/api/v1/user/activate-pro")
async def activate_pro(
    license_key: str,
    user: UserInfo = Depends(get_current_user)
):
    """Activate Pro license with Gumroad license key"""
    # Verify with Gumroad API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.gumroad.com/v2/licenses/verify",
            data={
                "product_id": "YOUR_GUMROAD_PRODUCT_ID",
                "license_key": license_key
            }
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid license key")

        license_data = response.json()

        if not license_data.get("success"):
            raise HTTPException(status_code=400, detail="License verification failed")

        # Activate pro (lifetime or set expiration)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("""UPDATE users
                     SET has_pro=1, pro_expires=?, gumroad_license=?
                     WHERE user_id=?""",
                  (None, license_key, user.user_id))  # None = lifetime
        conn.commit()
        conn.close()

        return {"success": True, "message": "Pro activated successfully"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "service": "aicp-auth"}
```

### Part 2: PySide6 Integration (`aicodeprep_gui/auth.py`)

```python
from PySide6 import QtCore, QtWidgets, QtWebEngineWidgets, QtNetwork
import json
import logging
from typing import Optional
from dataclasses import dataclass

@dataclass
class AuthUser:
    email: str
    user_id: str
    access_token: str
    has_pro: bool
    pro_expires: Optional[str]

class AuthManager(QtCore.QObject):
    """Handles authentication with the backend server"""

    auth_success = QtCore.Signal(AuthUser)
    auth_failed = QtCore.Signal(str)

    def __init__(self, api_base_url: str = "https://your-server.com"):
        super().__init__()
        self.api_base_url = api_base_url
        self.settings = QtCore.QSettings("aicodeprep-gui", "Auth")
        self.network_manager = QtNetwork.QNetworkAccessManager()

    def is_logged_in(self) -> bool:
        """Check if user has a valid token"""
        token = self.settings.value("access_token")
        if not token:
            return False

        # Validate token with backend
        return self.validate_token(token)

    def validate_token(self, token: str) -> bool:
        """Validate token with backend API"""
        # Synchronous validation for simplicity
        # In production, make this async
        import requests
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/user/info",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def get_stored_token(self) -> Optional[str]:
        """Get stored access token"""
        return self.settings.value("access_token")

    def store_token(self, token: str, user_info: dict):
        """Store access token and user info"""
        self.settings.setValue("access_token", token)
        self.settings.setValue("user_email", user_info.get("email"))
        self.settings.setValue("user_id", user_info.get("user_id"))
        self.settings.setValue("has_pro", user_info.get("has_pro", False))

    def clear_token(self):
        """Clear stored authentication data"""
        self.settings.remove("access_token")
        self.settings.remove("user_email")
        self.settings.remove("user_id")
        self.settings.remove("has_pro")

    def start_login_flow(self, parent_widget: QtWidgets.QWidget):
        """Start OAuth2 login flow"""
        # Create login dialog with embedded browser
        dialog = AuthDialog(self.api_base_url, parent=parent_widget)
        dialog.auth_completed.connect(self._on_auth_completed)
        dialog.exec()

    def _on_auth_completed(self, code: str):
        """Handle OAuth2 callback with authorization code"""
        # Exchange code for token
        import requests
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/auth/token",
                json={
                    "code": code,
                    "redirect_uri": "http://localhost:8765/callback"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]

                # Get user info
                user_response = requests.get(
                    f"{self.api_base_url}/api/v1/user/info",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )

                if user_response.status_code == 200:
                    user_info = user_response.json()
                    self.store_token(token, user_info)

                    auth_user = AuthUser(
                        email=user_info["email"],
                        user_id=user_info["user_id"],
                        access_token=token,
                        has_pro=user_info.get("has_pro", False),
                        pro_expires=user_info.get("pro_expires")
                    )

                    self.auth_success.emit(auth_user)
                else:
                    self.auth_failed.emit("Failed to get user info")
            else:
                self.auth_failed.emit("Failed to exchange token")
        except Exception as e:
            logging.error(f"Auth error: {e}")
            self.auth_failed.emit(str(e))

    def check_pro_status(self) -> bool:
        """Check if user has active Pro license"""
        token = self.get_stored_token()
        if not token:
            return False

        import requests
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/user/info",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                has_pro = data.get("has_pro", False)
                self.settings.setValue("has_pro", has_pro)
                return has_pro
        except:
            pass

        return False


class AuthDialog(QtWidgets.QDialog):
    """Dialog with embedded browser for OAuth2 login"""

    auth_completed = QtCore.Signal(str)

    def __init__(self, api_base_url: str, parent=None):
        super().__init__(parent)
        self.api_base_url = api_base_url
        self.setWindowTitle("Login to AICodePrep")
        self.resize(800, 600)

        layout = QtWidgets.QVBoxLayout(self)

        # Embedded web view
        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.web_view.urlChanged.connect(self._on_url_changed)

        layout.addWidget(self.web_view)

        # Start local callback server
        self._start_callback_server()

        # Navigate to auth URL
        auth_url = (
            f"{api_base_url}/application/o/authorize/"
            f"?client_id=YOUR_CLIENT_ID"
            f"&redirect_uri=http://localhost:8765/callback"
            f"&response_type=code"
            f"&scope=openid email profile"
        )
        self.web_view.setUrl(QtCore.QUrl(auth_url))

    def _start_callback_server(self):
        """Start local HTTP server to catch OAuth2 callback"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from urllib.parse import urlparse, parse_qs
        import threading

        dialog = self

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                query = urlparse(self.path).query
                params = parse_qs(query)

                if 'code' in params:
                    code = params['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<h1>Login successful!</h1><p>You can close this window.</p>")

                    # Emit signal with code
                    QtCore.QMetaObject.invokeMethod(
                        dialog,
                        "_handle_callback",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, code)
                    )

        self.server = HTTPServer(('localhost', 8765), CallbackHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    @QtCore.Slot(str)
    def _handle_callback(self, code: str):
        """Handle OAuth2 callback"""
        self.auth_completed.emit(code)
        self.accept()

    def _on_url_changed(self, url: QtCore.QUrl):
        """Monitor URL changes"""
        if url.toString().startswith("http://localhost:8765/callback"):
            # Callback will be handled by local server
            pass
```

### Part 3: Integration with Main Window

```python
# In aicodeprep_gui/gui/main_window.py

from aicodeprep_gui.auth import AuthManager

class FileSelectionGUI(QtWidgets.QMainWindow):
    def __init__(self, files):
        super().__init__()

        # Initialize auth manager
        self.auth_manager = AuthManager(api_base_url="https://your-server.com")

        # Check if user is logged in
        if not self.auth_manager.is_logged_in():
            self.show_login_dialog()
        else:
            # Check pro status
            has_pro = self.auth_manager.check_pro_status()
            # Update pro module
            from aicodeprep_gui import pro
            pro.enabled = has_pro

        # ... rest of initialization ...

    def show_login_dialog(self):
        """Show login dialog"""
        self.auth_manager.auth_success.connect(self._on_login_success)
        self.auth_manager.auth_failed.connect(self._on_login_failed)
        self.auth_manager.start_login_flow(self)

    def _on_login_success(self, user):
        """Handle successful login"""
        logging.info(f"Logged in as {user.email}")

        # Update pro status
        from aicodeprep_gui import pro
        pro.enabled = user.has_pro

        # Show welcome message
        QtWidgets.QMessageBox.information(
            self,
            "Login Successful",
            f"Welcome {user.email}!\n"
            f"Pro Status: {'Active' if user.has_pro else 'Free'}"
        )

    def _on_login_failed(self, error):
        """Handle login failure"""
        QtWidgets.QMessageBox.warning(
            self,
            "Login Failed",
            f"Authentication failed: {error}\n\n"
            "The app will run in offline mode."
        )
```

---

## 📧 Email Solutions (Easy Options)

### Option 1: SMTP2GO (Recommended for small scale)

- **Cost:** 1000 emails/month free
- **Setup:** 5 minutes
- **Docker:** Not needed, just SMTP credentials
- **Configuration:**

```python
# In Authentik email settings
SMTP_HOST=mail.smtp2go.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_USE_TLS=True
```

### Option 2: Mailgun

- **Cost:** 5000 emails/month free for 3 months
- **Setup:** 10 minutes (domain verification)
- **Pros:** Reliable, good API
- **Configuration:** Similar to SMTP2GO

### Option 3: Self-hosted (Docker-Mailu)

```yaml
# Add to docker-compose.yml
mailu:
  image: mailu/admin:latest
  restart: unless-stopped
  ports:
    - "25:25" # SMTP
    - "587:587" # Submission
  volumes:
    - ./mailu:/data
  environment:
    - SECRET_KEY=your_secret_key
    - DOMAIN=mail.yourdomain.com
```

---

## 🔒 2FA Options Without Email

### 1. TOTP (Time-based One-Time Password) ✅ RECOMMENDED

- **Supported by Authentik:** Yes, built-in
- **User Experience:** Scan QR code → Enter 6-digit code
- **Apps:** Google Authenticator, Authy, 1Password
- **Implementation:** Zero code, enable in Authentik UI

### 2. WebAuthn/Passkeys ✅ RECOMMENDED

- **Supported by Authentik:** Yes, built-in
- **User Experience:** Face ID, Touch ID, or security key
- **Security:** Highest level
- **Implementation:** Zero code, enable in Authentik UI

### 3. SMS (via Twilio)

- **Supported by Authentik:** Via webhook/custom flow
- **Cost:** ~$0.0075 per SMS
- **Setup:** Moderate complexity

### 4. Push Notifications (via Authentik Mobile)

- **Supported by Authentik:** Via companion app
- **Cost:** Free
- **User Experience:** Similar to Duo Push

---

## 🎨 Alternative Solutions Considered

### 1. **Keycloak**

- ❌ Heavier resource usage
- ❌ More complex configuration
- ✅ More enterprise features
- **Verdict:** Overkill for your use case

### 2. **Authelia**

- ✅ Lightweight
- ❌ Limited OAuth2 support
- ❌ No passkey support yet
- **Verdict:** Good for web apps, not ideal for desktop OAuth2

### 3. **Ory (Kratos + Hydra)**

- ✅ Modern architecture
- ❌ Requires multiple containers
- ❌ Steeper learning curve
- **Verdict:** Powerful but complex

### 4. **Supabase Auth**

- ✅ Very easy to use
- ✅ Great documentation
- ❌ Not fully self-hosted (needs their services)
- **Verdict:** Good option if you're okay with partial cloud dependency

### 5. **Build Your Own (Flask/FastAPI)**

- ✅ Full control
- ❌ Security risks if not done correctly
- ❌ Time-consuming to implement properly
- **Verdict:** Not recommended unless you're a security expert

---

## 🏗️ Implementation Roadmap

### Phase 1: Backend Setup (Day 1)

- [ ] Deploy Authentik via Docker Compose
- [ ] Configure OAuth2 application in Authentik
- [ ] Enable TOTP 2FA in Authentik
- [ ] Enable WebAuthn/Passkey in Authentik
- [ ] Create FastAPI backend
- [ ] Deploy FastAPI alongside Authentik

### Phase 2: PySide6 Integration (Days 2-3)

- [ ] Create `auth.py` module
- [ ] Implement OAuth2 flow in PySide6
- [ ] Add login dialog with embedded browser
- [ ] Store tokens securely in QSettings
- [ ] Add "Account" menu to main window

### Phase 3: License Management (Days 4-5)

- [ ] Integrate with Gumroad API
- [ ] Add "Activate Pro" dialog
- [ ] Implement license validation
- [ ] Update existing pro check to use auth system

### Phase 4: Polish & Testing (Days 6-7)

- [ ] Add "Logout" functionality
- [ ] Handle token refresh
- [ ] Add offline mode (graceful degradation)
- [ ] Test on Windows/Mac/Linux
- [ ] Write user documentation

---

## 💰 Cost Breakdown

### Self-Hosted on Your Ubuntu Server

- **Authentik:** Free (open source)
- **FastAPI:** Free (open source)
- **PostgreSQL:** Free (open source)
- **Domain:** $10-15/year (optional, can use IP)
- **SSL Certificate:** Free (Let's Encrypt)
- **Email (SMTP2GO):** Free (1000 emails/month)
- **Server resources:** Already have it!

**Total: ~$15/year (just domain)**

### Vs. Cloud Alternatives

- Auth0: $25+/month
- AWS Cognito: $0.0055/MAU (adds up quickly)
- Firebase Auth: Free tier limited, then pay-as-you-go

---

## 🚨 Security Considerations

### Token Storage

```python
# Don't store tokens in plain text!
# Use QSettings with encryption or OS keychain

# Windows: Use DPAPI
from cryptography.fernet import Fernet
import base64
import win32crypt

def encrypt_token_windows(token: str) -> bytes:
    return win32crypt.CryptProtectData(token.encode())

def decrypt_token_windows(encrypted: bytes) -> str:
    return win32crypt.CryptUnprotectData(encrypted)[1].decode()

# macOS/Linux: Use keyring library
import keyring

def store_token_secure(token: str):
    keyring.set_password("aicodeprep-gui", "access_token", token)

def get_token_secure() -> str:
    return keyring.get_password("aicodeprep-gui", "access_token")
```

### HTTPS is Mandatory

- Use Let's Encrypt for free SSL certificates
- **Never** send tokens over HTTP
- Configure Nginx reverse proxy for SSL termination

### Rate Limiting

```python
# In FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/auth/token")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def exchange_token(...):
    ...
```

---

## 📚 Resources & Documentation

### Authentik

- Docs: https://goauthentik.io/docs/
- Docker setup: https://goauthentik.io/docs/installation/docker-compose
- OAuth2 guide: https://goauthentik.io/docs/providers/oauth2/

### FastAPI

- Docs: https://fastapi.tiangolo.com/
- Security: https://fastapi.tianglo.com/tutorial/security/

### PySide6 OAuth2

- QWebEngineView: https://doc.qt.io/qtforpython-6/PySide6/QtWebEngineWidgets/QWebEngineView.html
- QNetworkAccessManager: https://doc.qt.io/qtforpython-6/PySide6/QtNetwork/QNetworkAccessManager.html

---

## 🎯 Minimal Viable Product (MVP)

If you want to get started ASAP with minimal features:

### 1-Day MVP (No OAuth, Just API Keys)

```python
# Skip OAuth entirely, just use API keys
# Users create account on web portal
# Get API key → paste into app

class SimpleAuthManager:
    def validate_api_key(self, api_key: str) -> bool:
        response = requests.get(
            f"{API_URL}/api/v1/validate",
            headers={"X-API-Key": api_key}
        )
        return response.status_code == 200

# In your app, add "Settings → API Key" field
```

**Pros:**

- Implement in 1 day
- No OAuth complexity
- Works offline (with cached validation)

**Cons:**

- Less user-friendly
- Users need to manually copy API keys
- No SSO benefits

---

## 🔄 Migration Path for Existing Users

Since you already have users with Gumroad licenses:

### Option 1: Grandfather Existing Users

```python
# Check if user has old pro.enabled via QSettings
old_license = QSettings("aicodeprep-gui", "ProLicense").value("license_key")

if old_license:
    # Auto-create account with email from Gumroad
    # Link license to new account
    # Send welcome email with login link
```

### Option 2: Manual Migration

- Add "Migrate to Cloud Account" menu option
- Opens dialog asking for email
- Validates Gumroad license
- Creates account
- Migrates pro status

---

## 🤔 FAQ

**Q: Do I need a domain name?**
A: Not required, but strongly recommended for SSL certificates. You can use DuckDNS for free.

**Q: Can users use the app offline?**
A: Yes, with cached token validation. App should validate tokens locally and only check with server periodically.

**Q: What if my server goes down?**
A: Implement graceful degradation – app works offline but can't verify new licenses.

**Q: How do I handle password resets?**
A: Authentik handles this automatically via email or admin panel.

**Q: Can I integrate with GitHub/Google login?**
A: Yes! Authentik supports OAuth2 federation. Users can "Sign in with GitHub."

**Q: What about user privacy?**
A: You control everything. No data leaves your server. GDPR-compliant by default.

---

## 📋 Next Steps

1. **Choose your solution**: I recommend Authentik + FastAPI
2. **Set up server**: Follow the Docker Compose guide above
3. **Test authentication**: Try logging in via browser first
4. **Integrate PySide6**: Use the code samples provided
5. **Test on all platforms**: Windows, macOS, Linux
6. **Deploy**: Update your app with new version

---

## 💬 Questions or Need Help?

This is a comprehensive guide but implementing auth is complex. Feel free to reach out if you need:

- Help with Docker setup
- PySide6 OAuth2 integration issues
- Security review
- Custom implementation for your specific needs

Good luck! 🚀
