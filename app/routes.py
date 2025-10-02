"""
REST API Routes for AutoTagger
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import func
import logging
import time
from pathlib import Path

from app import db
from app.models import Document, Tag
from app.nlp_processor import NLPProcessor
from app.file_handler import FileHandler

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Initialize NLP processor (lazy loading)
_nlp_processor = None

def get_nlp_processor():
    """Get or create NLP processor instance"""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = NLPProcessor(
            max_keywords=current_app.config['MAX_KEYWORDS'],
            min_keyword_length=current_app.config['MIN_KEYWORD_LENGTH']
        )
    return _nlp_processor

def get_file_handler():
    """Get file handler instance"""
    return FileHandler(
        upload_folder=current_app.config['UPLOAD_FOLDER'],
        allowed_extensions=current_app.config['ALLOWED_EXTENSIONS']
    )

@api_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    """
    Upload a document and automatically generate tags
    
    Returns:
        JSON response with document details and extracted tags
    """
    start_time = time.time()
    
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Save file
        file_handler = get_file_handler()
        success, message, filepath = file_handler.save_file(file, filename)
        
        if not success:
            return jsonify({'error': message}), 400
        
        # Extract text content
        success, message, content = file_handler.extract_text(filepath)
        
        if not success:
            file_handler.delete_file(filepath)
            return jsonify({'error': message}), 400
        
        # Get file info
        file_size = filepath.stat().st_size
        file_type = filepath.suffix[1:].lower()
        
        # Create document record
        document = Document(
            filename=filename,
            content=content,
            file_size=file_size,
            file_type=file_type,
            processed=False
        )
        db.session.add(document)
        db.session.flush()  # Get document ID
        
        # Extract tags using NLP
        nlp_processor = get_nlp_processor()
        tags_data = nlp_processor.extract_all_tags(content)
        
        # Save tags to database
        all_tags = []
        
        # Save keywords
        for tag_info in tags_data['keywords']:
            tag = Tag(
                document_id=document.id,
                tag_name=tag_info['tag_name'],
                tag_type=tag_info['tag_type'],
                confidence_score=tag_info['confidence_score']
            )
            db.session.add(tag)
            all_tags.append(tag)
        
        # Save entities
        for tag_info in tags_data['entities']:
            tag = Tag(
                document_id=document.id,
                tag_name=tag_info['tag_name'],
                tag_type=tag_info['tag_type'],
                confidence_score=tag_info['confidence_score'],
                entity_type=tag_info.get('entity_type')
            )
            db.session.add(tag)
            all_tags.append(tag)
        
        # Mark document as processed
        document.processed = True
        db.session.commit()
        
        processing_time = time.time() - start_time
        
        logger.info(f"Document {document.id} processed in {processing_time:.2f}s with {len(all_tags)} tags")
        
        return jsonify({
            'message': 'Document uploaded and processed successfully',
            'document': document.to_dict(),
            'tags': [tag.to_dict() for tag in all_tags],
            'processing_time': round(processing_time, 2),
            'tag_summary': {
                'keywords': len(tags_data['keywords']),
                'entities': len(tags_data['entities']),
                'total': len(all_tags)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error uploading document: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_bp.route('/documents', methods=['GET'])
def get_documents():
    """
    Get all documents with their tags
    
    Query parameters:
        - page: Page number (default: 1)
        - per_page: Results per page (default: 20)
        - processed: Filter by processing status (true/false)
    
    Returns:
        JSON response with list of documents
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', current_app.config['RESULTS_PER_PAGE'], type=int)
        processed_filter = request.args.get('processed', type=str)
        
        # Build query
        query = Document.query
        
        if processed_filter:
            query = query.filter_by(processed=(processed_filter.lower() == 'true'))
        
        # Paginate
        pagination = query.order_by(Document.upload_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        documents = []
        for doc in pagination.items:
            doc_dict = doc.to_dict()
            doc_dict['tags'] = [tag.to_dict() for tag in doc.tags.all()]
            documents.append(doc_dict)
        
        return jsonify({
            'documents': documents,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total_pages': pagination.pages,
                'total_documents': pagination.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """
    Get specific document details with tags
    
    Args:
        doc_id: Document ID
    
    Query parameters:
        - include_content: Include full document content (true/false, default: false)
    
    Returns:
        JSON response with document details
    """
    try:
        document = Document.query.get_or_404(doc_id)
        
        include_content = request.args.get('include_content', 'false').lower() == 'true'
        
        doc_dict = document.to_dict(include_content=include_content)
        doc_dict['tags'] = [tag.to_dict() for tag in document.tags.all()]
        
        # Group tags by type
        doc_dict['tags_by_type'] = {
            'keywords': [tag.to_dict() for tag in document.tags.filter_by(tag_type='keyword').all()],
            'entities': [tag.to_dict() for tag in document.tags.filter_by(tag_type='entity').all()],
            'custom': [tag.to_dict() for tag in document.tags.filter_by(tag_type='custom').all()]
        }
        
        return jsonify(doc_dict), 200
        
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_bp.route('/documents/<int:doc_id>/tags', methods=['PUT'])
def update_document_tags(doc_id):
    """
    Update/modify tags for a document
    
    Args:
        doc_id: Document ID
    
    Request body:
        {
            "add_tags": [{"tag_name": "tag1", "tag_type": "custom"}],
            "remove_tag_ids": [1, 2, 3]
        }
    
    Returns:
        JSON response with updated tags
    """
    try:
        document = Document.query.get_or_404(doc_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Add new tags
        added_tags = []
        if 'add_tags' in data:
            for tag_data in data['add_tags']:
                if 'tag_name' not in tag_data:
                    continue
                
                tag = Tag(
                    document_id=doc_id,
                    tag_name=tag_data['tag_name'],
                    tag_type=tag_data.get('tag_type', 'custom'),
                    confidence_score=tag_data.get('confidence_score', 1.0),
                    entity_type=tag_data.get('entity_type')
                )
                db.session.add(tag)
                added_tags.append(tag)
        
        # Remove tags
        removed_count = 0
        if 'remove_tag_ids' in data:
            for tag_id in data['remove_tag_ids']:
                tag = Tag.query.filter_by(id=tag_id, document_id=doc_id).first()
                if tag:
                    db.session.delete(tag)
                    removed_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tags updated successfully',
            'added': len(added_tags),
            'removed': removed_count,
            'current_tags': [tag.to_dict() for tag in document.tags.all()]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating tags for document {doc_id}: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """
    Delete a document and its tags
    
    Args:
        doc_id: Document ID
    
    Returns:
        JSON response confirming deletion
    """
    try:
        document = Document.query.get_or_404(doc_id)
        
        # Delete associated file if it exists
        file_handler = get_file_handler()
        filepath = Path(current_app.config['UPLOAD_FOLDER']) / document.filename
        file_handler.delete_file(filepath)
        
        # Delete document (tags will be deleted via cascade)
        db.session.delete(document)
        db.session.commit()
        
        logger.info(f"Document {doc_id} deleted")
        
        return jsonify({
            'message': f'Document {doc_id} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting document {doc_id}: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_bp.route('/documents/<int:doc_id>/similar', methods=['GET'])
def find_similar_documents(doc_id):
    """
    Find similar documents based on content
    
    Args:
        doc_id: Document ID
    
    Query parameters:
        - limit: Maximum number of similar documents (default: 5)
        - threshold: Minimum similarity score (default: 0.3)
    
    Returns:
        JSON response with similar documents
    """
    try:
        document = Document.query.get_or_404(doc_id)
        
        limit = request.args.get('limit', 5, type=int)
        threshold = request.args.get('threshold', 
                                    current_app.config['SIMILARITY_THRESHOLD'], 
                                    type=float)
        
        # Get all other documents
        other_documents = Document.query.filter(
            Document.id != doc_id,
            Document.processed == True
        ).all()
        
        if not other_documents:
            return jsonify({
                'message': 'No other documents to compare',
                'similar_documents': []
            }), 200
        
        # Prepare document contents
        document_contents = [(doc.id, doc.content) for doc in other_documents]
        
        # Find similar documents
        nlp_processor = get_nlp_processor()
        similar_docs = nlp_processor.find_similar_documents(
            document.content,
            document_contents,
            threshold=threshold
        )
        
        # Limit results
        similar_docs = similar_docs[:limit]
        
        # Get document details
        similar_documents = []
        for sim_doc_id, similarity in similar_docs:
            sim_doc = Document.query.get(sim_doc_id)
            doc_dict = sim_doc.to_dict()
            doc_dict['similarity_score'] = round(similarity, 3)
            doc_dict['tags'] = [tag.to_dict() for tag in sim_doc.tags.limit(5).all()]
            similar_documents.append(doc_dict)
        
        return jsonify({
            'document_id': doc_id,
            'similar_documents': similar_documents,
            'count': len(similar_documents)
        }), 200
        
    except Exception as e:
        logger.error(f"Error finding similar documents for {doc_id}: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_bp.route('/tags', methods=['GET'])
def get_all_tags():
    """
    Get all unique tags with document counts
    
    Query parameters:
        - tag_type: Filter by tag type (keyword/entity/custom)
        - min_count: Minimum document count (default: 1)
        - limit: Maximum number of tags to return (default: 100)
    
    Returns:
        JSON response with tag statistics
    """
    try:
        tag_type = request.args.get('tag_type', type=str)
        min_count = request.args.get('min_count', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # Build query for tag statistics
        query = db.session.query(
            Tag.tag_name,
            Tag.tag_type,
            func.count(Tag.document_id).label('document_count'),
            func.avg(Tag.confidence_score).label('avg_confidence')
        ).group_by(Tag.tag_name, Tag.tag_type)
        
        if tag_type:
            query = query.filter(Tag.tag_type == tag_type)
        
        query = query.having(func.count(Tag.document_id) >= min_count)
        query = query.order_by(func.count(Tag.document_id).desc())
        query = query.limit(limit)
        
        results = query.all()
        
        tags = [
            {
                'tag_name': tag_name,
                'tag_type': tag_type,
                'document_count': document_count,
                'avg_confidence': round(avg_confidence, 3)
            }
            for tag_name, tag_type, document_count, avg_confidence in results
        ]
        
        # Get tag type summary
        type_summary = db.session.query(
            Tag.tag_type,
            func.count(func.distinct(Tag.tag_name)).label('unique_tags'),
            func.count(Tag.id).label('total_instances')
        ).group_by(Tag.tag_type).all()
        
        summary = {
            tag_type: {
                'unique_tags': unique_tags,
                'total_instances': total_instances
            }
            for tag_type, unique_tags, total_instances in type_summary
        }
        
        return jsonify({
            'tags': tags,
            'summary': summary,
            'total_unique_tags': len(tags)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AutoTagger API'
    }), 200