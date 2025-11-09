import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-complex-secret-key-12345'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/studentinfo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
