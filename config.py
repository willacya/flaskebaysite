import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-dis'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'andrewwillacy@gmail.com'
    MAIL_PASSWORD = 'eejjutobtplpcuyc'
    ADMINS = ['andrewwillacy@gmail.com']
    LANGUAGES = ['en', 'es']
    POSTS_PER_PAGE = 25
    FLASK_DEBUG = 1


    OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '720828078682986',
        'secret': '22d95db2f12fd025b13b308c879797c8'
    },
    'twitter': {
        'id': 'flsLoSdNSbeWXdWx3qzrvwkOO',
        'secret': 'uf42rzv4hUck3ybLSrCmqX8r0iTtX3JsCSzcYchMBbQdmKIICH'
    },
    'google': {
        'id': '407204583184-vnvl8kbv8170d25oinnmvgakc496vti9.apps.googleusercontent.com',
        'secret': '6bRuA2hB-AB0xsIViVRtpuZv'
    }
    }


'''class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    LANGUAGES = ['en', 'es']
    POSTS_PER_PAGE = 25'''
