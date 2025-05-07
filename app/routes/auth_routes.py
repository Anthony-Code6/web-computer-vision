from flask import Blueprint, render_template, request, session, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == "test@gmail.com" and password == "123123":
            session['usuario'] = email
            return redirect(url_for('main.index'))
        return render_template('login.html', error="Credenciales invalidas")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('auth.login'))