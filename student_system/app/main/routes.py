from flask import render_template, redirect, url_for, flash, abort
from . import main  
from .. import db  
from ..models import Student_Info, Major
from ..forms import NameForm, EditForm  
from flask_login import login_required, current_user  

@main.route("/")
def index():
    studs = Student_Info.query.all()
    majors = Major.query.all()
    return render_template('index.html', studs=studs, majors=majors)

@main.route('/new', methods=['GET', 'POST'])
@login_required
def new_stud():
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
        return redirect(url_for('main.index'))
    return render_template("new_stud.html", form=form)

@main.route('/edit/<int:stu_id>', methods=['GET', 'POST'])
@login_required
def edit_stud(stu_id):
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
        return redirect(url_for('main.index'))

    form.id.data = stud.student_id
    form.name.data = stud.student_name
    if stud.major:
        form.major.data = stud.major.id
    return render_template('edit_stud.html', form=form, stud=stud)

@main.route('/delete/<int:stud_id>', methods=['POST'])
@login_required
def del_stud(stud_id):
    if not current_user.is_admin():
        abort(403)
    
    stud = Student_Info.query.get_or_404(stud_id)
    db.session.delete(stud)
    db.session.commit()
    flash('学生记录已删除')
    return redirect(url_for('main.index'))

@main.route("/major/<int:major_id>")
def filter_by_major(major_id):
    if major_id == 0:  
        studs = Student_Info.query.all()
        current_major = None
    else:
        major = Major.query.get_or_404(major_id)
        studs = major.students.all()
        current_major = major
    all_majors = Major.query.all()
    return render_template('index.html', studs=studs, majors=all_majors, current_major=current_major)