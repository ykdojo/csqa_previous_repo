from django.db import models
from users.models import CustomUser, Language
from allauth.socialaccount import app_settings
from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers

# A post made by a user.
class Post(models.Model):
    class Meta:
        ordering = ['-date_posted']

    text_content = models.TextField()

    # The only choice for the source field is "twitter" right now.
    source = models.CharField(max_length=100)

    # If this post was originally created on Twitter, we should
    # store the associated social account.
    # This is for a case like this:
    # User A on Edit Dojo uses @account1 on Twitter to create a post.
    # Then, User A associates their acocunt with another Twitter
    # account, @account2 (maybe for a different language).
    # When that happens, it'll be still good to know which Twitter
    # account this post came from originally.
    associated_social_account = models.ForeignKey(SocialAccount, on_delete=models.SET_NULL, null=True)
    # NOTE: I used app_settings.UID_MAX_LENGTH here to follow the
    # original pattern in django-allauth:
    # https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/app_settings.py

    # Dumb assumption here: the tweet ID is never longer than 100 chars.
    tweet_id_str = models.CharField(max_length=100)

    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_posted = models.DateTimeField()

    def __str__(self):
        return self.posted_by.username + ' - ' + self.text_content

class Sentence(models.Model):
    class Meta:
        ordering = ['parent_post', 'sentence_index']
    
    sentence_index = models.IntegerField()
    text_content = models.TextField()
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return (str(self.parent_post.pk)
                + ' - '
                + str(self.sentence_index)
                + ' - '
                + self.text_content)



class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('short_representation',)

class UserSerializer(serializers.ModelSerializer):
    learning_languages = LanguageSerializer(many=True)
    fluent_languages = LanguageSerializer(many=True)
    class Meta:
        model = CustomUser
        fields = ('username', 'learning_languages', 'fluent_languages')

class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ('uid',)

class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ('sentence_index', 'text_content')

class PostSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer()
    associated_social_account = SocialAccountSerializer()
    sentence_set = SentenceSerializer(many=True)
    class Meta:
        model = Post
        fields = ('text_content', 'posted_by', 'date_posted', 'associated_social_account', 'sentence_set')