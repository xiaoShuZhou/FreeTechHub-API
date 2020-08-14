from .models import User
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, FollowershipSerializer
from .serializers import FriendRequestSerializer, FriendshipSerializer
from .models import User, Followership, FriendRequest, Friendship
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
    ]


class GetSelfView(APIView):
    """
    get the request user model
    """
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        user = self.get_object(request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class FollowershipViewSet(viewsets.ModelViewSet):
    queryset = Followership.objects.all()
    serializer_class = FollowershipSerializer
    permission_classes = [
            IsAuthenticated,
        ]


class FollowershowView(APIView):
    renderer_classes = [JSONRenderer]

# Gets a list of follower for the relevant user
    def get(self, request, format=None):
        response = {'status': 100, 'data': None}
        user = self.request.user
        followers = Followership.objects.filter(following_id=user.id)
        followerList = []
        for follower in followers:
            followerList.append({'follower_name':follower.follower.username,
            'user_bio':follower.follower.bio,'id':follower.follower.pk})
        response['data'] = followerList
        return JsonResponse(response, safe=False)


class FollowingshowView(APIView):
    renderer_classes = [JSONRenderer]

# Gets a list of following for the relevant user
    def get(self, request, format=None):
        response = {'status': 100, 'data': None}
        user = self.request.user
        followings = Followership.objects.filter(follower_id=user.id)

        followingList = []
        for following in followings:
            followingList.append({'following_id':following.id,
            'following_name':following.following.username,
            'user_bio':following.following.bio,'id':following.following.pk})
        response['data'] = followingList
        return JsonResponse(response, safe=False)


class ChangePasswordView(APIView):
    queryset = User.objects.all()
    renderer_classes = [JSONRenderer]

    # ChangePassword
    def post(self, request, format=None):
        response = {'status': 100, 'data': None}
        data = request.data
        old_password = data.get('oldpassword')
        new_password = data.get('newpassword1')
        user = self.request.user
        if user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            context = {
                "status": 100,
                "msg": "successful"
            }
        else:
            context = {
                "status": 500,
                "msg": "error"
            }
        response['data'] = context
        return JsonResponse(response, safe=False)


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer


class GetRequestView(APIView):

    def get(self, request, format=None):
        user = User.objects.filter(id=request.user.id)
        all_requests = FriendRequest.objects.filter(to_user_id=request.user.id,
        is_cancel=False)
        all_related_request = {}
        all_related_request['request'] = [FriendRequestSerializer(request).data for request in all_requests]
        return Response(all_related_request)


class GetFriendsView(APIView):

    def get(self, request, user_id, format=None):
        user = User.objects.get(id=user_id)

        # because this user could be friend_1 or friend_2 of some
        # Friendship, therefore we are getting all the relavent.
        relavent_friendships_1 = Friendship.objects.filter(friend_1=user)
        relavent_friendships_2 = Friendship.objects.filter(friend_2=user)
        relavent_friendships = relavent_friendships_1 | relavent_friendships_2

        serialized_friends = []
        for friendship in relavent_friendships:
            if friendship.friend_1 == user:
                # if user is friend_1 in a friendship
                # then friend_2 is this user's friend.
                serialized_friends.append(
                    UserSerializer(friendship.friend_2).data
                )
            else:
                serialized_friends.append(
                    UserSerializer(friendship.friend_1).data
                )
        
        return Response(serialized_friends)
        

# Chat system
from asgiref.sync import sync_to_async
from .models import Chat, Message
from .serializers import MessageSerializer, ChatSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer


class GetRequestView(APIView):

    def get(self, request, format=None):
        user = User.objects.filter(id=request.user.id)
        all_requests = FriendRequest.objects.filter(to_user_id=request.user.id,
        is_cancel=False)
        all_related_request = {}
        all_related_request['request'] = [FriendRequestSerializer(request).data for request in all_requests]
        return Response(all_related_request)


class GetChatView(APIView):

    def get(self, request, format=None, **kwargs):
        sender   = self.request.query_params.get('sender', None)
        receiver = self.request.query_params.get('receiver', None)

        try:
            chat = Chat.objects.get(user1_id=sender,
                                    user2_id=receiver)

        except Chat.DoesNotExist:
            chat, _ = Chat.objects.get_or_create(user1_id=receiver,
                                                 user2_id=sender)

        return Response(ChatSerializer(chat).data)


async def WebsocketView(socket, live_sockects):
    await socket.accept()
    sender_id = None

    while True:
        message = await socket.receive_json()

        # socket.receive_json() will return None if the massage
        # if the message is to disconnect.
        if message == None:
            live_sockects.checkout(socket)
            break
        
        sender_id = message['sender_id']
        if message.get('register') == True:
            live_sockects.register(sender_id, socket)
            continue
        
        try:
            chat = await sync_to_async(
                Chat.objects.get
            )(user1_id=message['sender_id'], user2_id=message['receiver_id'])

        except Chat.DoesNotExist:
            chat, _ = await sync_to_async(
                Chat.objects.get_or_create
            )(user1_id=message['receiver_id'], user2_id=message['sender_id'])

        msg = await sync_to_async(Message.objects.create)(
            belonging_chat=chat,
            content=message['message'],
            sender_id=sender_id
        )

        msg = MessageSerializer(msg).data
        await socket.send_json(msg)

        # live_sockects.get_socket will return None if 
        # not find a match user in the list
        receiver_socket = live_sockects.get_socket(message['receiver_id'])
        # if receiver_socket == None means the receiver 
        # is not online or at message page
        if receiver_socket != None:
            await receiver_socket.send_json(msg)
