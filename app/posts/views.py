from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework import permissions

from .models import Tweet, StatusTweet, StatusType, Comment
from .serilaizers import TweetSerializer, StatusTweetSerializer, CommentSerializer
from .permissions import PostPermission
# import telebot
#
# bot = telebot.TeleBot("5899491883:AAG9D20zW2lxJaSOgCbdi_hW3Kj9P9l-tJs", parse_mode=None)
#
# CHAT_ID_LIST = [
#     '1286090702',
#     '1286090702',
#     '1286090702',
#     '1286090702',
#     '1286090702',
# ]
#
#
# def send_telegram_message(chat_id_list, message):
#     for chat_id in chat_id_list:
#         bot.send_message(chat_id, message)


class PostPagePagination(PageNumberPagination):
    page_size = 3


class TweetViewSet(viewsets.ModelViewSet):
    """
    API для создания, получения, изменения и удаления твитов
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    permission_classes = [PostPermission, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['text', ]
    search_fields = ['text', ]
    ordering_fields = ['updated_at', 'created_at']
    pagination_class = PostPagePagination

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)
        # send_telegram_message(CHAT_ID_LIST,
        #                       'twit was post')

    @action(methods=['POST', 'GET'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def leave_status(self, request, pk=None):
        serializer = StatusTweetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                profile=request.user.profile,
                tweet=self.get_object()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [PostPermission, ]

    def get_queryset(self):
        return super().get_queryset().filter(tweet_id=self.kwargs.get('tweet_id'))

    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            tweet_id=self.kwargs.get('tweet_id')
        )


