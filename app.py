from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from skill_extractor import SkillExtractor
from pymongo import MongoClient
from dotenv import load_dotenv

# === Load env variables ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# === Initialize Flask App ===
app = Flask(__name__)
extractor = SkillExtractor(gpu=False)

# === Upload Configuration ===
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Connect to MongoDB ===
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')  # Check connection
    print("✅ Connected to MongoDB Atlas")
    db = mongo_client["jobfinder"]
    skills_collection = db["extracted_skills"]
except Exception as e:
    print("❌ MongoDB connection error:", e)
    mongo_client = None

# === Helper Functions ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Routes ===

@app.route('/')
def home():
    return """
    <h1>Resume Skill Extractor</h1>
    <p>POST resume images to /extract-skills</p>
    <form action="/extract-skills" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    """

@app.route('/extract-skills', methods=['POST'])
def extract_skills():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            skills, extracted_text = extractor.process_resume_image(filepath)

            if os.path.exists(filepath):
                os.remove(filepath)

            # Store result in MongoDB
            if mongo_client:
                skills_collection.insert_one({
                    "skills": skills,
                    "extracted_text": extracted_text,
                    "uploaded_at": datetime.utcnow()
                })

            return jsonify({
                'status': 'success',
                'skills': skills,
                'extracted_text': extracted_text
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/results', methods=['GET'])
def get_results():
    if not mongo_client:
        return jsonify({"error": "MongoDB not connected"}), 500

    results = list(skills_collection.find({}, {'_id': 0}))
    return jsonify(results)

# === Run the app ===
if __name__ == '__main__':
    print("⏳ Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
    print("🚀 Flask server is running!")
