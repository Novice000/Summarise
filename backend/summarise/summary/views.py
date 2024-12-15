from decimal import InvalidOperation
import os
from django.shortcuts import get_object_or_404
from .utils.utils import extract_text_from_file
from .models import Summary, Chat
from .celery import update_chat_db, update_summary_db
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserSerializer, ChatSerializer, SummarySerializer
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from utils.pagination import SummaryPaginator, ChatPaginator

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = InferenceClient(api_key=API_KEY)
# Create your views here.

if not API_KEY:
    raise ValueError("Api Key not found")

class CreateUserView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

class GetUserView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
       
class SummaryView(APIView):
    
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    async def post(self, request, *args, **kwargs):
        
        user = request.user
        uploaded_file = request.FILES.get('file')
        
        if uploaded_file:
            to_summarise = uploaded_file.name
            try:
                text = extract_text_from_file(uploaded_file)
            except InvalidOperation:
                    return Response({"error": "Unsupported file type."}, status=400)
            except Exception as e:
                return Response({"error": str(e)}, status=500)
        else:
            text = request.data.get("text")
            if len(text) < 200:
                to_summarise = text
            else: to_summarise = text[:200]
        
        try:
            response_text = await client.summarization(text)
        except Exception as e:
            return Response({"error": f"summarization error : {e}"}, status = 500)
        
        #call celery worker to add to database
        update_summary_db.delay(user.id, to_summarise, response_text)
        
        #response to be returned
        return Response({"input":to_summarise,
                        "output":response_text}, status=202)
        
class SummariesListView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    pagination_class = SummaryPaginator
    
    def get_queryset(self):
        user = self.request.user
        summaries = Summary.objects.filter(user = user)
        return summaries
    
class GetSummaryView(RetrieveAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    
    def get_object(self):
        user = self.request.user
        id =  self.kwargs.get("id")
        summary = get_object_or_404(Summary, id = id)
        if summary.user == user:
            return summary
        raise PermissionDenied("Not Authorised to view this summary")
    
class ChatView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    async def post(self, request):
        user = request.user
        data = ChatSerializer(data = request.data)
        query = data.validated_data["chat"]
        chat_id = data.validated_data.get("id", None)
        output = await client.text_generation(query["user"])
        update_chat_db(output,query, user.id, chat_id)
        
class ChatListView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    pagination_class = ChatPaginator
    
    
    def get_queryset(self):
        user = self.request.user
        chats = Chat.objects.filter(user = user)
        if not chats:
            raise PermissionDenied("No chat Exists")
        return chats
    
class GetChatView(RetrieveAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        chat_id = self.kwargs.get("chat_id")
        try:
            chat = Chat.objects.get(id = chat_id)
        except (Chat.DoesNotExist, Chat.MultipleObjectsReturned):
            raise PermissionDenied("Invalid Chat Id provided")
        if chat.user != user:
            raise PermissionDenied("Not authorised to view this chat")
        return Chat