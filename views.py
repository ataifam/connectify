from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Post, Comments
from .forms import PostForm, SignUpForm, SettingsForm, ChangePasswordForm, PicForm, CommentForm, Captcha
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

@login_required(login_url="social:login")
def home(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.all()
        # query user's connection count
        connections = get_object_or_404(Profile, user_id=request.user.id).follows.filter(follows=request.user.profile)
        # load all posts in reverse order (most recent)
        posts = Post.objects.all().order_by("-time")[0:20]
        # load post form for the user to make a post
        form = PostForm()
        # load comment form for user to make comments
        commentForm = CommentForm()
        # user made a post
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                # modify post user to current user
                post.user = request.user
                # save post to db
                post.save()
                return redirect('social:home')
                
        return render(request, "social/home.html", {
            "posts": posts,
            "form": form,
            "commentForm": commentForm,
            "connections": connections,
            "profiles": profiles,
            })
    else:
        # show link to login
        return render(request, "social/home.html", {})

def login_user(request):
    captcha = Captcha
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        captcha = Captcha(request.POST)
        user = authenticate(request, username=username, password=password)
        if user is not None and captcha.is_valid():
            login(request, user)
            return redirect('social:home')
        else:
            messages.error(request, 'Error logging in. Please try again.')
            return redirect('social:login')
            
    else:
        return render(request, 'social/pagetologin.html', {'captcha': captcha})

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('social:login')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration Successful!")
            return redirect('social:home')
        
        messages.error(request, "An error has occured. Please try again!")
        return redirect('social:register')

    return render(request, 'social/register_user.html', {
        'form': form,
    })

def connections(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.all()
        # get user's profile
        profile = get_object_or_404(Profile, user_id=request.user.id)
        # get user's connections
        connections = profile.follows.filter(follows=request.user.profile)
        return render(request, "social/connections.html", {
            "profile": profile,
            "connections": connections,
            "profiles": profiles,
        })
    # show link to login
    return render(request, "social/connections.html", {})

def profile(request, pk):
    if request.user.is_authenticated:
        # current user
        user = get_object_or_404(User, id=request.user.id)
        # profile being accessed
        profile = get_object_or_404(Profile, user_id=pk)
        # the posts of the profile being accessed
        posts = Post.objects.filter(user_id=pk).order_by("-time")[0:20]
        # query user's connection count
        connections = get_object_or_404(Profile, user_id=request.user.id).follows.filter(follows=request.user.profile)
        # all profiles
        profiles = Profile.objects.all()

        # forms for user's profile ONLY!
        bioForm = SettingsForm(instance=user.profile)
        passwordForm = ChangePasswordForm(instance=user)
        picForm = PicForm(instance=user.profile)

        # for post modifying
        postForm = PostForm()

        # comment form for all profiles
        commentForm = CommentForm()

        # 3 possible forms may have been used on this page, identifier sent with request via html form
        if request.method == "POST":
            bioForm = SettingsForm(request.POST, instance=user.profile)
            passwordForm = ChangePasswordForm(request.POST or None, request.FILES or None, instance=user)
            picForm = PicForm(request.POST or None, request.FILES or None, instance=user.profile)
            # user used change bio form
            if 'new-bio' in request.POST:
                if bioForm.is_valid():
                    bioForm.save()
                    messages.success(request, ("Bio saved!"))
                    return redirect('social:profile', request.user.id)
            # user used change pass form
            elif 'new-pass' in request.POST:
                if passwordForm.is_valid():
                    passwordForm.save()
                    login(request, user)
                    messages.success(request, ("Password changed!"))
                    return redirect('social:profile', request.user.id)
            # user used change pic form
            elif 'new-pic':
                if picForm.is_valid():
                    picForm.save()
                    messages.success(request, ("Profile picture saved!"))
                    return redirect('social:profile', request.user.id)
            messages.error(request, ("An error has occured. Please try again!"))
            return redirect('social:profile', request.user.id)


        return render(request, "social/profile.html", {
            "profile": profile,
            "posts":posts,
            'bioForm':bioForm,
            'passwordForm':passwordForm,
            'picForm': picForm,
            'commentForm': commentForm,
            'postForm': postForm,
            'profiles': profiles,
            'connections': connections
        })
    
    # show link to login
    return render(request, "social/profile.html", {})

def search(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.all()
        # check for valid input
        q = request.GET.get('q') if bool(request.GET.get('q', False)) else None
        if q is not None:
            try:
                profile = Profile.objects.get(user__username=q) 
                return redirect('social:profile', profile.user.id)
            except Profile.DoesNotExist:
                profiles = Profile.objects.filter(user__username__icontains=q)[0:50]
        else:
            messages.error(request, "Invalid search entry. Please try again!")
        return render(request, "social/search.html", {
            'profiles': profiles,
        })
    else:
         # show link to login
        return render(request, "social/search.html", {})


@login_required(login_url="social:login")
def follow(request, pk):
        # current user
        user = get_object_or_404(User, id=request.user.id)
        # profile being accessed
        profile = get_object_or_404(Profile, user_id=pk)

        if request.method == "POST":
                # first check if user is attempting to follow themself
                if(request.user.id == profile.user.id):
                    messages.error(request, ("You cannot follow yourself!"))
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                action = request.POST.get('follow', '')
                if action == "unfollow":
                    # user stops following the current profile
                    user.profile.follows.remove(profile)
                elif action == "follow":
                    # user starts following the current profile
                    user.profile.follows.add(profile)
                # save modifications to user's follow list
                user.save()
                return redirect(request.META.get('HTTP_REFERER', '/'))  
        # if process fails for any reason, return error    
        messages.error(request, ("An error occured. Please try again!"))
        return redirect(request.META.get('HTTP_REFERER', '/'))

    
# users can vote via multiple pages so add its own view
@login_required(login_url="social:login")
def vote(request, pk):
        # get parent post
        post = get_object_or_404(Post, id=pk)
        # upvote branch
        if request.method == "POST":
                action = request.POST.get('vote', '')
                if action == 'up':
                    # if the user already upvoted this post, remove the upvote
                    if post.upvotes.filter(id=request.user.id):
                        post.upvotes.remove(request.user)
                    # if the user hasn't upvoted the post, add the vote
                    else:
                        post.upvotes.add(request.user)
                        # if the user previously downvoted this post, remove that vote
                        if post.downvotes.filter(id=request.user.id):
                            post.downvotes.remove(request.user)
                # downvote branch
                elif action == 'down':
                    # if the user already downvoted this post, remove the downvote
                    if post.downvotes.filter(id=request.user.id):
                        post.downvotes.remove(request.user)
                    # if the user hasn't downvoted the post, add the downvote
                    else:
                        post.downvotes.add(request.user)
                        # if the user previously upvoted this post, remove that vote
                        if post.upvotes.filter(id=request.user.id):
                            post.upvotes.remove(request.user)

        # redirect user to the page they were on
        return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url="social:login")   
def comment(request, pk):
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                # set commenter to the current user
                comment.user = request.user
                comment.save()
                # add the comment to the parent post
                get_object_or_404(Post, id=pk).comments.add(comment)
            else:
                messages.error(request, ("An error has occured. Please try again!"))
            return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url="social:login")
def updatePost(request, pk):
        if request.method == 'POST':
            post = get_object_or_404(Post, id=pk)
            if post.user.id != request.user.id:
                messages.error(request, ("You cannot edit other users' posts!"))
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                form = PostForm(request.POST or None, instance=post)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.edited = True
                    post.save()
                    messages.success(request, ("Post updated successfully"))
                    return redirect(request.META.get('HTTP_REFERER', '/'))
        messages.error(request, ("An error occured. Please try again!"))
        return redirect('social:home')

@login_required(login_url="social:login")
def deletePost(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=pk)
        if post.user.id != request.user.id:
                messages.error(request, ("You cannot delete other users' posts!"))
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            post.delete()
            messages.success(request, ("Post deleted successfully"))
            return redirect(request.META.get('HTTP_REFERER', '/'))
    messages.error(request, ("An error occured. Please try again!"))
    return redirect('social:home')
        

    