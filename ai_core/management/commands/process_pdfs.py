from django.core.management.base import BaseCommand
from ai_core.utils import process_pdf_in_batches, build_faiss_index


class Command(BaseCommand):
    help = "Process WAEC History PDFs and store embeddings"

    def handle(self, *args, **kwargs):
        syllabus_path = "data/waec_history_syllabus.pdf"
        textbook_path = "data/waec_history_textbook.pdf"

        self.stdout.write("Processing WAEC History Syllabus...")
        process_pdf_in_batches(syllabus_path, "WAEC Syllabus")
        self.stdout.write("Processing WAEC History Textbook...")
        process_pdf_in_batches(textbook_path, "History Textbook")

        self.stdout.write("Building FAISS index...")
        build_faiss_index()
        self.stdout.write("Processing complete.")
