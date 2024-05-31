import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///learnlink.db"
    SECRET_KEY = '9d8^7F&4s2@Lp#N6'
    SECURITY_PASSWORD_SALT = 'super-secret-salt'
    SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
    SECURITY_MSG_INVALID_PASSWORD = ("Bad username or password", "error")
    SECURITY_MSG_PASSWORD_NOT_PROVIDED = ("Bad username or password", "error")
    SECURITY_MSG_USER_DOES_NOT_EXIST = ("Bad username or password", "error")
    SECURITY_MSG_INVALID_EMAIL_ADDRESS = ("Bad username or password", "error")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

config = Config()
