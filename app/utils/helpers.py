from flask import session, redirect, url_for
from functools import wraps
from datetime import datetime

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime(format)
    except:
        return value