from django.urls import path
from .views import *

urlpatterns = [
    path("register", CreateUserView.as_view(), name="register_user"),
    path("summary/", SummaryView.as_view(), name="post_summary"),
    path("summary/list/", SummariesListView.as_view(), name="get_summary_list"),
    path("summary/<int:id>/", GetSummaryView.as_view(), name= "get_summary"),
    path("chat/", ChatView.as_view(), name="post_chat"),
    path("chat/list/", ChatListView.as_view(), name = "get_chat_list"),
    path("chat/<int:id>/", ChatListView.as_view(), name="get_chat"),
]