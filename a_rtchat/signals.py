from .models import GroupMessage 
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save


@receiver(post_save, sender=GroupMessage)
def send_notification(sender, instance, created, **kwargs):
    if created:
        print("a new message has been created")
        group = instance.group
        author = instance.author
        message_body = instance.body

        users_to_notify = group.users_online.exclude(id=author.id)
        print(users_to_notify)
        for user in users_to_notify:
            # Replace this with your notification mechanism (e.g., WebSocket, email, etc.)
            print(f"Notification: {user.username}, you have a new message in {group.group_name} from {author.username}: {message_body}")

