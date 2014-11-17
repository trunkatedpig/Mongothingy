from flask import Flask,request,redirect,render_template,session,make_response
from pymongo import Connection
from functools import wraps

conn = Connection()
db = conn["swaggy_database"]
users = db["users"]

app=Flask(__name__)


def loggedin():
    return "username" in session and "password" in session and db.users.find({"username": session["username"],"password":session["password"]}).count()==1

def check_login(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if loggedin():
            return f(*args, **kwargs)
        else:
            return render_template("page1.html", loggedin=False,username="")
    return inner

@app.route("/", methods=["GET","POST"])
@app.route("/home", methods=["GET","POST"])
def home():    
    if loggedin():
        return render_template("main.html", loggedin=True,username=session["username"])
    else:
        return render_template("main.html")

@app.route("/login", methods=["GET","POST"])
def login():
    ud = dict(request.form.items() + request.args.items())
    if request.method == "GET":
        if loggedin():
            return render_template("login.html", loggedin=True,username=session["username"])
        else:
            return render_template("login.html")
    else:
        if db.users.find({"username": ud["username"],"password":ud["password"]}).count()==1:
            session["username"] = ud["username"]
            session["password"] = ud["password"]
            return render_template("page1.html",loggedin = True, username = ud["username"])
        else:
            return render_template("login.html", loggedin = False, error = True)

@app.route("/register",methods=["GET","POST"])
def register():
    username = ""
    password = ""
    if "username" in session and "password" in session:
        username = session["username"]
        password = session["password"]

    ud = dict(request.form.items() + request.args.items())
    if request.method=="POST": ##already filled
        if ud["username"]!="" and ud["password"]!="" and ud["password2"]!="":
            if  False: ## username already in database
                ##user taken. red text
                return render_template("register.html",userTaken=True, username = username, loggedin = loggedin())
            elif ud["password"] != ud["password2"]:
                ##different passwords. red text
                return render_template("register.html",diffPass=True, username = username, loggedin = loggedin())
            else:
                ##do db stuff
                newUser = {"username":ud["username"],
                           "password":ud["password"]}
                users.insert(newUser)
                print "lol new user"
                return render_template("redirect.html",target="home",registered=True, username = username, loggedin = loggedin()) 
        else:
            ##not complete. red text.
            return render_template("register.html",notComplete=True, username = username, loggedin = loggedin())
            

    else:
        return render_template("register.html",samePass=True, username = username, loggedin = loggedin())
      
@app.route("/page1", methods=["GET","POST"])
@check_login 
def page1(): 
    return render_template("page1.html",loggedin=True,username=session["username"])

@app.route("/page2", methods=["GET","POST"])
@check_login
def page2():
    ud = dict(request.form.items() + request.args.items())
    if "logout" in ud:
        session["username"] = ""
        session["password"] = ""
        return render_template("page2.html",loggedin=False)

    return render_template("page2.html", loggedin=True,username=session["username"])

 
if __name__=="__main__":
    app.secret_key="b0kun0p1c0c7f"
    app.debug=True
    app.run();
