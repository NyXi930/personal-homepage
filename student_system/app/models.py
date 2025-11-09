from . import db  
from . import login_manager  # 导入登录管理器
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class CustomAnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False

login_manager.anonymous_user = CustomAnonymousUser

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # 原代码的256位哈希长度
    role = db.Column(db.String(16), default='guest')  # 角色：admin/guest

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Major(db.Model):
    __tablename__ = 'majors'
    id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(100), unique=True, nullable=False)
    students = db.relationship('Student_Info', backref='major', lazy='dynamic')

    def __repr__(self):
        return f'<Major {self.major_name}>'

class Student_Info(db.Model):
    __tablename__ = 'student_info'
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.Text)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'))

    def __repr__(self):
        return f'<Student {self.student_id} - {self.student_name}>'