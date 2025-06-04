from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re
import os
import cv2
import numpy as np
import tensorflow as tf, keras
from keras import backend as K
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Clear Keras session
K.clear_session()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

# Custom F1 Score metric
class F1Score(tf.keras.metrics.Metric):
    def __init__(self, name='f1_score', **kwargs):
        super().__init__(name=name, **kwargs)
        self.precision = tf.keras.metrics.Precision()
        self.recall = tf.keras.metrics.Recall()

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.precision.update_state(y_true, y_pred)
        self.recall.update_state(y_true, y_pred)

    def result(self):
        p = self.precision.result()
        r = self.recall.result()
        return 2 * ((p * r) / (p + r + K.epsilon()))

    def reset_states(self):
        self.precision.reset_states()
        self.recall.reset_states()

# Load pre-trained model
Loaded_model = keras.models.load_model(
    'Google_Colab_my_deepfake_model_with_fine_tuning_04_April_part2.keras',
    custom_objects={'F1Score': F1Score},
    compile=False
)

# Image preprocessing function
def preprocess_image(image_path, target_size=(224, 224)):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Error: Unable to load image at {image_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, target_size)
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# # Manual prediction check (can be removed in production)
# image_path4 = 'uploads/Fake_00KEKJJ1Q4.jpg'
# input_image4 = preprocess_image(image_path4)
# prediction4 = Loaded_model.predict(input_image4)
# threshold = 0.6
# if prediction4[0][0] < threshold:
#     print("Manual Prediction: Fake")
# else:
#     print("Manual Prediction: Real")
# print(f"Manual Confidence Score: {prediction4[0][0]:.4f}")

# MongoDB connection using environment variable
client = MongoClient(os.environ['MONGODB_URI'])
db = client.get_database('DeepfakeDB')

# Upload config
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/deepfake-checker", methods=['GET', 'POST'])
def deepfake_checker():
    if 'user_id' not in session:
        flash('Please sign in to access the Deepfake Checker', 'error')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                input_image = preprocess_image(file_path)
                prediction = Loaded_model.predict(input_image)
                confidence = prediction[0][0]
                threshold = 0.6

                if confidence >= threshold:
                    result = 'Real'
                    confidence_display = confidence
                else:
                    result = 'Fake'
                    confidence_display = 1 - confidence

                confidence_percent = f"{confidence_display * 100:.2f}%"
                return render_template("deepfake_checker.html",
                                       prediction=result,
                                       confidence=confidence_percent,
                                       filename=filename)

            except Exception as e:
                flash('Error processing image. Please try another file.', 'error')
                app.logger.error(f"Error: {str(e)}")
                return redirect(request.url)

        else:
            flash('Allowed file types: png, jpg, jpeg', 'error')
            return redirect(request.url)

    return render_template("deepfake_checker.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if not all([name, email, phone, password]):
            flash('All fields are required', 'error')
            return render_template('signup.html')

        cleaned_phone = re.sub(r'\D', '', phone)
        if not cleaned_phone.startswith('05') or len(cleaned_phone) != 10:
            flash('Invalid UAE phone number format (05X-XXX-XXXX)', 'error')
            return render_template('signup.html')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address', 'error')
            return render_template('signup.html')

        if db.users.find_one({'$or': [{'email': email}, {'phone': cleaned_phone}]}):
            flash('Email or phone already registered', 'error')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)
        new_user = {
            'name': name,
            'email': email,
            'phone': cleaned_phone,
            'password': hashed_password,
            'created_at': datetime.now()
        }

        try:
            db.users.insert_one(new_user)
            flash('Registration successful! Please sign in', 'success')
            return redirect(url_for('signin'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
            return render_template('signup.html')

    return render_template("signup.html")

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill all fields', 'error')
            return render_template('signin.html')

        user = db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash('Signed in successfully', 'success')
            return redirect(url_for('index'))

        flash('Invalid credentials', 'error')
        return render_template('signin.html')

    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
