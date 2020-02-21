"""
Example Github OAuth App
"""
import urllib.parse
from uuid import uuid4

from flask import Flask, abort, request
import requests
import requests.auth
import yaml

with open('config.yaml') as f:
    conf = yaml.load(f)
    CLIENT_ID = conf.get('CLIENT_ID', '')
    CLIENT_SECRET = conf.get('CLIENT_SECRET', '')
    REDIRECT_URI = conf.get('REDIRECT_URI', '')


def user_agent():
    return "oauth2-sample-app skailasa"


def return_format():
    return "application/json"


def base_headers():
    return {
        "User-Agent": user_agent(),
        "Accept": return_format(),
        }


app = Flask(__name__)
@app.route('/')
def homepage():

    text = f'<a href="{make_authorization_url()}">Authenticate with Github</a>'
    return text


def make_authorization_url():
    
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": "identity"}

    url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    return url


# (Potentially) to store valid states in a database or memcache.
def save_created_state(state):
    pass


def is_valid_state(state):
    return True


@app.route('/callback')
def callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        abort(403)

    code = request.args.get('code')

    access_token = get_token(code)
    username = get_username(access_token)

    return f"Your Github username is: {username}"


def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = base_headers()
    response = requests.get("https://github.com/login/oauth/access_token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)

    token_json = response.json()
    return token_json["access_token"]    


def get_username(access_token):
    headers = base_headers()
    headers['Authorization'] = f'token {access_token}'
    response = requests.get(
        "https://api.github.com/user",
        headers=headers
        )

    login = response.json()
    return login['login']


if __name__ == '__main__':
    app.run(debug=True, port=65010)
