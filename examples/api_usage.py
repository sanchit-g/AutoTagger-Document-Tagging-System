"""
Example usage of AutoTagger API
Demonstrates how to interact with the API endpoints
"""
import requests
import json
from pathlib import Path

# Base API URL
BASE_URL = "http://localhost:5000/api"

def create_sample_document():
    """Create a sample document for testing"""
    content = """
    Artificial Intelligence and Machine Learning are transforming industries worldwide.
    Companies like Google, Microsoft, and Amazon are leading the AI revolution.
    Natural Language Processing enables computers to understand human language.
    Deep learning models have achieved remarkable success in image recognition and speech synthesis.
    The future of AI includes autonomous vehicles, personalized medicine, and intelligent assistants.
    """
    
    # Save to file
    filepath = Path("sample_document.txt")
    filepath.write_text(content)
    return filepath

def upload_document(filepath):
    """Upload a document to the API"""
    print(f"\n1. Uploading document: {filepath}")
    
    with open(filepath, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/documents/upload", files=files)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✓ Document uploaded successfully!")
        print(f"  - Document ID: {data['document']['id']}")
        print(f"  - Tags extracted: {data['tag_summary']['total']}")
        print(f"  - Processing time: {data['processing_time']}s")
        
        print(f"\n  Top tags:")
        for tag in data['tags'][:5]:
            print(f"    - {tag['tag_name']} ({tag['tag_type']}, confidence: {tag['confidence_score']:.3f})")
        
        return data['document']['id']
    else:
        print(f"✗ Error: {response.json()}")
        return None

def get_all_documents():
    """Get all documents"""
    print(f"\n2. Fetching all documents")
    
    response = requests.get(f"{BASE_URL}/documents")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {len(data['documents'])} document(s)")
        
        for doc in data['documents']:
            print(f"  - ID {doc['id']}: {doc['filename']} ({doc['tag_count']} tags)")
    else:
        print(f"✗ Error: {response.json()}")

def get_document_details(doc_id):
    """Get specific document details"""
    print(f"\n3. Fetching document {doc_id} details")
    
    response = requests.get(f"{BASE_URL}/documents/{doc_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Document details:")
        print(f"  - Filename: {data['filename']}")
        print(f"  - Upload date: {data['upload_date']}")
        print(f"  - Keywords: {len(data['tags_by_type']['keywords'])}")
        print(f"  - Entities: {len(data['tags_by_type']['entities'])}")
    else:
        print(f"✗ Error: {response.json()}")

def add_custom_tags(doc_id):
    """Add custom tags to a document"""
    print(f"\n4. Adding custom tags to document {doc_id}")
    
    payload = {
        'add_tags': [
            {'tag_name': 'important', 'tag_type': 'custom'},
            {'tag_name': 'portfolio', 'tag_type': 'custom'},
            {'tag_name': 'ai-research', 'tag_type': 'custom'}
        ]
    }
    
    response = requests.put(
        f"{BASE_URL}/documents/{doc_id}/tags",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Tags updated successfully!")
        print(f"  - Added: {data['added']}")
        print(f"  - Total tags now: {len(data['current_tags'])}")
    else:
        print(f"✗ Error: {response.json()}")

def find_similar_documents(doc_id):
    """Find similar documents"""
    print(f"\n5. Finding documents similar to {doc_id}")
    
    response = requests.get(
        f"{BASE_URL}/documents/{doc_id}/similar",
        params={'limit': 5, 'threshold': 0.3}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if data['count'] > 0:
            print(f"✓ Found {data['count']} similar document(s):")
            for doc in data['similar_documents']:
                print(f"  - {doc['filename']} (similarity: {doc['similarity_score']:.3f})")
        else:
            print(f"✓ No similar documents found")
    else:
        print(f"✗ Error: {response.json()}")

def get_all_tags():
    """Get all tags with statistics"""
    print(f"\n6. Fetching all tags")
    
    response = requests.get(
        f"{BASE_URL}/tags",
        params={'limit': 10}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Tag statistics:")
        print(f"  - Total unique tags: {data['total_unique_tags']}")
        
        if 'summary' in data:
            for tag_type, stats in data['summary'].items():
                print(f"  - {tag_type}: {stats['unique_tags']} unique, {stats['total_instances']} total")
        
        print(f"\n  Top tags:")
        for tag in data['tags'][:5]:
            print(f"    - {tag['tag_name']} ({tag['tag_type']}, in {tag['document_count']} docs)")
    else:
        print(f"✗ Error: {response.json()}")

def delete_document(doc_id):
    """Delete a document"""
    print(f"\n7. Deleting document {doc_id}")
    
    response = requests.delete(f"{BASE_URL}/documents/{doc_id}")
    
    if response.status_code == 200:
        print(f"✓ Document deleted successfully!")
    else:
        print(f"✗ Error: {response.json()}")

def main():
    """Main execution"""
    print("="*60)
    print("AutoTagger API Usage Examples")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("\n✗ Error: AutoTagger server is not running!")
            print("Please start the server with: python run.py")
            return
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to AutoTagger server!")
        print("Please start the server with: python run.py")
        return
    
    print("✓ Server is running\n")
    
    # Create and upload document
    filepath = create_sample_document()
    doc_id = upload_document(filepath)
    
    if doc_id:
        # Demonstrate other API endpoints
        get_all_documents()
        get_document_details(doc_id)
        add_custom_tags(doc_id)
        find_similar_documents(doc_id)
        get_all_tags()
        
        # Optional: Uncomment to delete the document
        # delete_document(doc_id)
    
    # Cleanup
    if filepath.exists():
        filepath.unlink()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)

if __name__ == "__main__":
    main()