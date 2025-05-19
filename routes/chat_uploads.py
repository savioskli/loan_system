from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

chat_uploads_bp = Blueprint('chat_uploads', __name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static/uploads/chat')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@chat_uploads_bp.route('/user/upload_chat_image', methods=['POST'])
@login_required
def upload_chat_image():
    """Upload an image for the chat and return its URL"""
    try:
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['image']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            # Create a unique filename to prevent overwriting
            original_filename = secure_filename(file.filename)
            extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{extension}"
            
            # Save the file
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # Return the URL to the saved file
            file_url = f"/static/uploads/chat/{unique_filename}"
            
            current_app.logger.info(f"Chat image uploaded: {file_url} by user {current_user.id}")
            
            return jsonify({
                'success': True,
                'imageUrl': file_url,
                'filename': unique_filename
            })
        else:
            return jsonify({'error': f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error uploading chat image: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

@chat_uploads_bp.route('/user/chat_image/<filename>')
@login_required
def get_chat_image(filename):
    """Serve a chat image file"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        current_app.logger.error(f"Error serving chat image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404
