def handle_attachment_upload(new_case, attachment_file):
    """Handle file upload and create attachment record"""
    try:
        # Create a secure filename
        filename = secure_filename(attachment_file.filename)
        
        # Create the uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'legal_cases', str(new_case.id))
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save the file
        attachment_file.save(file_path)
        
        # Get file type
        file_type = attachment_file.content_type
        
        # Create attachment record with only the existing columns
        attachment = LegalCaseAttachment(
            legal_case_id=new_case.id,
            file_name=unique_filename,  # Use the unique filename
            file_path=file_path,
            file_type=file_type
        )
        db.session.add(attachment)
        db.session.commit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving attachment: {str(e)}")
        db.session.rollback()
        return False
