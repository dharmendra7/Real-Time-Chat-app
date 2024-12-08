from channels.generic.websocket import WebsocketConsumer
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from .models import *
import json

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope.get('user')
        self.chatroom_name = self.scope.get('url_route').get('kwargs').get('chatroom_name')
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        print(self.chatroom)
        
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        # add and update online users
        print(f"{self.chatroom.users_online.all() = }")
        print(f"{self.user = }")
        if self.user not in self.chatroom.users_online.all():
            print("working this block")
            self.chatroom.users_online.add(self.user)
            self.update_online_count()
        
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard(
            self.chatroom_name, self.channel_name
        ))
        
        # remove and update online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    def receive(self, text_data=None): # This method will receive the data from the form
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        
        message = GroupMessage.objects.create(
            body=body,
            author=self.user,
            group=self.chatroom
        )

        event = {
            'type':'message_handler',
            'message_id': message.id
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        
        context = {
            'message': message,
            'user': self.user
        }

        html = render_to_string("a_rtchat/partials/chat_message_p.html", context = context)
        self.send(text_data=html) 

    def update_online_count(self):
        online_count = self.chatroom.users_online.count() - 1

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        print("working")
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def online_count_handler(self, event):
        print("working")
        online_count = event['online_count']
        html = render_to_string("a_rtchat/partials/online_count.html", {'online_count': online_count})
        self.send(text_data=html)
        
