import os
basepath = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = r'&3\x02\x8d\x86\x0c\x8cUy\xd93\xcc\x06\x9c\xce\xa8gcje\xde\xd9\x9a\x9c'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basepath, 'snappy.db')
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basepath, 'snappytest.db')
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True