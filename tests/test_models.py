from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from social.models import Post, Comments, Profile
from django.utils import timezone
from django.urls import reverse
import datetime
import random as r

class ProfileTestCase(TestCase):
    def setUp(self):
        # test users
        User.objects.create_user(username="thezebraman2", password="ilovesecurity!#888")
        User.objects.create_user(username="thelizardman2", password="ilovesecurity!#888")
        User.objects.create_user(username="thegopherman2", password="ilovesecurity!#888")

    def testProfileMade(self):
        # query test user
        user = User.objects.get(username="thezebraman2")
        # access user's profile field
        profile = user.profile
        self.assertIsNotNone(profile)
        # bio should be empty
        self.assertTrue(not profile.bio)
        # profile pic should be empty
        self.assertTrue(not profile.profile_pic)
        self.assertIsNotNone(profile.last_seen)

    def testModifyProfile(self):
        # query test user
        user = User.objects.get(username="thezebraman2")
        # access user's profile field
        profile = user.profile
        
        # testing tostring method, adding bio field, and setting test profile pic
        self.assertEqual(str(profile), 'thezebraman2')
        profile.bio = "Hi my name is Phil!"
        profile.profile_pic = SimpleUploadedFile(name='test_image.jpg', content=open('social/static/social/default.jpeg', 'rb').read(), content_type='image/jpeg')
        
        # verify validity of updated fields
        self.assertEqual(profile.bio, "Hi my name is Phil!")
        self.assertEqual(profile.profile_pic.name, "test_image.jpg")
        self.assertTrue(profile.last_seen <= datetime.datetime.now(datetime.timezone.utc))

    def testProfileFollowers(self):
        # query test users
        user1 = User.objects.get(username="thezebraman2")
        user2 = User.objects.get(username="thelizardman2")
        user3 = User.objects.get(username="thegopherman2")

        # access test users' profiles
        profile1 = user1.profile
        profile2 = user2.profile
        profile3 = user3.profile

        # add followers to profile1
        profile1.follows.add(profile2)
        profile1.follows.add(profile3)

        # verify existence of profile1's followers
        self.assertListEqual([profile for profile in profile1.follows.all()], [profile2, profile3])

class PostTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username="thezebraman2", password="ilovesecurity!#888")
        User.objects.create_user(username="thelizardman2", password="ilovesecurity!#888")
        User.objects.create_user(username="thegopherman2", password="ilovesecurity!#888")
        User.objects.create_user(username="thekangarooman2", password="ilovesecurity!#888")
        User.objects.create_user(username="therabbitman2", password="ilovesecurity!#888")

    def testMakePost(self):
        # query test user
        user = User.objects.get(username="thezebraman2")

        # verify we start with 0 posts
        self.assertTrue(Post.objects.count() == 0)
        post = Post.objects.create(user=user, body="wahoooooo")
        # verify post registered
        self.assertTrue(Post.objects.count() == 1)
        # testing tostring method
        self.assertEqual(str(post), "wahoooooo")
        # verify post is accessible via poster
        self.assertIsNotNone(Post.objects.get(user=user))

        self.assertTrue(post.time <= datetime.datetime.now(datetime.timezone.utc))
        self.assertFalse(post.edited)

        # verify post upvotes and downvotes are empty upon post creation
        self.assertListEqual([str(upvoter.profile) for upvoter in post.upvotes.all()], [])
        self.assertListEqual([str(downvoter.profile) for downvoter in post.downvotes.all()], [])

    def testVoting(self):
        # query test users
        user1 = User.objects.get(username="thezebraman2")
        user2 = User.objects.get(username="thelizardman2")
        user3 = User.objects.get(username="thegopherman2")
        user4 = User.objects.get(username="thekangarooman2")
        user5 = User.objects.get(username="therabbitman2")

        # test posts
        post = Post.objects.create(user=user1, body="i love zebras!!")

        # add 3 upvotes to post
        post.upvotes.add(user1)
        post.upvotes.add(user2)
        post.upvotes.add(user3)
        # verify existence of users in manytomany upvotes field
        self.assertListEqual([str(upvoter.profile) for upvoter in post.upvotes.all()], [str(user1.profile), str(user2.profile), str(user3.profile)])
        # verify score of 3 (since 3 upvotes - 0 downvotes = 3)
        self.assertTrue(post.score() == 3)
        post.upvotes.clear()

        # add 2 downvotes
        post.downvotes.add(user3)
        post.downvotes.add(user5)
        # verify existence of users in many to many downvotes field
        self.assertListEqual([str(downvoter.profile) for downvoter in post.downvotes.all()], [str(user3.profile), str(user5.profile)])
        # verify score of -2 (since 0 upvotes - 2 downvotes = -2)
        self.assertTrue(post.score() == -2)
        post.downvotes.clear()

        # add 2 upvotes and 2 downvotes
        post.upvotes.add(user1)
        post.downvotes.add(user5)
        post.upvotes.add(user2)
        post.downvotes.add(user4)
        # verify existence of users in manytomany upvote and downvote fields
        self.assertListEqual([str(upvoter.profile) for upvoter in post.upvotes.all()], [str(user1.profile), str(user2.profile)])
        self.assertListEqual([str(downvoter.profile) for downvoter in post.downvotes.all()], [str(user4.profile), str(user5.profile)])
        # verify score is 0 (since 2 upvotes - 2 downvotes = 0)
        self.assertTrue(post.score() == 0)

class CommentTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username="thezebraman2", password="ilovesecurity!#888")
        user2 = User.objects.create_user(username="thelizardman2", password="ilovesecurity!#888")
        user3 = User.objects.create_user(username="thegopherman2", password="ilovesecurity!#888")
        user4 = User.objects.create_user(username="thekangarooman2", password="ilovesecurity!#888")
        user5 = User.objects.create_user(username="therabbitman2", password="ilovesecurity!#888")

        Post.objects.create(user=user1, body="i love zebras!!")
        Post.objects.create(user=user1, body="i am a zebra!")
        Post.objects.create(user=user2, body="i don't know if i like zebras that much")
        Post.objects.create(user=user3, body="gophers will rule the world")
        Post.objects.create(user=user5, body="where did my carrot go??")
        Post.objects.create(user=user5, body="who took my carrot?!?!?!?!")


    def testMakeComment(self):
        # query test user
        user3 = User.objects.get(username="thegopherman2")
        # query first test post
        post = Post.objects.get(id=1)

        # ensure post starts out with 0 comments
        self.assertTrue(post.comments.count() == 0)
        comment = Comments.objects.create(user=user3, post=post, content="lol so true")
        # verify comment registered for post
        self.assertTrue(post.comments.count() == 1)

        # test comment tostring method
        self.assertEqual(str(comment), 'lol so true')


    def testMultipleComments(self):
        # query test users
        user1 = User.objects.get(username="thezebraman2")
        user2 = User.objects.get(username="thelizardman2")
        user3 = User.objects.get(username="thegopherman2")
        user4 = User.objects.get(username="thekangarooman2")
        user5 = User.objects.get(username="therabbitman2")

        # list of users
        users = [user1, user2, user3, user4, user5]
        # list of potential comments
        comments = ['agreed!', 'what??', 'idk man i just like carrots', 'so you say', 'its party time!', 'wow', 'hmmmm', 'where am i?']

        # for all posts, add 4 comments from users randomly selected from users list
        for post in Post.objects.all():
            for i in range(4):
                Comments.objects.create(user=users[r.randint(0, 4)], post=post, content=comments[r.randint(0, 7)])

        # verify 24 comments registered
        self.assertTrue(Comments.objects.count() == 24)
        # verify posts have 4 comments each
        for post in Post.objects.all():
            self.assertTrue(post.comments.count() == 4)

