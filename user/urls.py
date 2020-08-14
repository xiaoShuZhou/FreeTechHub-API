from django.urls import path, include
from rest_framework import routers
from user  import views


router = routers.DefaultRouter()
router.register('user', views.UserViewSet)
router.register('followership', views.FollowershipViewSet)
router.register('friendrequest', views.FriendRequestViewSet)
router.register('friendship', views.FriendshipViewSet)
router.register('message', views.MessageViewSet)
router.register('chat', views.ChatViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('getself/', views.GetSelfView.as_view()),
    path('getfollowing/', views.FollowingshowView.as_view()),
    path('getfollower/', views.FollowershowView.as_view()),
    path('changepassword/', views.ChangePasswordView.as_view()),
    path('getrequest/', views.GetRequestView.as_view()),
    path('getfriends/<int:user_id>/', views.GetFriendsView.as_view()),
    path('getchat/', views.GetChatView.as_view()),
]
