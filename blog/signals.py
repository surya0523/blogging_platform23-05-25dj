# blog/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Comment

@receiver(post_save, sender=Comment)
def new_comment_notification(sender, instance, created, **kwargs):
    if created:
        post_author_email = instance.post.author.email
        subject = f"New comment on your blog post: '{instance.post.title}'"
        message = (
            f"Hello {instance.post.author.username},\n\n"
            f"A new comment has been added to your post '{instance.post.title}'.\n\n"
            f"Comment by: {instance.user.username}\n"
            f"Comment text: {instance.text}\n\n"
            f"View the post here: http://127.0.0.1:8000{instance.post.get_absolute_url()}"
        )
        from_email = 'your-email@gmail.com'
        recipient_list = [post_author_email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)