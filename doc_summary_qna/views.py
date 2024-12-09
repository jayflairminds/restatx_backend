from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from PyPDF2 import PdfReader
from .doc_processing import *
from .prompts import *
import pytesseract 
from rest_framework import status
from pdf2image import convert_from_bytes
import fitz 
import csv
from io import StringIO
import mimetypes
from docx import Document
from PIL import Image

class UploadView(APIView):
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('uploaded_file')
            
            text = get_pdf_text(uploaded_file) 
            chunks = get_text_chunks(text)
            get_vector_store(chunks)
            return Response({"Output": "File uploaded successfully"}, status=200)
        except Exception as e:
            return Response({"error":str(e)},status=500)



class ResponseView(APIView):
    def post(self,request):
        try:
            user_question = request.data.get("user_question")
            predefined_question = request.data.get("predefined_question")
            if predefined_question:
                user_question = predefined_prompts()
            response = user_input(user_question)
            return Response({"response":response},status=200)
        except Exception as e:
            return Response({"error":str(e)},status=500)


class ExtractText(APIView):
    

     def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('uploaded_file')  # Get the uploaded file
              
        if not uploaded_file:
            return Response({"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST)

        file_extension = uploaded_file.name.split('.')[-1].lower()
        mime_type, _ = mimetypes.guess_type(uploaded_file.name) 

        if file_extension == "pdf":

            try:
                # Read the file into memory
                file_content = uploaded_file.read()

                # Open PDF with PyMuPDF
                doc = fitz.open(stream=file_content, filetype="pdf")


                textPageNumberMap = {}
                # Convert PDF pages to images using pdf2image
                pages = convert_from_bytes(file_content, 500)

                # Iterate through each page
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text("text")

                    # If text is available, use PyMuPDF
                    if text.strip():
                        textPageNumberMap[page_num + 1] = text
                    else:
                        # Otherwise, use OCR with Tesseract
                        scanned_text = pytesseract.image_to_string(pages[page_num])
                        textPageNumberMap[page_num + 1] = scanned_text

                # Combine all text from the pages
                combined_text = "\n".join(textPageNumberMap.values())

                if not combined_text.strip():
                    return Response(
                        {"message": "OCR failed to extract text. Please upload a better file."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Process the text into chunks
                chunks = get_text_chunks(combined_text)
                # Generate summary or other processing
                get_vector_store(chunks)

                return Response({"extracted_text": textPageNumberMap}, status=status.HTTP_200_OK)


            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

        elif file_extension == "csv":
            try:
                file_content = uploaded_file.read().decode('utf-8')
                csv_reader = csv.reader(StringIO(file_content))
                csv_text = ""

                for row in csv_reader:
                    csv_text += " ".join(row) + "\n"

                # Check if any content was extracted
                if not csv_text.strip():
                    return Response({"message":"Failed to extract text from the CSV file. Please upload a better CSV file."},status=status.HTTP_400_BAD_REQUEST)

                # Process CSV text (e.g., chunking or summary generation)
                chunks = get_text_chunks(csv_text)
                get_vector_store(chunks)

                return Response({"extracted_text": csv_text}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
            
        elif mime_type and mime_type.startswith("image/"):

             try:
                # Open the image with PIL
                image = Image.open(uploaded_file)

                # Extract text using Tesseract OCR
                extracted_text = pytesseract.image_to_string(image)

                if not extracted_text.strip():
                    return Response(
                        {"message": "OCR failed to extract text. Please upload a better image."},
                        status=status.HTTP_400_BAD_REQUEST
                    )


                # Process the extracted text
                chunks = get_text_chunks(extracted_text)
                get_vector_store(chunks)

                return Response({"extracted_text": extracted_text}, status=status.HTTP_200_OK)

             except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             
        elif file_extension == "docx":
            try:
                # Read the .docx file
                doc = Document(uploaded_file)
                doc_text = ""

                # Extract text from each paragraph in the document
                for paragraph in doc.paragraphs:
                    doc_text += paragraph.text + "\n"

                if not doc_text.strip():
                    return Response(
                        {"message": "The document appears to be empty. Please upload a valid .docx file."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Process the extracted text
                chunks = get_text_chunks(doc_text)
                get_vector_store(chunks)

                return Response({"extracted_text": doc_text}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        elif file_extension == "txt":
            try:
                # Read the uploaded text file
                file_content = uploaded_file.read().decode('utf-8')

                # Check if the file contains any content
                if not file_content.strip():
                     return Response({"message": "The file appears to be empty. Please upload a valid text file."}, status=status.HTTP_400_BAD_REQUEST)

                 # Process the text content (e.g., chunking or summary generation)
                chunks = get_text_chunks(file_content)
                get_vector_store(chunks)

                return Response({"extracted_text": file_content}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)                

        # Unsupported file type
        else:
            return Response({"error": "Unsupported file type."}, status=status.HTTP_400_BAD_REQUEST)  