from flask import Flask, render_template, redirect, request, flash, session, url_for
import model

app = Flask(__name__)
app.secret_key = #secret key goes here

@app.route("/")
def index():
    print "hello, running index"
    return render_template("test.html")
   
@app.route("/login_form")
def login_form():
    return render_template("login.html")

@app.route("/signup")
def signup_form():
    return render_template("signup_form.html")

@app.route("/process_signup", methods=["POST"])
def user_signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    location = request.form.get("location")


    # ERROR CHECKING
    if not email:
        flash("Please enter a valid email address")
        return redirect(url_for("signup_form"))
    if not password:
        flash("Please enter a password")
        return redirect("/signup")

    # check for email
    u = model.session.query(model.User).filter(model.User.email==email).first()

    # if exists, ask if they want to login
    if u:
        flash("User already exists! LOGIN DAMMIT")
        return redirect(url_for("login_form"))
    # if doesn't exist, add user info to database as new user
    else:
        u = model.User()
        u.username = username
        u.email = email
        u.password = password
        u.location = location
        model.session.add(u)
        model.session.commit()
        
        session["user_email"] = u.email
        session["user_id"] = str(u.id)
        print session
        flash("Successfully signed up!")


    return redirect("/")

@app.route("/login", methods=["POST"])
def user_login():
    email = request.form.get("email")
    password = request.form.get("password")
    u = model.session.query(model.User).filter_by(email = email).filter_by(password = password).first()
    if u:
        flash("Login successful")
        session["user_email"] = u.email
        session["user_id"] = str(u.id)
        print session
        return redirect("/")
    else:
        flash("Email/password not valid, please try again.")
        return redirect("/login_form")

@app.route("/logout")
def user_logout():
    session["user_email"] = None
    session["user_id"] = None
    flash("Logout successful")
    print session
    return redirect("/")



if __name__ == "__main__":
    app.run(debug = True)