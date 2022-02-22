from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date,datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emp.db'
db = SQLAlchemy(app)

class EmpData(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usertype = db.Column(db.String(8), nullable = False, default = 'Employee')
    name = db.Column(db.String(30), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    doj = db.Column(db.Date, nullable = False)
    yoe = db.Column(db.Integer, nullable = False, default=1)
    skill_set = db.Column(db.Text, nullable = True)
    projects = db.Column(db.Text, nullable = True)

    def __repr__(self):
        return 'ID = '+str(self.id)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods = ['GET', 'POST'])
def register_emp():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        emp_name = request.form['emp_name']
        emp_type = request.form['user_type'] if request.form['user_type'] else 'Employee'
        emp_exp = request.form['emp_exp'] if request.form['emp_exp'] else 1
        emp_ss = request.form['emp_ss'] if request.form['emp_ss'] else None
        emp_pro = request.form['emp_pro'] if request.form['emp_pro'] else None
        emp_dob = datetime.strptime(request.form['emp_dob'], "%Y-%m-%d")
        emp_doj = datetime.strptime(request.form['emp_doj'], "%Y-%m-%d")
        new_emp = EmpData(id=emp_id, name=emp_name, usertype=emp_type, dob=emp_dob, doj=emp_doj, yoe=emp_exp, skill_set=emp_ss, projects=emp_pro)
        db.session.add(new_emp)
        db.session.commit()
        return render_template('index.html', submission_successful=True)
    else:
        return render_template('register.html')

@app.route('/search',methods = ['GET','POST'])
def search():
    si = request.form.get('s_id')
    sn = request.form.get('s_name')
    if si:
        q = EmpData.query.filter_by(id=si).first()
        return render_template('search.html', search_emp=q)
    elif sn:
        q = EmpData.query.filter_by(name=sn).first()
        return render_template('search.html', search_emp=q)
    else:
        return render_template('searchnew.html')

@app.route('/list')
def list_emp():
    all_emp = EmpData.query.all()
    return render_template('list.html', list_emp=all_emp)

@app.route('/update')
def update_emp():
    return render_template('update.html')

@app.route('/delete')
def delete_emp():
    return render_template('delete.html')

if __name__ == "__main__":
    app.run(debug=True)