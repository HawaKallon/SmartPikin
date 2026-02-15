import os
from PyPDF2 import PdfReader
from django.core.management.base import BaseCommand
from django.conf import settings
from ai_core.models import DocumentChunk
from ai_core.utils import get_embedding, embedding_to_bytes

BATCH_SIZE = 100


class Command(BaseCommand):
    help = "Process primary, JSS, and SSS handbook PDFs from a directory and store embeddings."

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

        self.stdout.write(f"Processing PDFs in directory: {pdf_dir}")
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_dir, filename)
                self.stdout.write(f"Processing {filename}...")
                self.process_pdf(pdf_path)

        self.stdout.write(self.style.SUCCESS("Processing complete."))

    def process_pdf(self, pdf_path):
        """
        Process a PDF file, extract text, split into chunks, generate embeddings, and store in the database.
        """
        reader = PdfReader(pdf_path)
        text = "".join([page.extract_text() for page in reader.pages])

        chunks = [text[i:i + 300] for i in range(0, len(text), 300)]

        document_type = self.classify_document_type(os.path.basename(pdf_path))

        for i in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            embeddings = [get_embedding(chunk) for chunk in batch_chunks]

            DocumentChunk.objects.bulk_create([
                DocumentChunk(
                    document_type=document_type,
                    chunk_text=chunk,
                    embedding=embedding_to_bytes(embedding),
                    metadata={"source": pdf_path, "chunk_id": f"chunk_{i + j}"}
                )
                for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings))
            ])

    def classify_document_type(self, filename):
        """
        Classify the document type based on the filename.
        """
        filename_lower = filename.lower()
        if "primary" in filename_lower:
            return "Primary School Handbook"
        elif "jss" in filename_lower or "junior" in filename_lower:
            return "JSS Handbook"
        elif "sss" in filename_lower or "senior" in filename_lower:
            return "SSS Handbook"
        else:
            return "Unknown"
