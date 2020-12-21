from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile,Account,Comment,Notification_Manual
from django.urls import reverse
# from django.contrib.auth import get_user_model
from django.core.mail import mail_admins
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.contrib import messages 
# from notifications.signals import notify

# User = get_user_model() 

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
	instance.profile.save()

@receiver(post_save, sender=Comment)
def comment_created_email_notification(sender, instance,created,*args, **kwargs):
	if created:
		user = instance.user
		# i = instance.content_type
		# c = ContentType.objects.get_for_model(i.__class__)
		# j = c.objects.get(id=instance.object_id)

		# p = instance.content_type.__class__.objects.get(slug=instance.content_object.slug)


		# url = instance.content_type.__class____.get_absolute_url

		# notify.send(sender=instance,recipient=instance.parent.user, verb='new comment')

		Notification_Manual.objects.create(
			user=instance.user,
			sender = instance.user,
			content=instance.content,
			post_url=instance.content_object.get_absolute_url()
		)


# @receiver(post_save, sender=Comment)
# def comment_created_email_notification(sender, instance,created,*args, **kwargs):
#     if created:
#          mail_admins(
#          	f'New comment from {instance.user.username} on {instance.timestamp}',
#          	f'{instance.content}'
#          )