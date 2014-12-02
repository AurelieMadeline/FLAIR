from flask import Flask, render_template, redirect, request, flash, session, url_for, send_from_directory
import model, os
from werkzeug import secure_filename


UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = set(['png','jpg', 'jpeg'])

app = Flask(__name__)
app.secret_key ="f\x81*I\x19\xd5\xb3\x98o\x9b\xf7\xd0\x0b\xb0H9\xcb\xd9\xfbH\x02\xfd\xe2\xf9"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=['GET', 'POST'])
def index():
    style = request.form.get("style")
    location = request.form.get("location")
    gender = request.form.get("gender")

    if request.method == 'POST':

        filters = {}
        if gender:
            filters['gender'] = gender
        if style:
            filters['style'] = style
        match = model.session.query(model.Picture).\
            filter_by(**filters)

        if location:
            match = match.join(model.Picture.location, aliased=True).\
                filter_by(location_name=location)

        match = match.all()

        if match==[]:
            flash("Oops, looks like no results found!")
    else:
        match=[]

    return render_template("home.html", match=match)


@app.route("/login")
def login_form():
    user_id=session.get("user_id")
    if user_id:
        return redirect("/profile")
    return render_template("login.html")

@app.route("/signup")
def signup_form():
    user_id=session.get("user_id")
    if user_id:
        return redirect("/profile")
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
        flash("User already exists. Please, login.")
        return redirect(url_for("login_form"))
    # if doesn't exist, add user info to database as new user
    else:
        u = model.User()
        u.username = username
        u.email = email
        u.password = password # hash later?
       
        # how do I turn location into an id?
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


    return redirect("/profile")

@app.route("/login", methods=["POST"])
def user_login():
    email = request.form.get("email")
    password = request.form.get("password")
    u = model.session.query(model.User).filter_by(email = email).filter_by(password = password).first()
    if u:
        flash("Login successful")
        session["user_email"] = u.email
        session["user_id"] = u.id
        print session
        return redirect("/profile")
    else:
        flash("Email or password not valid, please try again.")
        return redirect("/login")

@app.route("/logout")
def user_logout():
    session["user_email"] = None
    session["user_id"] = None
    flash("You are successfully logged out!")
    print session
    return redirect("/login")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            notes = request.form.get("notes")
            style = request.form.get("style")
            location = request.form.get("location")
            gender = request.form.get("gender")
            p=model.Picture()
            p.user_id = session["user_id"]
            p.filename = filename
            p.notes = notes
            p.style = style
            p.gender = gender

            l= model.session.query(model.Location).filter_by(location_name=location).first()
            if not l:
                l=model.Location()
                l.location_name=location
                model.session.add(l)
                model.session.commit()

            p.location_id=l.id

            model.session.add(p)
            model.session.commit()
            
            return redirect(url_for('show_profile',
                                    filename=filename))
    return render_template ("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/picture_view/<int:id>')
def show_single_photo(id):
     pic = model.session.query(model.Picture).get(id)
     return render_template("view_picture.html", pic=pic)

@app.route('/delete/<int:id>', methods=['POST'])
def remove(id):
    pic=model.session.query(model.Picture).get(id)
    print pic
    model.session.delete(pic)
    model.session.commit()
    return redirect(url_for('show_profile'))

@app.route("/profile")
def show_profile():
    user_id=session.get("user_id")
    if user_id==None:
        return redirect ("/login")
    else:
        user_obj= model.session.query(model.User).filter_by(id=session["user_id"]).first()
        pic_id=model.session.query(model.Picture).filter_by(user_id=session["user_id"]).all()
    
    return render_template("profile.html", user=user_obj, pic_id=pic_id)



if __name__ == "__main__":
    app.run(debug = True)

