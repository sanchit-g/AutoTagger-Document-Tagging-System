"""
NLP Processing Module for AutoTagger
Handles keyword extraction, NER, and document similarity
"""
import re
import logging
from collections import Counter
from typing import List, Dict, Tuple
import numpy as np

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Main NLP processing class for document analysis"""
    
    def __init__(self, max_keywords=10, min_keyword_length=3):
        """
        Initialize NLP processor
        
        Args:
            max_keywords: Maximum number of keywords to extract
            min_keyword_length: Minimum length of keywords
        """
        self.max_keywords = max_keywords
        self.min_keyword_length = min_keyword_length
        
        # Initialize NLTK components
        self._init_nltk()
        
        # Initialize spaCy
        try:
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {e}")
            logger.warning("Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),  # Support unigrams and bigrams
            min_df=1
        )
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def _init_nltk(self):
        """Download required NLTK data"""
        required_data = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                try:
                    nltk.download(data, quiet=True)
                    logger.info(f"Downloaded NLTK data: {data}")
                except Exception as e:
                    logger.warning(f"Could not download NLTK data {data}: {e}")
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text: lowercase, remove special chars, etc.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """
        Tokenize and lemmatize text
        
        Args:
            text: Input text
            
        Returns:
            List of lemmatized tokens
        """
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words, then lemmatize
        lemmatized = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) >= self.min_keyword_length
        ]
        
        return lemmatized
    
    def extract_keywords_tfidf(self, text: str, top_n: int = None) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF
        
        Args:
            text: Input text
            top_n: Number of top keywords to extract
            
        Returns:
            List of (keyword, score) tuples
        """
        if top_n is None:
            top_n = self.max_keywords
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Fit and transform
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([processed_text])
            
            # Get feature names and scores
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Create keyword-score pairs
            keyword_scores = [(feature_names[i], scores[i]) 
                            for i in range(len(feature_names)) if scores[i] > 0]
            
            # Sort by score and return top N
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            return keyword_scores[:top_n]
            
        except Exception as e:
            logger.error(f"Error extracting keywords with TF-IDF: {e}")
            return []
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities using spaCy
        
        Args:
            text: Input text
            
        Returns:
            List of entity dictionaries with text, label, and confidence
        """
        if not self.nlp:
            logger.warning("spaCy model not available")
            return []
        
        try:
            doc = self.nlp(text)
            
            entities = []
            for ent in doc.ents:
                # Filter relevant entity types
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'confidence': 0.8  # spaCy doesn't provide confidence scores directly
                    })
            
            # Remove duplicates while preserving order
            seen = set()
            unique_entities = []
            for ent in entities:
                key = (ent['text'].lower(), ent['label'])
                if key not in seen:
                    seen.add(key)
                    unique_entities.append(ent)
            
            return unique_entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def extract_all_tags(self, text: str) -> Dict[str, List]:
        """
        Extract all types of tags from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with 'keywords' and 'entities' lists
        """
        tags = {
            'keywords': [],
            'entities': []
        }
        
        # Extract keywords
        keywords = self.extract_keywords_tfidf(text)
        for keyword, score in keywords:
            tags['keywords'].append({
                'tag_name': keyword,
                'tag_type': 'keyword',
                'confidence_score': float(score)
            })
        
        # Extract entities
        entities = self.extract_entities(text)
        for entity in entities:
            tags['entities'].append({
                'tag_name': entity['text'],
                'tag_type': 'entity',
                'confidence_score': entity['confidence'],
                'entity_type': entity['label']
            })
        
        logger.info(f"Extracted {len(tags['keywords'])} keywords and {len(tags['entities'])} entities")
        return tags
    
    def calculate_document_similarity(self, doc1_content: str, doc2_content: str) -> float:
        """
        Calculate cosine similarity between two documents
        
        Args:
            doc1_content: Content of first document
            doc2_content: Content of second document
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Preprocess both documents
            doc1 = self.preprocess_text(doc1_content)
            doc2 = self.preprocess_text(doc2_content)
            
            # Create TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([doc1, doc2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_similar_documents(self, target_content: str, 
                              document_contents: List[Tuple[int, str]], 
                              threshold: float = 0.3) -> List[Tuple[int, float]]:
        """
        Find similar documents based on content
        
        Args:
            target_content: Content of target document
            document_contents: List of (doc_id, content) tuples
            threshold: Minimum similarity threshold
            
        Returns:
            List of (doc_id, similarity_score) tuples, sorted by similarity
        """
        if not document_contents:
            return []
        
        try:
            # Preprocess target document
            target = self.preprocess_text(target_content)
            
            # Preprocess all documents
            all_contents = [target] + [self.preprocess_text(content) for _, content in document_contents]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_contents)
            
            # Calculate similarities with target (first document)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            # Create results
            similar_docs = [
                (doc_id, float(sim)) 
                for (doc_id, _), sim in zip(document_contents, similarities)
                if sim >= threshold
            ]
            
            # Sort by similarity (descending)
            similar_docs.sort(key=lambda x: x[1], reverse=True)
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            return []