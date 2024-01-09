from django import forms
from .models import Post, Profile, Comments
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

class CommentForm(forms.ModelForm):
    content = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={
        "placeholder": "Comment here!",
        "class": "form-control comment-textarea",
        "required": True,
        "rows": 3,
        }),
        label='',
        max_length=100,
        min_length=1
    )

    class Meta:
        model = Comments
        exclude = ("user", "post")

class SignUpForm(UserCreationForm):
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

        def __init__(self, *args, **kwargs):
            super(SignUpForm, self).__init__(*args, **kwargs)

            self.fields['username'].widget.attrs['class'] = 'form-control'
            self.fields['username'].widget.attrs['placeholder'] = 'Username'
            self.fields['username'].widget.attrs['label'] = ''

            self.fields['password1'].widget.attrs['class'] = 'form-control'
            self.fields['password1'].widget.attrs['placeholder'] = 'Password'
            self.fields['password1'].widget.attrs['label'] = ''

            self.fields['password2'].widget.attrs['class'] = 'form-control'
            self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
            self.fields['password2'].widget.attrs['label'] = ''

class PostForm(forms.ModelForm):
    body = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={
        "placeholder": "Write your post here!",
        "class": "form-control post-textarea",
        "required": True,
        "rows": 2,
        }),
        label='',
        max_length=100,
        min_length=1
    )

    class Meta:
        model = Post
        exclude = ("user", "upvotes", "downvotes", "comments", "edited",)

class SettingsForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ("user", "follows", "last_seen", "profile_pic")
        

class ChangePasswordForm(UserCreationForm):
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('password1', 'password2')

        def __init__(self, *args, **kwargs):
            super(SignUpForm, self).__init__(*args, **kwargs)

            self.fields['password1'].widget.attrs['class'] = 'form-control'
            self.fields['password1'].widget.attrs['placeholder'] = 'Password'

            self.fields['password2'].widget.attrs['class'] = 'form-control'
            self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

class PicForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('profile_pic', )

class Captcha(forms.Form):
    captcha = CaptchaField()

