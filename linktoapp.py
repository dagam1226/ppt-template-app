# app.py
# This script creates a simple web server using Flask.
# It defines an endpoint to receive the files, calls the processing engine,
# and sends the cleaned file back for download.

import os
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from main_processor import process_presentation # Imports our engine

# Initialize the Flask application
app = Flask(__name__)

# Define a folder to temporarily store uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # A simple route to confirm the server is running
    return "PowerPoint Processor is running."

@app.route('/upload', methods=['POST'])
def upload_files():
    """
    This is the main endpoint that the front-end will call.
    It handles the file upload, processing, and download.
    """
    try:
        # Check if the post request has the file parts
        if 'template' not in request.files or 'source' not in request.files:
            return jsonify({"error": "Missing template or source file"}), 400

        template_file = request.files['template']
        source_file = request.files['source']

        # If the user does not select a file, the browser submits an empty file without a filename.
        if template_file.filename == '' or source_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Securely save the uploaded files
        template_filename = secure_filename(template_file.filename)
        source_filename = secure_filename(source_file.filename)
        
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)
        source_path = os.path.join(app.config['UPLOAD_FOLDER'], source_filename)
        
        template_file.save(template_path)
        source_file.save(source_path)

        # Define the output path for the cleaned file
        output_filename = f"cleaned_{source_filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # --- Call the Processing Engine ---
        success = process_presentation(template_path, source_path, output_path)

        if not success:
            return jsonify({"error": "Failed to process the presentation."}), 500

        # --- Send the Cleaned File Back for Download ---
        return send_file(output_path, as_attachment=True, download_name=output_filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This allows the app to be run by Gunicorn on Heroku
if __name__ == '__main__':
    app.run(debug=True)
