from ensurepip import bootstrap
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

# 初始化Flask应用
app = Flask(__name__)
bootstrap = Bootstrap(app)

# 配置项
app.config['SECRET_KEY'] = 'xxx'  # 建议替换为复杂密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/studentinfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用修改跟踪

# 初始化数据库
print("准备定义 db...")
db = SQLAlchemy(app)
print("db 定义成功！")

# 数据库模型
class Major(db.Model):
    __tablename__ = 'majors'
    id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(100), unique=True, nullable=False)
    # 关联 Student_Info 模型
    students = db.relationship('Student_Info', backref='major', lazy='dynamic')
    def __repr__(self):
        return f'<Major {self.major_name}>'

class Student_Info(db.Model):
    __tablename__='student_info'
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.Text) 
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'))  # 外键关联专业

# 表单类
class NameForm(FlaskForm):
    id = IntegerField('Student ID', validators=[DataRequired()])
    name = StringField('Student Name', validators=[DataRequired()])
    major = SelectField('Major', coerce=int)  # 下拉选择专业
    submit = SubmitField('Submit')

class EditForm(NameForm):
    submit = SubmitField("Edit")

# 路由：首页（显示所有学生信息）
@app.route("/", methods=['GET', 'POST'])
def index():
    studs = Student_Info.query.all()
    majors = Major.query.all()  # 查询所有专业
    return render_template('index.html', studs=studs, majors=majors)

# 路由：新增学生
@app.route('/new', methods=['GET', 'POST'])
def new_stud():
    form = NameForm()
    # 动态加载专业选项
    form.major.choices = [(m.id, m.major_name) for m in Major.query.order_by('major_name').all()]
    if form.validate_on_submit():
        student_id = form.id.data
        student_name = form.name.data
        major_obj = Major.query.get(form.major.data)
        new_student = Student_Info(student_id=student_id, student_name=student_name, major=major_obj)
        db.session.add(new_student)
        db.session.commit() 
        flash("New student record saved successfully") 
        return redirect(url_for('index')) 
    return render_template("new_stud.html", form=form)

# 路由：编辑学生信息
@app.route('/edit/<int:stu_id>', methods=['GET', 'POST'])
def edit_stud(stu_id):
    form = EditForm()
    stud = Student_Info.query.get(stu_id)
    # 动态加载专业选项
    form.major.choices = [(m.id, m.major_name) for m in Major.query.order_by('major_name').all()]
    if form.validate_on_submit():
        stud.student_id = form.id.data
        stud.student_name = form.name.data
        stud.major = Major.query.get(form.major.data)
        db.session.commit() 
        flash('Student record updated successfully') 
        return redirect(url_for('index'))
    # 初始化表单数据
    form.id.data = stud.student_id
    form.name.data = stud.student_name
    if stud.major:
        form.major.data = stud.major.id
    return render_template('edit_stud.html', form=form)

# 新增删除学生的路由
@app.route('/delete/<int:stud_id>', methods=['POST'])
def del_stud(stud_id):
    stud = Student_Info.query.get(stud_id)
    if stud:
        db.session.delete(stud)
        db.session.commit()
        flash('学生记录已成功删除')
    else:
        flash('学生不存在')
    return redirect(url_for('index'))

@app.route("/major/<int:major_id>")
def filter_by_major(major_id):
    # 查找指定专业（若不存在则返回404）
    major = Major.query.get_or_404(major_id)
    # 通过专业的反向关系查询该专业下的所有学生
    studs = major.students.all()
    # 同时传递所有专业列表（保持筛选按钮可用）
    all_majors = Major.query.all()
    return render_template('index.html', studs=studs, majors=all_majors)
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 新增初始专业
        if not Major.query.all():
            m1 = Major(major_name='计算机科学与技术')
            m2 = Major(major_name='软件工程')
            db.session.add_all([m1, m2])
            db.session.commit()
    app.run(debug=True)