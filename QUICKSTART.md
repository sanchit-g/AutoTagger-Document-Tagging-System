# AutoTagger Quick Start Guide

Get up and running with AutoTagger in 5 minutes!

## Prerequisites
- Python 3.9 or higher
- pip installed
- 500MB free disk space

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup script
./setup.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Create directories
mkdir -p uploads logs

# 5. Create .env file (optional)
cp .env.example .env
```

## Start the Server

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run the server
python run.py
```

The server will start at `http://localhost:5000`

## Test the API

### Using curl

```bash
# 1. Create a test file
echo "Artificial Intelligence and Machine Learning are revolutionizing technology." > test.txt

# 2. Upload the document
curl -X POST http://localhost:5000/api/documents/upload -F "file=@test.txt"

# 3. Get all documents
curl http://localhost:5000/api/documents

# 4. Get all tags
curl http://localhost:5000/api/tags
```

### Using Python

```bash
# Run the example script
python examples/api_usage.py
```

## Common API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/upload` | POST | Upload and process document |
| `/api/documents` | GET | List all documents |
| `/api/documents/{id}` | GET | Get document details |
| `/api/documents/{id}/similar` | GET | Find similar documents |
| `/api/tags` | GET | Get all tags with stats |
| `/api/health` | GET | Health check |

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API endpoints using the examples
3. Check out the test suite in `tests/`
4. Customize configuration in `config.py`

## Troubleshooting

**Server won't start?**
- Ensure virtual environment is activated
- Check Python version: `python --version`
- Verify dependencies: `pip list`

**spaCy model error?**
```bash
python -m spacy download en_core_web_sm
```

**NLTK data error?**
The application downloads NLTK data automatically on first run. If issues persist:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

## Support

For issues or questions, check the [README.md](README.md) documentation.