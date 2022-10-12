
from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user,current_user,LoginManager,UserMixin,logout_user

app = Flask(__name__)
app.config['SECRET_KEY']='super secret key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(30),unique=True,nullable=False)
    phoneNumber=db.Column(db.String(10),nullable=False)
    password=db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return f"User('{self.name}','{self.email}','{self.phoneNumber}')"





@app.route("/home")
def home():
    if current_user.is_authenticated:
     posts=User.query.all()
     return render_template('home.html',posts=posts,title="Home")
    else:
     return render_template('Display.html',title="Display")
@app.route("/signIn",methods=['GET'])
def signInInitial():
    if current_user.is_authenticated:
        return redirect(url_for("welcome"))
    return render_template('SignIn.html',title="SignIn")

@app.route("/signIn/<info>/<category>",methods=['GET'])
def signIn(info,category):
    if current_user.is_authenticated:
        return redirect(url_for("welcome"))
    if info:
     return render_template('SignIn.html',title="SignIn",message=info,category=category)

@app.route("/")
@app.route('/register',methods=['GET'])
def Newregister():
    if current_user.is_authenticated:
       return redirect(url_for("welcome"))
    return render_template('Register.html',title="Register")

@app.route("/register/<message>",methods=['GET'])
def register(message):
    if current_user.is_authenticated:
       return redirect(url_for("welcome"))
    if message :
     return render_template('Register.html',title="Register",message=message)
@app.route("/display",methods=['POST'])
def display():
    if current_user.is_authenticated:
        return redirect(url_for("welcome"))
    if(request.method == 'POST'):
        if(request.form['password'] != request.form['ConfirmPassword']):
            return redirect(url_for('register',message='Password does not match'))
        else:
        #  return render_template('Display.html',title="Display",RegisteredDetails=Details)
         hashed_password=bcrypt.generate_password_hash(request.form['password']).decode('utf8')
         user=User(name=request.form['name'],email=request.form['email'],phoneNumber=request.form['phoneNumber'],password=hashed_password)
         db.session.add(user)
         db.session.commit()
         return redirect(url_for('signIn',info='User Created successfully!!!',category='success'))
@app.route('/welcome',methods=['POST','GET'])
def welcome():
    if(request.method == 'GET'):
        if current_user.is_authenticated:
         return render_template('Display.html',title="Display",RegisteredDetails=current_user)
        else:
            return render_template('Display.html',title="Display")
    if(request.method == 'POST'):
        details= User.query.filter_by(email=request.form['email']).first()
        if details and bcrypt.check_password_hash(details.password,request.form['password']):
           login_user(details,remember=True)
           return render_template('Display.html',title="Display",RegisteredDetails=details)
        else:
            return redirect(url_for('signIn',info='Invalid credentials',category='danger'))

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
     logout_user()
     return redirect(url_for('Newregister'))
    else:
        return render_template('Display.html',title="Display")

@app.route('/delete/<id>')
def delete(id):
    if current_user.is_authenticated:
     if id:
      User.query.filter(User.id == id).delete()
      db.session.commit()
      return redirect(url_for('home'))
    else :
        return render_template('Display.html',title="Display")

@app.route('/update/<id>')
def update(id):
    if current_user.is_authenticated:
     user=User.query.filter(User.id == id).first()
     return render_template('Update.html',title='Update',user=user)
    else :
     return render_template('Display.html',title="Display")
@app.route('/editDetails/<id>',methods=['POST'])
def editDetails(id):
    if request.method == 'POST':
     if current_user.is_authenticated:
        user=User.query.filter(User.id == id).first()
        if request.form['password'] == request.form['ConfirmPassword']:
         if user.name != request.form['name']:
            user.name=request.form['name']
         if user.email != request.form['email']:
            user.email=request.form['email']
         if user.phoneNumber != request.form['phoneNumber']:
            user.phoneNumber=request.form['phoneNumber']
         if user.password != request.form['password']:
            print(request.form['password'])
            hashed_password=bcrypt.generate_password_hash(request.form['password']).decode('utf8')
            user.password=hashed_password
         db.session.commit()
         return redirect(url_for('home'))
        else :
          return render_template('Update.html',title='Update',user=user,message='password does not match')
     else :
      return render_template('Display.html',title="Display")      
if __name__ == "__main__":  
    app.run(debug=True)