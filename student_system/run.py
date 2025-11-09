from app import create_app, db 
from app.models import User, Student_Info, Major 

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Student_Info=Student_Info,
        Major=Major
    )

if __name__ == '__main__':
    app.run(debug=True)