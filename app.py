from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from skill_extractor import SkillExtractor  
from datetime import datetime

app = Flask(__name__)
extractor = SkillExtractor(gpu=False)  # Set to True if you have GPU

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/extract-skills', methods=['POST'])  # Fixed typo in route
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
                
            return jsonify({
                'status': 'success',
                'skills': skills,
                'extracted_text': extracted_text
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400
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

if __name__ == '__main__':
    print("⏳ Starting Flask server...")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
    print("🚀 Flask server is running!")