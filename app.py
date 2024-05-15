from flask import Flask, request, session, redirect, url_for
import paho.mqtt.publish as publish
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = '635dc513f73c32d219843a6d5d81d3a29e289f6b'
oauth = OAuth(app)
github = oauth.register('github',
                        authorize_url='https://github.com/login/oauth/authorize',
                        authoize_params = None,
                        access_token_url='https://github.com/login/oauth/access_token',
                        access_token_params = None,
                        client_id='Ov23liizxBpZHjL6DV2s',
                        client_secret='635dc513f73c32d219843a6d5d81d3a29e289f6b',
                        client_kwargs={'scope': 'user:email'})

# MQTT broker details
MQTT_BROKER = '127.0.0.1'
MQTT_PORT = 1883
MQTT_TOPIC = 'control_led'


@app.route('/login')
def login():
    # code from authlib documentation
    redirect_uri = url_for('authorize', _external=True)
    return github.authorize_redirect(redirect_uri, prompt='consent')


@app.route('/authorize')
def authorize():
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get('http://api.github.com/user')
    resp.raise_for_status()
    profile = resp.json()
    session['user_name'] = profile['login']
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if 'user_name' not in session:
        login_button = '<a href="' + url_for('login') + '">Login</a>'
        return f"Hello, stranger. Please {login_button} to continue."
    else:
        logout_button = '<a href="' + url_for('logout') + '">logout</a>'
        control_led_on_button = '''
                    <form action="/control_led_on" method="post">
                        <button type="submit">Turn LED On</button>
                    </form>
                '''
        control_led_off_button = '''
                    <form action="/control_led_off" method="post">
                        <button type="submit">Turn LED Off</button>
                    </form>
                '''
        return f"Hello, {session['user_name']}. You are now logged in. {logout_button}<br>{control_led_on_button} {control_led_off_button}"


@app.route('/control_led_on', methods=['POST'])
def control_led_on():
    if 'user_name' not in session:
        return 'User not logged in', 403

    # Publish MQTT message to turn LED on
    publish.single(MQTT_TOPIC, 'on', hostname=MQTT_BROKER, port=MQTT_PORT)

    return 'LED turned on'


@app.route('/control_led_off', methods=['POST'])
def control_led_off():
    if 'user_name' not in session:
        return 'User not logged in', 403

    # Publish MQTT message to turn LED off
    publish.single(MQTT_TOPIC, 'off', hostname=MQTT_BROKER, port=MQTT_PORT)

    return 'LED turned off'


if __name__ == '__main__':
    app.run(debug=True)
