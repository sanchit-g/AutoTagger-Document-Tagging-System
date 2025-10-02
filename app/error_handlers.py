"""
Error handlers and validation utilities
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors"""
        logger.warning(f"Bad request: {error}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle method not allowed errors"""
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL'
        }), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file too large errors"""
        return jsonify({
            'error': 'File Too Large',
            'message': f'File size exceeds maximum allowed size of {app.config["MAX_CONTENT_LENGTH"] / (1024*1024):.0f}MB'
        }), 413
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle internal server errors"""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other exceptions"""
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error
        
        # Log the error
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        
        # Return generic error response
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_file_upload(file, allowed_extensions, max_size=None):
    """
    Validate uploaded file
    
    Args:
        file: Flask file object
        allowed_extensions: Set of allowed extensions
        max_size: Maximum file size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check extension
    if '.' not in file.filename:
        return False, "File has no extension"
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check file size if max_size provided
    if max_size:
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > max_size:
            return False, f"File size exceeds maximum of {max_size / (1024*1024):.0f}MB"
    
    return True, None

def validate_tag_data(data):
    """
    Validate tag data for updates
    
    Args:
        data: Dictionary with tag data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Invalid data format"
    
    # Validate add_tags if present
    if 'add_tags' in data:
        if not isinstance(data['add_tags'], list):
            return False, "'add_tags' must be a list"
        
        for tag in data['add_tags']:
            if not isinstance(tag, dict):
                return False, "Each tag in 'add_tags' must be a dictionary"
            
            if 'tag_name' not in tag:
                return False, "Each tag must have 'tag_name'"
            
            if not isinstance(tag['tag_name'], str) or not tag['tag_name'].strip():
                return False, "'tag_name' must be a non-empty string"
            
            if 'tag_type' in tag and tag['tag_type'] not in ['keyword', 'entity', 'custom']:
                return False, "'tag_type' must be 'keyword', 'entity', or 'custom'"
    
    # Validate remove_tag_ids if present
    if 'remove_tag_ids' in data:
        if not isinstance(data['remove_tag_ids'], list):
            return False, "'remove_tag_ids' must be a list"
        
        for tag_id in data['remove_tag_ids']:
            if not isinstance(tag_id, int) or tag_id <= 0:
                return False, "Each tag ID must be a positive integer"
    
    # Must have at least one operation
    if 'add_tags' not in data and 'remove_tag_ids' not in data:
        return False, "Must provide either 'add_tags' or 'remove_tag_ids'"
    
    return True, None

def validate_pagination_params(page, per_page, max_per_page=100):
    """
    Validate pagination parameters
    
    Args:
        page: Page number
        per_page: Results per page
        max_per_page: Maximum allowed per_page value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if page < 1:
        return False, "Page number must be >= 1"
    
    if per_page < 1:
        return False, "Per page value must be >= 1"
    
    if per_page > max_per_page:
        return False, f"Per page value cannot exceed {max_per_page}"
    
    return True, None

def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove potentially dangerous characters
    dangerous_chars = ['..', '~', '$', '&', '|', ';', '`', '<', '>']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    
    return filename