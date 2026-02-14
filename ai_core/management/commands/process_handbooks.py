import os
import numpy as np
import faiss
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from django.core.management.base import BaseCommand
from django.conf import settings
from ai_core.models import DocumentChunk  # Replace `your_app` with your app name

# Define paths and constants
FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, "faiss_index_handbooks.index")  # Separate index file
BATCH_SIZE = 100
MODEL_NAME = 'all-MiniLM-L6-v2'

class Command(BaseCommand):
    help = "Process primary, JSS, and SSS handbook PDFs from a directory and store embeddings in a separate FAISS index."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            type=str,
            required=True,
            help="Path to the directory containing primary, JSS, and SSS handbook PDFs.",
        )

    def handle(self, *args, **options):
        pdf_dir = options.get("dir")

        if not os.path.exists(pdf_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {pdf_dir}"))
            return

        # Process all PDFs in the directory
        self.stdout.write(f"Processing PDFs in directory: {pdf_dir}")
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_dir, filename)
                self.stdout.write(f"Processing {filename}...")
                self.process_pdf(pdf_path)

        # Build FAISS index
        self.stdout.write("Building FAISS index...")
        self.build_faiss_index()
        self.stdout.write(self.style.SUCCESS("Processing complete."))

    def process_pdf(self, pdf_path):
        """
        Process a PDF file, extract text, split into chunks, generate embeddings, and store in the database.
        """
        # Extract text from PDF
        reader = PdfReader(pdf_path)
        text = "".join([page.extract_text() for page in reader.pages])

        # Split text into chunks
        chunks = [text[i:i + 300] for i in range(0, len(text), 300)]  # Adjust chunk size as needed

        # Load sentence transformer model
        model = SentenceTransformer(MODEL_NAME)

        # Determine document type based on filename (customize this logic as needed)
        document_type = self.classify_document_type(os.path.basename(pdf_path))

        # Process chunks in batches
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            embeddings = model.encode(batch_chunks)

            # Store chunks and embeddings in the database
            DocumentChunk.objects.bulk_create([
                DocumentChunk(
                    document_type=document_type,
                    chunk_text=chunk,
                    embedding=np.array(embedding).tobytes(),
                    metadata={"source": pdf_path, "chunk_id": f"chunk_{i + j}"}  # Add metadata
                )
                for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings))
            ])

    def classify_document_type(self, filename):
        """
        Classify the document type based on the filename.
        Customize this logic based on your filenames.
        """
        filename_lower = filename.lower()
        if "primary" in filename_lower:
            return "Primary School Handbook"
        elif "jss" in filename_lower or "junior" in filename_lower:
            return "JSS Handbook"
        elif "sss" in filename_lower or "senior" in filename_lower:
            return "SSS Handbook"
        else:
            return "Unknown"  # Default type

    def build_faiss_index(self):
        """
        Build a FAISS index from all embeddings in the database for handbooks.
        """
        chunks = DocumentChunk.objects.filter(
            document_type__in=["Primary School Handbook", "JSS Handbook", "SSS Handbook"]
        )
        embeddings = [np.frombuffer(chunk.embedding, dtype=np.float32) for chunk in chunks]
        embedding_dim = embeddings[0].shape[0] if embeddings else 768

        # Create and populate FAISS index
        index = faiss.IndexFlatL2(embedding_dim)
        if embeddings:
            index.add(np.array(embeddings))

        # Save the index to disk
        faiss.write_index(index, FAISS_INDEX_PATH)
        self.stdout.write(self.style.SUCCESS(f"FAISS index saved to {FAISS_INDEX_PATH}"))