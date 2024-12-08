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
        
        async_to_sync(self.channel_layer.group_add(
            self.chatroom_name, self.channel_name
        ))
        
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard(
            self.chatroom_name, self.channel_name
        ))

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

        async_to_sync(self.channel_layer.group_add(
            self.chatroom_name, event
        ))

    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        
        context = {
            'message': message,
            'user': self.user
        }

        html = render_to_string("a_rtchat/partials/chat_message_p.html", context = context)
        self.send(text_data=html) 
