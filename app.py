from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import session
from bson.objectid import ObjectId
from flask_login import UserMixin
from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
import uuid
from data_analysis import perform_data_analysis




app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Grad'
mongo = PyMongo(app)
login_manager = LoginManager(app)

users_collection = mongo.db.Users
form_collection = mongo.db.FormResponses
form_response_collection = mongo.db.Form_response


class User(UserMixin):
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        user_obj = User()
        user_obj.id = str(user['_id'])
        user_obj.username = user['username']  # Add username to the user object
        return user_obj
    return None
@app.route('/view_form/<form_id>', methods=['GET', 'POST'])
def view_form_page(form_id):
    form = form_collection.find_one({'_id': ObjectId(form_id)})
    if form:
        if 'form_data' in form:
            # Structure 2
            form_data = {
                'form_id': str(form['_id']),
                'title': form['form_data'].get('title'),
                'questions': form['form_data'].get('questions', [])
            }
        else:
            # Structure 1
            form_data = {
                '_id': str(form['_id']),
                'title': form.get('title'),
                'questions': form.get('questions', [])
            }
        return render_template('view_form.html', form_data=form_data)
    else:
        flash('Form not found', 'error')
        return redirect(url_for('index'))
    


@app.route('/data_analysis')
@login_required
def data_analysis():
    # Trigger data analysis
    perform_data_analysis()

    # Render template or return response as needed
    return render_template('data_analysis.html')









@app.route('/respond/<form_id>')
def view_form_for_response(form_id):
    # Retrieve form details from the database using the form_id
    form = form_collection.find_one({'_id': ObjectId(form_id)})
    if form:
        # Render the view form page with the retrieved form details
        return render_template('view_form.html', form=form)
    else:
        # Handle case where form with the given form_id does not exist
        flash('Form not found', 'error')
        return redirect(url_for('index'))
    





@app.route('/submit-form', methods=['POST'])
def submit_form():
    form_id = request.form['form_id']
    form_data = request.form

    # Save the form data to MongoDB
    form_collection.insert_one({
        'form_id': form_id,
        'form_data': form_data
    })

    return jsonify({'message': 'Form submitted successfully.'})    




# Home page
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/save_form', methods=['POST'])
def save_form():
    form_data = request.json

    # Generate a unique identifier for the form
    form_id = str(uuid.uuid4())

    # Store the form data in the database along with the unique identifier
    mongo.db.FormResponses.insert_one({'form_id': form_id, 'form_data': form_data})

    # Return the custom link to the frontend
    custom_link = f'/respond/{form_id}'
    return jsonify({"message": "Form saved successfully", "custom_link": custom_link})

# Route to render the form for users to respond to
@app.route('/respond/<form_id>', methods=['POST'])
def respond_to_form(form_id):
    data = request.json  # Parse JSON data from request

    responses = []

    for key, value in data.items():
        # Extract question number from key
        question_number = key.replace('question', '')
        
        # Retrieve question title from form_data in the database
        form_data = form_collection.find_one({'_id': ObjectId(form_id)})['form_data']
        question = form_data['questions'][int(question_number)]['title']

        # Append question and user's answer to responses list
        responses.append({'question': question, 'answer': value})

    # Save the responses to MongoDB
    form_response_collection.insert_one({
        'form_id': form_id,
        'responses': responses
    })

    return jsonify({'message': 'Form submitted successfully.'})
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form['Email']
        password = request.form['password']

        user = users_collection.find_one({'email': Email, 'password': password})
        if user:
            # Create a User object for Flask-Login
            user_obj = User()
            user_obj.id = str(user['_id'])

            # Log in the user using Flask-Login
            login_user(user_obj)

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login_page.html')
# Dashboard page
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated and 'email' in session:
        # Fetch forms from MongoDB
        forms = form_collection.find()
        return render_template('dashboard.html', forms=forms)  # Pass forms to the template
    else:
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))

def get_form_data_from_database(form_id):
    # Assuming you're using MongoDB with PyMongo
    form_data = form_collection.find_one({'_id': ObjectId(form_id)})
    return form_data

@app.route('/view_form/<form_id>')
def view_form(form_id):
    # Fetch form data from the database based on the form_id
    form_data = get_form_data_from_database(form_id)  # Replace with your actual implementation

    if form_data:
        return render_template('view_form.html', form_data=form_data)
    else:
        flash('Form not found', 'error')
        return redirect(url_for('dashboard'))
#forms page
@app.route('/forms', methods=['GET', 'POST'])
@login_required
def forms():
    if current_user.is_authenticated and 'email' in session:
        return render_template('forms.html')
    else:
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))



# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['Email']  # 'Email' should be lowercase
        password = request.form['password']
        confirm_password = request.form['confirmPassword']  # 'confirmPassword' is the name of the input field

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already exists!', 'error')
        else:
            user_id = users_collection.insert_one({'username': username, 'email': email, 'password': password}).inserted_id
            user_obj = User()
            user_obj.id = str(user_id)
            login_user(user_obj)
            flash('Signup successful!', 'success')
            return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/analysis')
@login_required
def analysis():
    # Perform data analysis
    perform_data_analysis()

    # Fetch analysis results from the database
    analysis_results = get_analysis_results_from_database()  # Implement this function to fetch analysis results from the database

    if current_user.is_authenticated and 'email' in session:
        # Fetch forms from MongoDB
        forms = form_collection.find()
        return render_template('analysis.html', forms=forms, analysis_results=analysis_results)
    else:
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
def get_analysis_results_from_database():
    # Assuming you're using MongoDB with PyMongo
    analysis_results = form_response_collection.find_one({'analysis_results': {'$exists': True}})
    return analysis_results

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
