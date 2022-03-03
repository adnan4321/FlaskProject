from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import date,datetime

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
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        emp_user = EmpCred.query.filter_by(username=request.form['emp_user']).first()
        if emp_user:
            if emp_user.password == request.form['emp_pw']:
                login_user(emp_user)
                return render_template('index.html')
            else:
                return render_template('login.html', incorrect_pw=True)
        else:
            return render_template('login.html', incorrect_user=True)
    else:
        return render_template('login.html')


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
                slist.append(EmpData.query.filter_by(id=info).first())
        else:
            for info in searchname:
                slist.append(EmpData.query.filter_by(name=info).first())
        return render_template('search.html', search_emp=slist,flag=1)
    else:
        return render_template('search.html',flag=0)

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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('login.html',logout_successful=True)

if __name__ == "__main__":
    app.run(debug=True)