import os
from urllib import response
from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from .celery import update_chat_db, update_summary_db
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserSerializer, ChatSerializer, SummarySerializer
import PyPDF2
from docx import Document
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import asyncio

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = InferenceClient(api_key=API_KEY)
# Create your views here.

if not API_KEY:
    raise ValueError("Api Key not found")

class CreateUser(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = [UserSerializer]
    

class SummaryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (MultiPartParser, FormParser)
    
    async def post(self, request, *args, **kwargs):
        user = request.user
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            file_name = uploaded_file.name
            try:
                # Process PDF file
                if uploaded_file.name.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
   
                # Process text files (e.g., .txt)
                elif uploaded_file.name.endswith('.txt'):
                    text = uploaded_file.read().decode('utf-8')  # Read and decode text
                
                # Read and process the .docx file
                elif uploaded_file.name.endswith('.docx'):
                    # Load the .docx file
                    document = Document(uploaded_file)
                    text = []
                    for paragraph in document.paragraphs:
                        text.append(paragraph.text)             # Extract text from each paragraph
                    text = "\n".join(text)
            
                else:
                    return Response({"error": "Unsupported file type."}, status=400)


            except Exception as e:
                return Response({"error": str(e)}, status=500)
        else:
            text = request.data.get("text")
            filename = text[:100]
        
        try:
            response_text = await client.summarization(text)
        except Exception as e:
            return Response({"error": f"summarization error : {e}"}, status = 500)
        
        #call celery worker to add to database
        update_summary_db.delay(user.id, filename, response_text)
        
        #response to be returned
        return Response({"input":filename,
                        "output":response_text}, status=202)
        
    
    def get(self, request):
        user = request.user
        return Response(
            {
                "ouput": ...,
            }, status = 200
        )