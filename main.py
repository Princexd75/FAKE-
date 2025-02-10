from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = "random_secret_key"  # Change this to a strong secret key
oauth = OAuth(app)

# Facebook OAuth Configuration
facebook = oauth.remote_app(
    'facebook',
    consumer_key='YOUR_FACEBOOK_APP_ID',  # Replace with your Facebook App ID
    consumer_secret='YOUR_FACEBOOK_APP_SECRET',  # Replace with your Facebook App Secret
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

@app.route('/')
def home():
    if 'oauth_token' in session:
        user_info = facebook.get('/me?fields=name,email')
        return render_template('home.html', user=user_info.data)
    return render_template('home.html', user=None)

# Facebook Login Route
@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized', _external=True))

# Callback Route (After Login)
@app.route('/login/callback')
def facebook_authorized():
    response = facebook.authorized_response()
    if response is None or 'access_token' not in response:
        return "Login Failed!"

    session['oauth_token'] = (response['access_token'], '')
    user_info = facebook.get('/me?fields=name,email')
    session['user'] = user_info.data
    return redirect(url_for('home'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('oauth_token', None)
    session.pop('user', None)
    return redirect(url_for('home'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

if __name__ == '__main__':
    app.run(debug=True)
