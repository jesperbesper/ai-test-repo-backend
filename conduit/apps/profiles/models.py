from django.db import models

from conduit.apps.core.models import TimestampedModel


class Profile(TimestampedModel):
    # As mentioned, there is an inherent relationship between the Profile and
    # User models. By creating a one-to-one relationship between the two, we
    # are formalizing this relationship. Every user will have one -- and only
    # one -- related Profile model.
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )

    # Each user profile will have a field where they can tell other users
    # something about themselves. This field will be empty when the user
    # creates their account, so we specify `blank=True`.
    bio = models.TextField(blank=True)

    # In addition to the `bio` field, each user may have a profile image or
    # avatar. Similar to `bio`, this field is not required. It may be blank.
    image = models.URLField(blank=True)

    # This is an example of a Many-To-Many relationship where both sides of the
    # relationship are of the same model. In this case, the model is `Profile`.
    # As mentioned in the text, this relationship will be one-way. Just because
    # you are following mean does not mean that I am following you. This is
    # what `symmetrical=False` does for us.
    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False
    )

    favorites = models.ManyToManyField(
        'articles.Article',
        related_name='favorited_by'
    )


    def __str__(self):
        return self.user.username

    def follow(self, profile):
        """Follow `profile` if we're not already following `profile`."""
        self.follows.add(profile)

    def unfollow(self, profile):
        """Unfollow `profile` if we're already following `profile`."""
        self.follows.remove(profile)

    def is_following(self, profile):
        """Returns True if we're following `profile`; False otherwise."""
        return self.follows.filter(pk=profile.pk).exists()

    def is_followed_by(self, profile):
        """Returns True if `profile` is following us; False otherwise."""
        return self.followed_by.filter(pk=profile.pk).exists()

    def favorite(self, article):
        """Favorite `article` if we haven't already favorited it."""
        self.favorites.add(article)

    def unfavorite(self, article):
        """Unfavorite `article` if we've already favorited it."""
        self.favorites.remove(article)

    def has_favorited(self, article):
        """Returns True if we have favorited `article`; else False."""
        return self.favorites.filter(pk=article.pk).exists()


class ProfileStatistics(models.Model):
    """Cache profile statistics for performance."""
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name='statistics'
    )
    
    total_articles = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    total_followers = models.IntegerField(default=0)
    total_following = models.IntegerField(default=0)
    total_article_views = models.IntegerField(default=0)
    total_likes_received = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profile.user.username} - Statistics"


class FollowRequest(models.Model):
    """Manage follow requests for private profiles."""
    from_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='sent_follow_requests'
    )
    
    to_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='received_follow_requests'
    )
    
    message = models.TextField(blank=True, max_length=500)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['from_profile', 'to_profile']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_profile.user.username} -> {self.to_profile.user.username}"


class Badge(models.Model):
    """Achievement badges for users."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    
    # Requirements
    required_articles = models.IntegerField(default=0)
    required_followers = models.IntegerField(default=0)
    required_comments = models.IntegerField(default=0)
    
    # Badge properties
    rarity = models.CharField(
        max_length=10,
        choices=[
            ('common', 'Common'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary')
        ],
        default='common'
    )
    
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ProfileBadge(models.Model):
    """Track which badges profiles have earned."""
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='earned_badges'
    )
    
    badge = models.ForeignKey(
        Badge, on_delete=models.CASCADE, related_name='awarded_to'
    )
    
    earned_at = models.DateTimeField(auto_now_add=True)
    is_displayed = models.BooleanField(default=True)

    class Meta:
        unique_together = ['profile', 'badge']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.profile.user.username} - {self.badge.name}"


class UserBlocking(models.Model):
    """Allow users to block other users."""
    blocker = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='blocking'
    )
    
    blocked = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='blocked_by'
    )
    
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['blocker', 'blocked']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.blocker.user.username} blocked {self.blocked.user.username}"
