"""
Management command to load sample users and profiles for collaborative article editing spec.
"""
from django.core.management.base import BaseCommand
from conduit.apps.authentication.models import User, UserNotification, UserPreference
from conduit.apps.profiles.models import Profile, ProfileStatistics


class Command(BaseCommand):
    help = "Load sample users and profiles for testing collaborative editing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Loading sample users..."))

        # Create sample users
        users_data = [
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "securepass123",
                "bio": "Tech writer and collaborative author"
            },
            {
                "username": "bob",
                "email": "bob@example.com",
                "password": "securepass123",
                "bio": "Content editor and reviewer"
            },
            {
                "username": "charlie",
                "email": "charlie@example.com",
                "password": "securepass123",
                "bio": "Data analyst and contributor"
            },
            {
                "username": "diana",
                "email": "diana@example.com",
                "password": "securepass123",
                "bio": "Product manager and writer"
            },
            {
                "username": "eve",
                "email": "eve@example.com",
                "password": "securepass123",
                "bio": "Developer and technical writer"
            }
        ]

        created_count = 0
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                email=user_data["email"],
                defaults={"is_active": True, "is_staff": False}
            )

            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(f"  Created user: {user.username}")
                created_count += 1

                # Create profile
                profile, _ = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        "bio": user_data["bio"],
                        "image": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.username}"
                    }
                )

                # Create profile statistics
                ProfileStatistics.objects.get_or_create(
                    profile=profile,
                    defaults={
                        "total_articles": 0,
                        "total_comments": 0,
                        "total_followers": 0,
                        "total_following": 0,
                        "total_article_views": 0,
                        "total_likes_received": 0
                    }
                )

                # Create user preferences
                UserPreference.objects.get_or_create(
                    user=user,
                    defaults={
                        "email_on_new_follower": True,
                        "email_on_comment": True,
                        "email_on_mention": True,
                        "email_newsletter": False,
                        "theme": "auto",
                        "language": "en",
                        "articles_per_page": 10,
                        "show_email": False,
                        "show_reading_list": True,
                        "allow_indexing": True
                    }
                )
            else:
                self.stdout.write(f"  User already exists: {user.username}")

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully loaded {created_count} new users")
        )
