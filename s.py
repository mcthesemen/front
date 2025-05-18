from flask import render_template
from models import Work, User


@app.route('/works')
def work_list():
    works = Work.query.all()  # Предполагается, что у вас есть модель Work
    return render_template('work_list.html', works=works)
