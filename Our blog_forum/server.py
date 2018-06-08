from flask import Flask, render_template, g, request, redirect
import sqlite3, os, re

DATABASE = './blog.sqlite'

app = Flask(__name__)


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


def get_all_users():
    users = g.db.execute('SELECT * FROM user').fetchall()
    return users


def print_users(user_list):
    for user in user_list:
        print_user(user)


def print_user(user):
    print('username: ', user['username'], ', password: ', user['password'], ', e-mail: ', user['email'], ', role: ',
          user['role'])


@app.route('/users/add', methods=('GET', 'POST'))
def add_user():
    error = None
    g.active_url = '/users/add'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        db = get_db()
        if role == "admin" or "moderator":
            error = "You don't have permission to perform this action!"
        if not username:
            error = 'Username is required!  '
        elif not password:
            error = 'Password is required!'
        elif not email:
            error = 'E-mail is required!'
        elif not role:
            error = "Role is required!"
        elif not match:
            error = 'Invalid E-mail!'
        elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(username)
        elif db.execute(
                'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'E-mail {0} is already in use.'.format(email)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, email, role) VALUES (?, ?, ?, ?)',
                (username, password, email, role)
            )
            db.commit()
            return redirect('users')

    return render_template('user/add-user.html', error=error)


@app.route('/users/<int:id>/edit', methods=('POST', 'GET'))
def edit_user(id):
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (id,)
    ).fetchone()
    error = None
    if user is None:
        error = 'User with ID={0} does not exist.'.format(id)
    else:
        print_user(user)
    g.active_url = '/users/edit'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        db = get_db()
        if not username:
            error = 'Username is required!  '
        elif not password:
            error = 'Password is required!'
        elif not email:
            error = 'E-mail is required!'
        elif not role:
            error = "Role is required!"
        elif not match:
            error = 'Invalid E-mail!'
        elif user['username'] != username and db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(username)
        elif db.execute(
                'SELECT email FROM user WHERE email = ?', (email,)
        ).fetchone == email:
            error = 'E-mail {0} already exists!'.format(email)

        if error is None:
            db.execute(
                'UPDATE user SET username=?, password=?, email=?,role=? WHERE id = ?',
                (username, password, email, role, id)
            )
            db.commit()
            return redirect('/users')

    return render_template('/user/edit-user.html', user=user, error=error)


@app.route('/users/<int:id>/delete', methods=('POST',))
def delete_user(id):
    db = get_db()
    # if db.execute(
    #             'SELECT id FROM user WHERE id = ?', (id,)
    #     ).fetchone() is not None:
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return redirect('/users')

@app.route('/posts')
def show_posts():
    return render_template('/posts/posts.html')

# @app.route('/posts/add')
# def get_post(id, check_author=True):
#     error = None
#     post=get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         'FROM post p JOIN user u ON p.author_id = u.id'
#         'WHERE p.id = ?',
#         (id,)
#     ).fetchone()
#     if post is None:
#         error = "Post {} does not exist".format(id)
#     if check_author and post['author_id'] != g.user['id']:
#         error = "Forbidden"
#
#     return post



@app.route('/login', methods=('GET', 'POST'))
def user_login():
    if request.method == 'POST':
        g.active_url='/login/login'
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif user == user['username'] and password != user['password']:
            error = 'Incorrect password.'
        if error is None:
            print("OK")

    return render_template('/login/login.html',)


@app.route('/users')
def users():
    g.active_url = '/users'
    db = get_db()
    users = get_all_users()
    print_users(users)
    return render_template('user/users.html', users=users)


@app.route('/')
def home():
    g.active_url = '/'
    return render_template('/home/home.html')


if __name__ == '__main__':
    app.run()
