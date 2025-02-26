from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
import google.generativeai as genai
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from history_ai import history_gemini
from rest_framework.views import APIView

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv_path = os.path.join(BASE_DIR, ".env")
history = history_gemini.memory
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables!")

class MySecureView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]  
    permission_classes = [HasAPIKey | IsAuthenticated] 

def protected_view(request):
    return JsonResponse({"message": "This is a protected view"})

@api_view(['GET', 'POST'])
@permission_classes([HasAPIKey]) 
def deva_chat(request, query=None):
    user_input = request.data.get("message", "").strip() if request.method == 'POST' else query
    
    if not user_input:
        return Response({"error": "Message cannot be empty"}, status=400)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are my assistant. Your name is Deva, call me Sir."
        )
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_input)
        model_response = response.text

        history.append({"role": "user", "parts": [user_input]})
        history.append({"role": "model", "parts": [model_response]})
        
        return Response({"question": user_input, "response": model_response})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
