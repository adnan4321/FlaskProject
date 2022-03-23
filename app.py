from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import date,datetime
import string,random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emp.db'
app.config['SECRET_KEY'] = 'thisisatestsecret'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return EmpCred.query.get(int(user_id))

class EmpData(db.Model):
    __tablename__ = "empdata"
    id = db.Column(db.Integer, primary_key = True)
    usertype = db.Column(db.String(8), nullable = False, default = 'Employee')
    name = db.Column(db.String(30), nullable = False)
    dob = db.Column(db.Date, nullable = False)
    doj = db.Column(db.Date, nullable = False)
    yoe = db.Column(db.Integer, nullable = False, default=1)
    skill_set = db.Column(db.Text, nullable = True)
    projects = db.Column(db.Text, nullable = True)
    empcred = db.relationship('EmpCred',backref = 'data', uselist = False)

    def __repr__(self):
        return f"User ('{str(self.id)}','{str(self.name)}')"

class EmpCred(db.Model, UserMixin):
    __tablename__ = "empcred"
    username = db.Column(db.String(30), nullable = False)
    password = db.Column(db.String(30), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('empdata.id'), primary_key = True,unique = True)

    def get_id(self):
        return (self.user_id)

    def __repr__(self):
        return f"Username: {str(self.username)}"

@app.route('/')
@login_required
def home():
    return render_template('index_emp.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        emp_user = EmpCred.query.filter_by(username=request.form['emp_user']).first()
        if emp_user:
            if emp_user.password == request.form['emp_pw']:
                    login_user(emp_user)
                    return render_template('index_emp.html')
            else:
                return render_template('login.html', incorrect_pw=True)
        else:
            return render_template('login.html', incorrect_user=True)
    else:
        return render_template('login.html')


@app.route('/register', methods = ['GET', 'POST'])
@login_required
def register_emp():
    str_set = string.ascii_uppercase + string.ascii_lowercase + string.digits
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
        emp_un = emp_name.split(' ')[0]+emp_id
        emp_pw = ''.join(random.choices(str_set,k=8))
        new_cred = EmpCred(username=emp_un,password=emp_pw,user_id=emp_id)
        db.session.add(new_emp)
        db.session.add(new_cred)
        db.session.commit()
        return render_template('index_emp.html', submission_successful=True)
    else:
        return render_template('register.html')

@app.route('/search',methods = ['GET','POST'])
@login_required
def search():
    if request.method == 'POST':
        si = request.form.get('s_id')
        searchid = si.split(',')
        sn = request.form.get('s_name')
        searchname = sn.split(',')
        slist = []
        if si:
            for info in searchid:
                if EmpData.query.filter_by(id=info).first() != None:
                    slist.append(EmpData.query.filter_by(id=info).first())
        else:
            for info in searchname:
                if EmpData.query.filter_by(name=info).first() != None:
                    slist.append(EmpData.query.filter_by(name=info).first())
        return render_template('search.html', search_emp=slist,flag=1)
    else:
        return render_template('search.html',flag=0)

@app.route('/list')
@login_required
def list_emp():
    all_emp = EmpData.query.all()
    return render_template('list.html', list_emp=all_emp)

@app.route('/edit/<int:id>', methods = ['GET','POST'])
@login_required
def update_emp(id):
    emp_data = EmpData.query.get(id)
    if request.method == 'POST':
        emp_data.name = request.form['emp_name']
        emp_data.yoe = request.form['emp_exp']
        emp_data.skill_set = request.form['emp_ss']
        emp_data.projects = request.form['emp_pro']
        emp_data.dob = datetime.strptime(request.form['emp_dob'], "%Y-%m-%d")
        emp_data.doj = datetime.strptime(request.form['emp_doj'], "%Y-%m-%d")
        db.session.commit()
        return render_template('index_emp.html',update_successful=True)
    else:
        return render_template('update.html',emp_data=emp_data)

@app.route('/edit/change/<int:id>', methods = ['GET','POST'])
@login_required
def changecred_emp(id):
    emp_data = EmpData.query.get(id)
    if request.method == 'POST':
        npw = request.form['emp_npw']
        newpw = request.form['emp_cnpw']
        if npw == newpw:
            emp_data.pcred.password = newpw
            db.session.commit()
            return render_template('index_emp.html',change_successful=True)
        else:
            return render_template('changecred.html',notsame=True)
    else:
        return render_template('changecred.html',emp_data=emp_data)

@app.route('/delete/<int:id>')
@login_required
def delete_emp(id):
    emp_data = EmpData.query.get(id)
    db.session.delete(emp_data.empcred)
    db.session.delete(emp_data)
    db.session.commit()
    return render_template('index_emp.html',delete_successful=True)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)