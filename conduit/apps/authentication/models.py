import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models

from conduit.apps.core.models import TimestampedModel


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free. 

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, username, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
      """
      Create and return a `User` with superuser powers.

      Superuser powers means that this use is an admin that can do anything
      they want.
      """
      if password is None:
          raise TypeError('Superusers must have a password.')

      user = self.create_user(username, email, password)
      user.is_superuser = True
      user.is_staff = True
      user.save()

      return user


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a user no longer wishes to use our platform, they may try to delete
    # there account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. To solve this problem, we
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users, this flag will always be
    # falsed.
    is_staff = models.BooleanField(default=False)

    # More fields required by Django when specifying a custom user model.

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case, we want that to be the email field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
      """
      This method is required by Django for things like handling emails.
      Typically, this would be the user's first and last name. Since we do
      not store the user's real name, we return their username instead.
      """
      return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')


class UserNotification(models.Model):
    """Notifications for user activities."""
    NOTIFICATION_TYPES = (
        ('follow', 'New Follower'),
        ('comment', 'New Comment'),
        ('like', 'Article Liked'),
        ('mention', 'Mentioned'),
        ('rating', 'Article Rated'),
        ('reply', 'Comment Reply'),
    )

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    
    actor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications',
        null=True, blank=True
    )
    
    link = models.CharField(max_length=255, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"


class UserSession(models.Model):
    """Track user login sessions for security."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sessions'
    )
    
    session_token = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"


class UserActivityLog(models.Model):
    """Log user activities for analytics."""
    ACTIVITY_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('article_view', 'Article View'),
        ('article_create', 'Article Create'),
        ('article_edit', 'Article Edit'),
        ('article_delete', 'Article Delete'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='activity_logs'
    )
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.TextField(blank=True)  # JSON data
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class UserPreference(models.Model):
    """Store user preferences and settings."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='preferences'
    )
    
    # Email preferences
    email_on_new_follower = models.BooleanField(default=True)
    email_on_comment = models.BooleanField(default=True)
    email_on_mention = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    
    # Display preferences
    theme = models.CharField(
        max_length=10, 
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )
    language = models.CharField(max_length=10, default='en')
    articles_per_page = models.IntegerField(default=10)
    
    # Privacy settings
    show_email = models.BooleanField(default=False)
    show_reading_list = models.BooleanField(default=True)
    allow_indexing = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"
