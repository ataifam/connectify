from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError

#create post
class Post(models.Model):
    user = models.ForeignKey(
        User, related_name="posts",
        on_delete=models.DO_NOTHING
    )
    body=models.CharField(max_length=200)
    time = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(User, related_name="upvote", blank=True)
    downvotes = models.ManyToManyField(User, related_name="downvote", blank=True)
    edited = models.BooleanField(null=False, default=False)

    def score(self):
        return self.upvotes.count() - self.downvotes.count()
    def __str__(self):
        return (
                f"{self.body}"
        )
    
class Comments(models.Model):
    user = models.ForeignKey(
        User, related_name="comments",
        on_delete=models.DO_NOTHING
    )
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE, blank=True, null=True)
    content=models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
                f"{self.content}"
        )
    
#create a model profile for users
class Profile(models.Model):
    #one to one relationship between any user and profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #profiles can follow any amount users
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True,)

    profile_pic = models.ImageField(null=True, blank=True, upload_to="images/")

    bio = models.TextField(blank=True, editable=True, max_length=50)

    last_seen = models.DateTimeField(User, auto_now=True)

    def __str__(self):
        return self.user.username
    
#new profile whenever a new user registers
@receiver(post_save, sender=User)
def NewProfile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()