from flask import Flask, redirect, url_for, session, request, jsonify
from msal import ConfidentialClientApplication

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Default for local testing

# Azure AD Configuration from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:5000/getAToken"
SCOPES = ["User.Read"]

# MSAL Confidential Client
msal_app = ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

@app.route('/')
def index():
    """Home route"""
    return '<a href="/login">Login with Azure AD</a>'

@app.route('/login')
def login():
    """Initiates the login process"""
    # Build the authorization URL
    auth_url = msal_app.get_authorization_request_url(
        SCOPES, redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)

@app.route('/getAToken')
def get_a_token():
    """Handles the redirect and obtains tokens"""
    code = request.args.get('code')
    if not code:
        return "Login failed. No authorization code received.", 400

    # Exchange the authorization code for an access token
    result = msal_app.acquire_token_by_authorization_code(
        code, scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    
    if "access_token" in result:
        session["user"] = result.get("id_token_claims")
        return redirect(url_for("profile"))
    else:
        return f"Token acquisition failed: {result.get('error_description')}", 400

@app.route('/profile')
def profile():
    """Displays the user's profile information"""
    if "user" not in session:
        return redirect(url_for("index"))

    user = session["user"]
    return jsonify(user)

@app.route('/logout')
def logout():
    """Logs the user out and clears the session"""
    session.clear()
    logout_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/logout?post_logout_redirect_uri=http://localhost:5000"
    return redirect(logout_url)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
