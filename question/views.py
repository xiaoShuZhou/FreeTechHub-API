from django.shortcuts import render
from rest_framework import viewsets
from .serializers import QuestionSerializer
from .models import Question
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsOwnerOrReadOnly
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [
        IsAuthenticated,
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]

    def create(self, request, *args, **kwargs):
        print(request.data)
        print(type(request.data))
        data = {
            'csrfmiddlewaretoken': request.data['csrfmiddlewaretoken'],
            'title': request.data['title'],
            'content': request.data['content'],
            'rewarded_money':request.data['rewarded_money'],
            'viewTimes': 0,
            'note': request.data['note'],
            'status': False,
            'question_type': True,
            'owner' : request.user.id
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
