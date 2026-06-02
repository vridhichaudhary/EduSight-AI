from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.students.models import Student, ChatMessage
from .chat_engine import ChatEngine
import logging

logger = logging.getLogger('apps.chat')

class ChatQueryView(APIView):
    """
    Handles chat message history and new queries.
    GET: Returns conversation history for a student
    POST: Processes a new user message and returns AI response
    """
    
    def get(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {"success": False, "message": "student_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        student = get_object_or_404(Student, pk=student_id)
        
        # Get history (last 50 messages)
        messages = ChatMessage.objects.filter(
            student=student
        ).order_by('created_at')[:50]
        
        data = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]
        
        return Response({
            "success": True,
            "data": data
        })

    def post(self, request):
        student_id = request.data.get('student_id')
        message_text = request.data.get('message')
        
        if not student_id or not message_text:
            return Response(
                {"success": False, "message": "student_id and message are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        student = get_object_or_404(Student, pk=student_id)
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            student=student,
            role='user',
            content=message_text
        )
        
        # Generate AI response
        engine = ChatEngine(student_id=student.id)
        ai_response_text = engine.generate_response(message_text)
        
        # Save AI message
        ai_msg = ChatMessage.objects.create(
            student=student,
            role='assistant',
            content=ai_response_text
        )
        
        return Response({
            "success": True,
            "data": {
                "message_id": ai_msg.id,
                "ai_response": ai_response_text,
                "timestamp": ai_msg.created_at.isoformat()
            }
        })
