from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Post, Comments

admin.site.unregister(Group)

class UserProfile(admin.StackedInline):
    model = Profile

#user is defined just by username
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [UserProfile]

admin.site.unregister(User)

admin.site.register(User, UserAdmin)

admin.site.register(Post)

admin.site.register(Comments)