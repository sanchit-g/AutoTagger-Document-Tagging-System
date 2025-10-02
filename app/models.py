"""
Database Models for AutoTagger
"""
from app import db
from datetime import datetime
from sqlalchemy import Index

class Document(db.Model):
    """Document model for storing uploaded documents"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed = db.Column(db.Boolean, default=False, nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    file_type = db.Column(db.String(10))  # txt or pdf
    
    # Relationship with tags
    tags = db.relationship('Tag', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    
    # Index for faster queries
    __table_args__ = (
        Index('idx_upload_date', 'upload_date'),
        Index('idx_processed', 'processed'),
    )
    
    def to_dict(self, include_content=False):
        """Convert document to dictionary"""
        data = {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'processed': self.processed,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'tag_count': self.tags.count()
        }
        if include_content:
            data['content'] = self.content
        return data
    
    def __repr__(self):
        return f'<Document {self.id}: {self.filename}>'

class Tag(db.Model):
    """Tag model for storing document tags"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    tag_name = db.Column(db.String(100), nullable=False)
    tag_type = db.Column(db.String(20), nullable=False)  # keyword, entity, custom
    confidence_score = db.Column(db.Float, default=0.0)
    entity_type = db.Column(db.String(50))  # PERSON, ORG, GPE, etc. (for NER tags)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_document_id', 'document_id'),
        Index('idx_tag_name', 'tag_name'),
        Index('idx_tag_type', 'tag_type'),
        Index('idx_confidence', 'confidence_score'),
    )
    
    def to_dict(self):
        """Convert tag to dictionary"""
        data = {
            'id': self.id,
            'document_id': self.document_id,
            'tag_name': self.tag_name,
            'tag_type': self.tag_type,
            'confidence_score': round(self.confidence_score, 3),
            'created_at': self.created_at.isoformat()
        }
        if self.entity_type:
            data['entity_type'] = self.entity_type
        return data
    
    def __repr__(self):
        return f'<Tag {self.tag_name} ({self.tag_type})>'