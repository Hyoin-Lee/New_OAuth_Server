from flask import Flask, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = '635dc513f73c32d219843a6d5d81d3a29e289f6b'


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        if 'logout' in request.form:
            session.pop('username', None)
            return redirect(url_for('hello_world'))
        username = request.form.get('username')
        if username:
            session['username'] = username
            return (f'Hello, {username}! '
                    f'<form action="" method="post"><input type="submit" name="logout" value="Logout"></form>')
        else:
            return 'Please provide a username!'
    if 'username' in session:
        return (f'Hello, {session["username"]}! '
                f'<form action="" method="post"><input type="submit" name="logout" value="Logout"></form>')
    return '''
    <form action="" method="post">
      <input type="text" name="username" placeholder="username">
      <button type="submit">Login</button>
    </form>
    '''


if __name__ == '__main__':
    app.run(debug=True)
