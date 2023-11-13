from flask import *
from flask_wtf import FlaskForm
from sql import add_user, is_username_taken, check_user, get_by_id
from wtforms import StringField, PasswordField, SubmitField,TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_caching import Cache
from flask_mail import *
from Database import *
import os
from werkzeug.utils import secure_filename
from flask_babel import Babel


app = Flask(__name__)

app.secret_key = 'upasana12345'


babel = Babel(app)

def get_locale():
    user_language = request.args.get('lang', 'en')

    if user_language not in app.config['LANGUAGES']:
        user_language = 'en'
    return user_language

babel.init_app(app, locale_selector=get_locale)
#config languages
app.config['LANGUAGES'] = {
    'en' : 'English',
    'fr' : 'French',
    'es' : 'Spanish',
}

#Sample translations
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

#configure flask mail

app.config['MAIL_SERVER']='smtp.gmail.com'  
app.config['MAIL_PORT']=465  
app.config['MAIL_USERNAME'] = 'sharmaupasana823@gmail.com'  
app.config['MAIL_PASSWORD'] = 'xkkzgbuvozqhrhmf'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  

mail = Mail(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#configuring the Cache data
cache=Cache(app,config={'CACHE_TYPE': 'simple'}) #setting up the cache for the website

# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

# @app.before_request
# def log_request_info():
#     logging.info('Request Method : %s', request.method)
#     logging.info('Request url : %s', request.url)
#     logging.info('Request Headers : %s', dict(request.headers))
#     logging.info('Request Data : %s', request.data)

# @app.after_request
# def log_response_info(response):
#     logging.info('Response Status: %s', response.status)
#     logging.info('Request Headers : %s', dict(request.headers))
#     return response

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators= [DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),
                                                                     EqualTo('password')])
    submit = SubmitField('Sign Up')
    def validate_username(form, field):
        if is_username_taken(field.data):
            print("error")
            raise ValidationError('Username already taken')

class loginForm(FlaskForm):
    email = StringField('Email', validators= [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class User(UserMixin):
    def __init__(self, id, username, email, password):
         self.id = id
         self.username = username
         self.email = email
         self.password = password
         self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.id   



login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    data = get_by_id(user_id)
    if data is not None and len(data) >= 4:
        return User(data[0], data[1], data[2], data[3])
    else:
        return None  # Return None to indicate that the user couldn't be loaded



@app.route('/register', methods= ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        add_user(username, email, password)
        return redirect('/login')
    return render_template('register.html', form= form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = check_user(email)
        Us = load_user(user[0]) 

        if email == Us.email and password == Us.password:
            session_key = f'user{email}'
            session_data = {'email': email, 'password': password}
            cache.set(session_key, session_data, timeout=3600)
            login_user(Us)
            Us.authenticated = True
            flash("Successfully logged in")
            return redirect(url_for('recepieNama'))
        else:
            flash('Login Failed. Invalid Credentials')
    return render_template('login.html', form=form)

@app.route('/', methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/receipes', methods=['GET','POST'])
def recepieNama():
    selected_language = request.args.get('lang','en')
    recipes = get_recipes()
    print(recipes)
    return render_template(f'recipes_{selected_language}.html', recipes = recipes)

@app.route('/receipes/post', methods=['POST'])
def post_receipes():
    # post it into the database
    title = request.form.get('recipeName')
    ingredients = request.form.get('ingredients')
    recipe = request.form.get('details')
    author = current_user.username
    images = request.files.get('recipeImage')


    # grid fs for pictures/ saving it in the database
    media_id = fs.put(images, filename=images.filename)
    add_recipes(title, ingredients, recipe, author, media_id)

    # saving to server
    if images:
        target_folder = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username, title)
        os.makedirs(target_folder, exist_ok=True)
        image_path = os.path.abspath(os.path.join(target_folder, secure_filename(images.filename)))
        print('saved')
        images.save(image_path)

    # confirmation mail about the posting of recipe
    email = current_user.email
    msg = Message('Recipe Posted', sender='no_reply@app.com', recipients=[email])
    msg.body = f'Thank you for posting your recipe "{title}"!'
    mail.send(msg)

    flash('Recipe posted successfully!')
    return redirect(url_for('recepieNama'))
   
@app.route('/get_media/<media_id>')   
def get_media(media_id):
    media = fs.get(ObjectId(media_id))
    return send_file(BytesIO(media.read()), mimetype='image/jpeg')

@app.route('/recipe/view/<id>', methods=['GET', 'POST'])
def recipe_details(id):
    recipe = get_recipe_this(id)
    return render_template('recipe_detail.html', recipe = recipe[0])

@app.route('/receipes/edit/<id>', methods=['GET', 'POST'])
def receipes_edit(id):
    pass
@app.route('/receipes/delete/<id>', methods=['GET', 'POST'])
def delete_receipes():
    pass



@app.teardown_appcontext
def close_connection(exception): 
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)