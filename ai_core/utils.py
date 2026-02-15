import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
import datetime
import os
import json
import math
import logging
from PyPDF2 import PdfReader
from django.conf import settings

from google import genai

logger = logging.getLogger(__name__)

# Configure Google GenAI client
genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

EMBEDDING_MODEL = "text-embedding-004"


def get_embedding(text):
    """Get embedding vector from Google GenAI."""
    result = genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return result.embeddings[0].values


def get_query_embedding(text):
    """Get embedding vector for a query from Google GenAI."""
    result = genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return result.embeddings[0].values


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def embedding_to_bytes(embedding):
    """Serialize embedding list to bytes for database storage."""
    return json.dumps(embedding).encode('utf-8')


def embedding_from_bytes(data):
    """Deserialize embedding from bytes."""
    return json.loads(data.decode('utf-8'))


def process_pdf_in_batches(pdf_path, document_type, batch_size=100):
    from .models import DocumentChunk

    reader = PdfReader(pdf_path)
    text = "".join([page.extract_text() for page in reader.pages])
    chunks = [text[i:i + 300] for i in range(0, len(text), 300)]

    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        embeddings = [get_embedding(chunk) for chunk in batch_chunks]

        DocumentChunk.objects.bulk_create([
            DocumentChunk(
                document_type=document_type,
                chunk_text=chunk,
                embedding=embedding_to_bytes(embedding),
                metadata={"source": pdf_path}
            )
            for chunk, embedding in zip(batch_chunks, embeddings)
        ])


def update_pdf_data(pdf_path, document_type):
    from .models import DocumentChunk

    reader = PdfReader(pdf_path)
    text = "".join([page.extract_text() for page in reader.pages])
    chunks = [text[i:i + 300] for i in range(0, len(text), 300)]

    for chunk in chunks:
        if not DocumentChunk.objects.filter(chunk_text=chunk, document_type=document_type).exists():
            embedding = get_embedding(chunk)
            DocumentChunk.objects.create(
                document_type=document_type,
                chunk_text=chunk,
                embedding=embedding_to_bytes(embedding),
                metadata={"source": pdf_path}
            )


def search_similar_chunks(query, chunks=None, top_k=5):
    """Search for similar chunks using cosine similarity (replaces FAISS)."""
    from .models import DocumentChunk

    if chunks is None:
        chunks = DocumentChunk.objects.all()

    query_embedding = get_query_embedding(query)

    scored_chunks = []
    for chunk in chunks:
        try:
            chunk_embedding = embedding_from_bytes(chunk.embedding)
            score = cosine_similarity(query_embedding, chunk_embedding)
            scored_chunks.append((score, chunk))
        except Exception:
            continue

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored_chunks[:top_k]]


def generate_pdf(html_content, output_filename='document.pdf', options=None):
    try:
        pdf = pdfkit.from_string(html_content, False, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
        return response
    except IOError as e:
        return None


import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file.
    :param pdf_file: Uploaded PDF file
    :return: Extracted text as a string
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None
