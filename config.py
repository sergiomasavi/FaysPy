"""
Este archivo organiza las configuraciones de todo el proyecto y ayudará a diferenciar entre las conviguraciones
en desarrollo, prueba y producción para la base de datos
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY','secret')
    STREAM_API_KEY = '' #Insert your Stream api KEY her
    STREAM_SCRET = '' #Insert your Stream Secret here
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('MAIL_FAYS_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_FAYS_PASSWORD')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OFFBRAND_MAIL_SUBJECT_PREFIX = '[FaysPy]'
    OFFBRAND_MAIL_SENDER = 'Fayspy <fayspy.ds@gmail.com>'
    OFFBRAND_ADMIN = os.environ.get('fayspy.ds@gmail.com')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}