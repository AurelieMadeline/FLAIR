from flask import Flask, render_template, redirect, request, flash, session, url_for, send_from_directory
import model, os
from werkzeug import secure_filename

UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = set(['png','jpg', 'jpeg'])

app = Flask(__name__)
app.secret_key ="ABC"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("test.html")

@app.route("/login")
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
        return redirect(url_for("signup_form"))

    # check for email
    u = model.session.query(model.User).filter(model.User.email==email).first()

    # if exists, ask if they want to login
    if u:
        flash("User already exists! Please, login.")
        return redirect(url_for("login_form"))
    # if doesn't exist, add user info to database as new user
    else:
        u = model.User()
        u.username = username
        u.email = email
        u.password = password # hash later?
       
        # how do we turn location into an id?
        l= model.session.query(model.Location).filter_by(location_name=location).first()
        if not l:
            l=model.Location()
            l.location_name=location
            model.session.add(l)
            model.session.commit()

        u.location_id=l.id

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
        return redirect("/login")

@app.route("/logout")
def user_logout():
    session["user_email"] = None
    session["user_id"] = None
    flash("Logout successful")
    print session
    return redirect("/")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():

    #to check if user_id is in session

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            notes = request.form.get("notes")
            style = request.form.get("style")
            brand = request.form.get("brand")
            location = request.form.get("location")
            p=model.Picture()
            p.user_id = session["user_id"]
            p.filename = filename
            p.notes = notes
            p.style = style
            p.brand = brand

            l= model.session.query(model.Location).filter_by(location_name=location).first()
            if not l:
                l=model.Location()
                l.location_name=location
                model.session.add(l)
                model.session.commit()

            p.location_id=l.id

            model.session.add(p)
            model.session.commit()

            return redirect(url_for('success_upload',
                                    filename=filename))
    return render_template ("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/fileview/<filename>")
def success_upload(filename):
    return render_template("preview.html")

if __name__ == "__main__":
    app.run(debug = True)
