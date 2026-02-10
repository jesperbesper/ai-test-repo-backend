# Generated migration for new models

from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_auto_20160828_1656'),
        ('profiles', '0003_profile_favorites'),
    ]

    operations = [
        # Add new fields to Article model
        migrations.AddField(
            model_name='article',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='article',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='article',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        
        # Add fields to Comment model
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='replies', to='articles.Comment'
            ),
        ),
        migrations.AddField(
            model_name='comment',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
        
        # Create Category model
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                    related_name='subcategories', to='articles.Category'
                )),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['order', 'name'],
            },
        ),
        
        # Add category field to Article
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='articles', to='articles.Category'
            ),
        ),
        
        # Create ArticleRevision model
        migrations.CreateModel(
            name='ArticleRevision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('body', models.TextField()),
                ('revision_note', models.TextField(blank=True)),
                ('version_number', models.IntegerField()),
                ('article', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='revisions', to='articles.Article'
                )),
                ('edited_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='article_edits', to='profiles.Profile'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='articlerevision',
            unique_together={('article', 'version_number')},
        ),
        
        # Create ArticleRating model
        migrations.CreateModel(
            name='ArticleRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])),
                ('review', models.TextField(blank=True)),
                ('article', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ratings', to='articles.Article'
                )),
                ('profile', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='article_ratings', to='profiles.Profile'
                )),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='articlerating',
            unique_together={('article', 'profile')},
        ),
        
        # Create BookmarkCollection model
        migrations.CreateModel(
            name='BookmarkCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('color', models.CharField(default='#667eea', max_length=7)),
                ('articles', models.ManyToManyField(
                    blank=True, related_name='in_collections', to='articles.Article'
                )),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='bookmark_collections', to='profiles.Profile'
                )),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Create ReadingList model
        migrations.CreateModel(
            name='ReadingList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('priority', models.IntegerField(
                    default=3,
                    validators=[MinValueValidator(1), MaxValueValidator(5)],
                    help_text='1=Low, 5=High'
                )),
                ('notes', models.TextField(blank=True)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('article', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='in_reading_lists', to='articles.Article'
                )),
                ('profile', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reading_list', to='profiles.Profile'
                )),
            ],
            options={
                'ordering': ['-priority', '-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='readinglist',
            unique_together={('profile', 'article')},
        ),
    ]
