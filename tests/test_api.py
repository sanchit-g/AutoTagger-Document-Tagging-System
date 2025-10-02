"""
Basic API tests for AutoTagger
"""
import pytest
import json
import io
from pathlib import Path

from app import create_app, db
from app.models import Document, Tag

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return """
    Machine learning is a subset of artificial intelligence that focuses on 
    developing algorithms that enable computers to learn from data. Companies 
    like Google, Microsoft, and Amazon are investing heavily in AI research. 
    Natural language processing is a key area of machine learning that deals 
    with text and speech understanding.
    """

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_upload_document(client, sample_text):
    """Test document upload"""
    # Create a test file
    data = {
        'file': (io.BytesIO(sample_text.encode('utf-8')), 'test.txt')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'document' in data
    assert 'tags' in data
    assert data['document']['processed'] is True
    assert len(data['tags']) > 0

def test_get_documents(client, sample_text):
    """Test getting all documents"""
    # First upload a document
    data = {
        'file': (io.BytesIO(sample_text.encode('utf-8')), 'test.txt')
    }
    client.post('/api/documents/upload', data=data, content_type='multipart/form-data')
    
    # Get all documents
    response = client.get('/api/documents')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'documents' in data
    assert len(data['documents']) > 0

def test_get_specific_document(client, sample_text):
    """Test getting specific document"""
    # Upload a document
    data = {
        'file': (io.BytesIO(sample_text.encode('utf-8')), 'test.txt')
    }
    upload_response = client.post(
        '/api/documents/upload',
        data=data,
        content_type='multipart/form-data'
    )
    doc_id = json.loads(upload_response.data)['document']['id']
    
    # Get specific document
    response = client.get(f'/api/documents/{doc_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == doc_id
    assert 'tags' in data

def test_update_tags(client, sample_text):
    """Test updating document tags"""
    # Upload a document
    data = {
        'file': (io.BytesIO(sample_text.encode('utf-8')), 'test.txt')
    }
    upload_response = client.post(
        '/api/documents/upload',
        data=data,
        content_type='multipart/form-data'
    )
    doc_id = json.loads(upload_response.data)['document']['id']
    
    # Add custom tags
    update_data = {
        'add_tags': [
            {'tag_name': 'important', 'tag_type': 'custom'},
            {'tag_name': 'review', 'tag_type': 'custom'}
        ]
    }
    
    response = client.put(
        f'/api/documents/{doc_id}/tags',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['added'] == 2

def test_delete_document(client, sample_text):
    """Test deleting document"""
    # Upload a document
    data = {
        'file': (io.BytesIO(sample_text.encode('utf-8')), 'test.txt')
    }
    upload_response = client.post(
        '/api/documents/upload',
        data=data,
        content_type='multipart/form-data'
    )
    doc_id = json.loads(upload_response.data)['document']['id']
    
    # Delete document
    response = client.delete(f'/api/documents/{doc_id}')
    assert response.status_code == 200
    
    # Verify document is deleted
    response = client.get(f'/api/documents/{doc_id}')
    assert response.status_code == 404

def test_get_tags(client, sample_text):
    """Test getting all tags"""
    # Upload a document
    data = {
        'file': (io.BytesIO(sample_text.encode('utf-8')), 'test.txt')
    }
    client.post('/api/documents/upload', data=data, content_type='multipart/form-data')
    
    # Get all tags
    response = client.get('/api/tags')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'tags' in data
    assert 'summary' in data

def test_invalid_file_type(client):
    """Test uploading invalid file type"""
    data = {
        'file': (io.BytesIO(b'test'), 'test.exe')
    }
    
    response = client.post(
        '/api/documents/upload',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400

def test_no_file_uploaded(client):
    """Test upload without file"""
    response = client.post('/api/documents/upload')
    assert response.status_code == 400