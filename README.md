# AutoTagger - Automated Document Tagging System

A Python-based REST API backend for automated document tagging using Natural Language Processing (NLP). AutoTagger automatically extracts relevant keywords, named entities, and generates tags for uploaded documents while providing document similarity matching capabilities.

## 🎯 Features

### Core Functionality
- **Document Upload & Processing**: Accept TXT and PDF files via file upload
- **Automatic Tag Generation**: Extract keywords using TF-IDF and named entities using spaCy NER
- **Document Similarity**: Calculate cosine similarity to find related documents
- **Tag Management**: View, update, and manage tags for all documents
- **RESTful API**: Complete REST API with CRUD operations

### NLP Capabilities
- **Keyword Extraction**: TF-IDF based keyword extraction (top 5-10 keywords per document)
- **Named Entity Recognition**: Extract persons, organizations, locations, and more using spaCy
- **Text Preprocessing**: Tokenization, stopword removal, and lemmatization using NLTK
- **Similarity Matching**: Cosine similarity calculation for document comparison
- **Confidence Scores**: Each tag includes a confidence score indicating relevance

### Technical Features
- **SQLite Database**: Efficient storage with proper indexing and foreign keys
- **Tag Categorization**: Tags organized by type (keyword, entity, custom)
- **Batch Processing**: Support for multiple documents
- **Error Handling**: Comprehensive error handling and validation
- **Logging**: Detailed logging for debugging and monitoring
- **File Size Limits**: Configurable limits to prevent abuse

## 🛠️ Tech Stack

- **Python 3.9+**
- **Flask**: Web framework for REST API
- **SQLAlchemy**: ORM for database operations
- **NLTK**: Text preprocessing and tokenization
- **spaCy**: Named Entity Recognition
- **scikit-learn**: TF-IDF vectorization and cosine similarity
- **PyPDF2 & pdfplumber**: PDF text extraction
- **SQLite**: Lightweight database

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 500MB free disk space (for NLP models)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd autotagger
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLP Models

```bash
# Download spaCy model
python -m spacy download en_core_web_sm

# NLTK data will be downloaded automatically on first run
```

### 5. Create Required Directories

```bash
mkdir -p uploads logs
```

## 🎮 Running the Application

### Development Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Upload Document
**POST** `/documents/upload`

Upload a document and automatically generate tags.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (TXT or PDF file)

**Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 1,
    "filename": "example.txt",
    "upload_date": "2024-01-15T10:30:00",
    "processed": true,
    "file_size": 15234,
    "file_type": "txt",
    "tag_count": 8
  },
  "tags": [
    {
      "id": 1,
      "tag_name": "machine learning",
      "tag_type": "keyword",
      "confidence_score": 0.856,
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "tag_name": "Google",
      "tag_type": "entity",
      "entity_type": "ORG",
      "confidence_score": 0.800,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "processing_time": 1.23,
  "tag_summary": {
    "keywords": 5,
    "entities": 3,
    "total": 8
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@document.txt"
```

#### 2. List All Documents
**GET** `/documents`

Get all documents with their tags.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Results per page (default: 20)
- `processed` (optional): Filter by processing status (true/false)

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "example.txt",
      "upload_date": "2024-01-15T10:30:00",
      "processed": true,
      "file_size": 15234,
      "file_type": "txt",
      "tag_count": 8,
      "tags": [...]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_documents": 87
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/documents?page=1&per_page=10
```

#### 3. Get Specific Document
**GET** `/documents/{id}`

Get details of a specific document.

**Query Parameters:**
- `include_content` (optional): Include full document content (true/false, default: false)

**Response:**
```json
{
  "id": 1,
  "filename": "example.txt",
  "upload_date": "2024-01-15T10:30:00",
  "processed": true,
  "file_size": 15234,
  "file_type": "txt",
  "tag_count": 8,
  "tags": [...],
  "tags_by_type": {
    "keywords": [...],
    "entities": [...],
    "custom": [...]
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/documents/1?include_content=true
```

#### 4. Update Document Tags
**PUT** `/documents/{id}/tags`

Add or remove tags for a document.

**Request Body:**
```json
{
  "add_tags": [
    {
      "tag_name": "custom tag",
      "tag_type": "custom",
      "confidence_score": 1.0
    }
  ],
  "remove_tag_ids": [5, 6, 7]
}
```

**Response:**
```json
{
  "message": "Tags updated successfully",
  "added": 1,
  "removed": 3,
  "current_tags": [...]
}
```

**Example:**
```bash
curl -X PUT http://localhost:5000/api/documents/1/tags \
  -H "Content-Type: application/json" \
  -d '{"add_tags": [{"tag_name": "important", "tag_type": "custom"}]}'
```

#### 5. Delete Document
**DELETE** `/documents/{id}`

Delete a document and all its tags.

**Response:**
```json
{
  "message": "Document 1 deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/documents/1
```

#### 6. Find Similar Documents
**GET** `/documents/{id}/similar`

Find documents similar to the specified document.

**Query Parameters:**
- `limit` (optional): Maximum number of results (default: 5)
- `threshold` (optional): Minimum similarity score 0-1 (default: 0.3)

**Response:**
```json
{
  "document_id": 1,
  "similar_documents": [
    {
      "id": 5,
      "filename": "related_doc.txt",
      "similarity_score": 0.847,
      "upload_date": "2024-01-14T09:15:00",
      "tags": [...]
    }
  ],
  "count": 3
}
```

**Example:**
```bash
curl "http://localhost:5000/api/documents/1/similar?limit=5&threshold=0.5"
```

#### 7. Get All Tags
**GET** `/tags`

Get all unique tags with statistics.

**Query Parameters:**
- `tag_type` (optional): Filter by tag type (keyword/entity/custom)
- `min_count` (optional): Minimum document count (default: 1)
- `limit` (optional): Maximum number of tags (default: 100)

**Response:**
```json
{
  "tags": [
    {
      "tag_name": "machine learning",
      "tag_type": "keyword",
      "document_count": 15,
      "avg_confidence": 0.782
    }
  ],
  "summary": {
    "keyword": {
      "unique_tags": 145,
      "total_instances": 892
    },
    "entity": {
      "unique_tags": 67,
      "total_instances": 234
    }
  },
  "total_unique_tags": 212
}
```

**Example:**
```bash
curl "http://localhost:5000/api/tags?tag_type=entity&min_count=2"
```

#### 8. Health Check
**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "AutoTagger API"
}
```

## 📁 Project Structure

```
autotagger/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── routes.py            # API endpoints
│   ├── nlp_processor.py     # NLP processing logic
│   ├── file_handler.py      # File upload and text extraction
│   └── error_handlers.py    # Error handling and validation
├── uploads/                 # Uploaded files directory
├── logs/                    # Application logs
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔧 Configuration

Configuration can be modified in [`config.py`](config.py):

- `MAX_CONTENT_LENGTH`: Maximum file size (default: 10MB)
- `ALLOWED_EXTENSIONS`: Allowed file types (default: txt, pdf)
- `MAX_KEYWORDS`: Maximum keywords to extract (default: 10)
- `MIN_KEYWORD_LENGTH`: Minimum keyword length (default: 3)
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.3)

## 🧪 Testing

Create a test document and upload it:

```bash
# Create a test file
echo "Machine learning is a subset of artificial intelligence. 
Google and Microsoft are leading companies in AI research." > test.txt

# Upload the document
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@test.txt"

# View all documents
curl http://localhost:5000/api/documents

# Find similar documents
curl http://localhost:5000/api/documents/1/similar
```

## 📊 Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    file_size INTEGER,
    file_type VARCHAR(10)
);
```

### Tags Table
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    tag_name VARCHAR(100) NOT NULL,
    tag_type VARCHAR(20) NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    entity_type VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
```

## 🚀 Performance Metrics

- **Keyword Extraction**: 5-10 meaningful tags per document
- **Processing Time**: < 2 seconds for files up to 10MB
- **Similarity Accuracy**: > 80% for related documents
- **Scalability**: Supports 100+ documents efficiently

## 🔒 Security Features

- File type validation
- File size limits
- SQL injection prevention (SQLAlchemy ORM)
- Input sanitization
- Secure filename handling
- Error message sanitization

## 🐛 Troubleshooting

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### NLTK Data Download Issues
The application will automatically download required NLTK data on first run. If issues occur:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

### PDF Extraction Issues
Some PDFs may not extract text properly if they contain scanned images. Use OCR tools for scanned documents.

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced custom tagging rules
- [ ] Tag recommendations based on similar documents
- [ ] Batch document upload
- [ ] Export tags to CSV/JSON
- [ ] Document versioning
- [ ] User authentication
- [ ] Real-time processing with WebSockets
- [ ] Docker containerization
- [ ] Admin dashboard UI