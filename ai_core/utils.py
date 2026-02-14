import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
import datetime
import os
import numpy as np
import faiss
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from .models import DocumentChunk

FAISS_INDEX_PATH = "faiss_index.index"


def process_pdf_in_batches(pdf_path, document_type, batch_size=100):
    reader = PdfReader(pdf_path)
    text = "".join([page.extract_text() for page in reader.pages])
    chunks = [text[i:i + 300] for i in range(0, len(text), 300)]  # Split into chunks

    model = SentenceTransformer('all-MiniLM-L6-v2')

    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        embeddings = [model.encode(chunk) for chunk in batch_chunks]

        DocumentChunk.objects.bulk_create([
            DocumentChunk(
                document_type=document_type,
                chunk_text=chunk,
                embedding=np.array(embedding).tobytes(),
                metadata={"source": pdf_path}
            )
            for chunk, embedding in zip(batch_chunks, embeddings)
        ])


def update_pdf_data(pdf_path, document_type):
    reader = PdfReader(pdf_path)
    text = "".join([page.extract_text() for page in reader.pages])
    chunks = [text[i:i + 300] for i in range(0, len(text), 300)]

    model = SentenceTransformer('all-MiniLM-L6-v2')

    for chunk in chunks:
        if not DocumentChunk.objects.filter(chunk_text=chunk, document_type=document_type).exists():
            embedding = model.encode(chunk)
            DocumentChunk.objects.create(
                document_type=document_type,
                chunk_text=chunk,
                embedding=np.array(embedding).tobytes(),
                metadata={"source": pdf_path}
            )


def build_faiss_index():
    chunks = DocumentChunk.objects.all()
    embeddings = [np.frombuffer(chunk.embedding, dtype=np.float32) for chunk in chunks]
    embedding_dim = embeddings[0].shape[0] if embeddings else 768

    index = faiss.IndexFlatL2(embedding_dim)
    if embeddings:
        index.add(np.array(embeddings))

    faiss.write_index(index, FAISS_INDEX_PATH)
    return index


def load_faiss_index():
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    else:
        return build_faiss_index()


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