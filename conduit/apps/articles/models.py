from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from conduit.apps.core.models import TimestampedModel


class Article(TimestampedModel):
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    title = models.CharField(db_index=True, max_length=255)

    description = models.TextField()
    body = models.TextField()

    # Every article must have an author. This will answer questions like "Who
    # gets credit for writing this article?" and "Who can edit this article?".
    # Unlike the `User` <-> `Profile` relationship, this is a simple foreign
    # key (or one-to-many) relationship. In this case, one `Profile` can have
    # many `Article`s.
    author = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='articles'
    )

    tags = models.ManyToManyField(
        'articles.Tag', related_name='articles'
    )

    category = models.ForeignKey(
        'articles.Category', on_delete=models.SET_NULL, 
        related_name='articles', null=True, blank=True
    )

    view_count = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comment(TimestampedModel):
    body = models.TextField()

    article = models.ForeignKey(
        'articles.Article', related_name='comments', on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        'profiles.Profile', related_name='comments', on_delete=models.CASCADE
    )

    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies'
    )

    is_edited = models.BooleanField(default=False)


class Tag(TimestampedModel):
    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return self.tag


class Category(TimestampedModel):
    """Hierarchical categories for organizing articles."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subcategories'
    )
    
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ArticleRevision(TimestampedModel):
    """Track article edit history for version control."""
    article = models.ForeignKey(
        'articles.Article', on_delete=models.CASCADE, related_name='revisions'
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()
    
    edited_by = models.ForeignKey(
        'profiles.Profile', on_delete=models.SET_NULL, 
        null=True, related_name='article_edits'
    )
    
    revision_note = models.TextField(blank=True)
    version_number = models.IntegerField()

    class Meta:
        ordering = ['-created_at']
        unique_together = ['article', 'version_number']

    def __str__(self):
        return f"{self.article.title} - v{self.version_number}"


class ArticleRating(TimestampedModel):
    """Allow users to rate articles on a scale."""
    article = models.ForeignKey(
        'articles.Article', on_delete=models.CASCADE, related_name='ratings'
    )
    
    profile = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='article_ratings'
    )
    
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    review = models.TextField(blank=True)

    class Meta:
        unique_together = ['article', 'profile']

    def __str__(self):
        return f"{self.profile.user.username} rated {self.article.title}: {self.score}/5"


class BookmarkCollection(TimestampedModel):
    """Collections for organizing bookmarked articles."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    owner = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, 
        related_name='bookmark_collections'
    )
    
    articles = models.ManyToManyField(
        'articles.Article', related_name='in_collections', blank=True
    )
    
    is_public = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#667eea')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.owner.user.username}'s {self.name}"


class ReadingList(TimestampedModel):
    """Track articles that users plan to read later."""
    profile = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='reading_list'
    )
    
    article = models.ForeignKey(
        'articles.Article', on_delete=models.CASCADE, related_name='in_reading_lists'
    )
    
    priority = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=Low, 5=High"
    )
    
    notes = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['profile', 'article']
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.profile.user.username} - {self.article.title}"
