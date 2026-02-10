# Generated migration for profile models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_profile_favorites'),
    ]

    operations = [
        # Create ProfileStatistics model
        migrations.CreateModel(
            name='ProfileStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_articles', models.IntegerField(default=0)),
                ('total_comments', models.IntegerField(default=0)),
                ('total_followers', models.IntegerField(default=0)),
                ('total_following', models.IntegerField(default=0)),
                ('total_article_views', models.IntegerField(default=0)),
                ('total_likes_received', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('profile', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='statistics', to='profiles.Profile'
                )),
            ],
        ),
        
        # Create FollowRequest model
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, max_length=500)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('accepted', 'Accepted'),
                        ('rejected', 'Rejected'),
                    ],
                    default='pending', max_length=10
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('from_profile', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sent_follow_requests', to='profiles.Profile'
                )),
                ('to_profile', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='received_follow_requests', to='profiles.Profile'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='followrequest',
            unique_together={('from_profile', 'to_profile')},
        ),
        
        # Create Badge model
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('icon', models.CharField(max_length=50)),
                ('required_articles', models.IntegerField(default=0)),
                ('required_followers', models.IntegerField(default=0)),
                ('required_comments', models.IntegerField(default=0)),
                ('rarity', models.CharField(
                    choices=[
                        ('common', 'Common'),
                        ('rare', 'Rare'),
                        ('epic', 'Epic'),
                        ('legendary', 'Legendary')
                    ],
                    default='common', max_length=10
                )),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        
        # Create ProfileBadge model
        migrations.CreateModel(
            name='ProfileBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earned_at', models.DateTimeField(auto_now_add=True)),
                ('is_displayed', models.BooleanField(default=True)),
                ('badge', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='awarded_to', to='profiles.Badge'
                )),
                ('profile', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='earned_badges', to='profiles.Profile'
                )),
            ],
            options={
                'ordering': ['-earned_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='profilebadge',
            unique_together={('profile', 'badge')},
        ),
        
        # Create UserBlocking model
        migrations.CreateModel(
            name='UserBlocking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='blocked_by', to='profiles.Profile'
                )),
                ('blocker', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='blocking', to='profiles.Profile'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='userblocking',
            unique_together={('blocker', 'blocked')},
        ),
    ]
