from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, AnonymousUserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'your-very-complex-secret-key-12345'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/studentinfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问该页面'

class CustomAnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False

login_manager = LoginManager(app)
login_manager.anonymous_user = CustomAnonymousUser  

class User(UserMixin, db.Model):
    """用户模型（含角色字段）"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)  
    password_hash = db.Column(db.String(256), nullable=False)  
    role = db.Column(db.String(16), default='guest')  

    def set_password(self, password):
        """加密密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """判断是否为管理员"""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(), Length(3, 64, message='用户名长度需在3-64位之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(), Length(6, 128, message='密码长度需在6-128位之间'),
        EqualTo('confirm_password', message='两次输入的密码必须一致')
    ])
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册，请更换')

class LoginForm(FlaskForm):
    """登录表单（含记住我功能）"""
    username = StringField('用户名', validators=[DataRequired(), Length(3, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')  # 记住我功能
    submit = SubmitField('登录')

class NameForm(FlaskForm):
    id = IntegerField('Student ID', validators=[DataRequired()])
    name = StringField('Student Name', validators=[DataRequired()])
    major = SelectField('Major', coerce=int)
    submit = SubmitField('Submit')

class EditForm(NameForm):
    submit = SubmitField("Edit")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册路由"""
    if current_user.is_authenticated:  
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role='guest')
        user.set_password(form.password.data)  
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录！')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录路由"""
    if current_user.is_authenticated:  
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'欢迎回来，{user.username}！')
            return redirect(url_for('index'))
        flash('用户名或密码错误')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """用户登出路由"""
    logout_user()
    flash('已成功登出')
    return redirect(url_for('index'))

@app.route("/")
def index():
    """首页（学生列表）"""
    studs = Student_Info.query.all()
    majors = Major.query.all()
    return render_template('index.html', studs=studs, majors=majors)

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_stud():
    """新增学生（仅管理员可访问）"""
    if not current_user.is_admin():
        abort(403)  
    
    form = NameForm()
    form.major.choices = [(m.id, m.major_name) for m in Major.query.order_by('major_name')]
    if form.validate_on_submit():
        new_student = Student_Info(
            student_id=form.id.data,
            student_name=form.name.data,
            major=Major.query.get(form.major.data)
        )
        db.session.add(new_student)
        db.session.commit()
        flash("学生记录添加成功")
        return redirect(url_for('index'))
    return render_template("new_stud.html", form=form)

@app.route('/edit/<int:stu_id>', methods=['GET', 'POST'])
@login_required
def edit_stud(stu_id):
    """编辑学生（仅管理员可访问）"""
    if not current_user.is_admin():
        abort(403)
    
    stud = Student_Info.query.get_or_404(stu_id)
    form = EditForm()
    form.major.choices = [(m.id, m.major_name) for m in Major.query.order_by('major_name')]
    
    if form.validate_on_submit():
        stud.student_id = form.id.data
        stud.student_name = form.name.data
        stud.major = Major.query.get(form.major.data)
        db.session.commit()
        flash('学生记录更新成功')
        return redirect(url_for('index'))
    
    form.id.data = stud.student_id
    form.name.data = stud.student_name
    if stud.major:
        form.major.data = stud.major.id
    return render_template('edit_stud.html', form=form, stud=stud)

@app.route('/delete/<int:stud_id>', methods=['POST'])
@login_required
def del_stud(stud_id):
    """删除学生（仅管理员可访问）"""
    if not current_user.is_admin():
        abort(403)
    
    stud = Student_Info.query.get_or_404(stud_id)
    db.session.delete(stud)
    db.session.commit()
    flash('学生记录已删除')
    return redirect(url_for('index'))

@app.route("/major/<int:major_id>")
def filter_by_major(major_id):
    major = Major.query.get_or_404(major_id)
    studs = major.students.all()
    all_majors = Major.query.all()
    return render_template('index.html', studs=studs, majors=all_majors)

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Major.query.first():
            db.session.add_all([
                Major(major_name='计算机科学与技术'),
                Major(major_name='软件工程')
            ])
            db.session.commit()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')  
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
