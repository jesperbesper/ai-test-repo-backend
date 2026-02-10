# Generated migration for authentication models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        # Create UserNotification model
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(
                    choices=[
                        ('follow', 'New Follower'),
                        ('comment', 'New Comment'),
                        ('like', 'Article Liked'),
                        ('mention', 'Mentioned'),
                        ('rating', 'Article Rated'),
                        ('reply', 'Comment Reply'),
                    ],
                    max_length=20
                )),
                ('message', models.TextField()),
                ('link', models.CharField(blank=True, max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                    related_name='sent_notifications', to=settings.AUTH_USER_MODEL
                )),
                ('recipient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications', to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # Create UserSession model
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_token', models.CharField(max_length=255, unique=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sessions', to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-last_activity'],
            },
        ),
        
        # Create UserActivityLog model
        migrations.CreateModel(
            name='UserActivityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(
                    choices=[
                        ('login', 'User Login'),
                        ('logout', 'User Logout'),
                        ('article_view', 'Article View'),
                        ('article_create', 'Article Create'),
                        ('article_edit', 'Article Edit'),
                        ('article_delete', 'Article Delete'),
                        ('profile_update', 'Profile Update'),
                        ('password_change', 'Password Change'),
                    ],
                    max_length=30
                )),
                ('description', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='activity_logs', to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='useractivitylog',
            index=models.Index(fields=['user', '-created_at'], name='authenticat_user_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='useractivitylog',
            index=models.Index(fields=['activity_type', '-created_at'], name='authenticat_activity_created_idx'),
        ),
        
        # Create UserPreference model
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_on_new_follower', models.BooleanField(default=True)),
                ('email_on_comment', models.BooleanField(default=True)),
                ('email_on_mention', models.BooleanField(default=True)),
                ('email_newsletter', models.BooleanField(default=False)),
                ('theme', models.CharField(
                    choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
                    default='auto', max_length=10
                )),
                ('language', models.CharField(default='en', max_length=10)),
                ('articles_per_page', models.IntegerField(default=10)),
                ('show_email', models.BooleanField(default=False)),
                ('show_reading_list', models.BooleanField(default=True)),
                ('allow_indexing', models.BooleanField(default=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='preferences', to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
    ]
