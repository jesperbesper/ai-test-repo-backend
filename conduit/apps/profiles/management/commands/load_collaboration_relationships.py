"""
Management command to load sample collaboration relationships and follow networks for collaborative editing spec.
"""
from django.core.management.base import BaseCommand
from conduit.apps.profiles.models import Profile
from conduit.apps.authentication.models import User


class Command(BaseCommand):
    help = "Load sample follow relationships simulating a collaboration network"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Loading collaboration relationships..."))

        # Get users and profiles
        users = {
            username: User.objects.filter(username=username).first()
            for username in ["alice", "bob", "charlie", "diana", "eve"]
        }

        if not all(users.values()):
            self.stdout.write(
                self.style.ERROR("Error: Please run 'load_users' command first")
            )
            return

        profiles = {
            username: Profile.objects.get(user=user)
            for username, user in users.items()
        }

        created_count = 0

        # Define collaboration follow relationships
        # These represent authors who frequently collaborate on articles
        follow_relationships = [
            # Alice follows her active collaborators
            ("alice", "bob"),      # Alice follows Bob
            ("alice", "charlie"),  # Alice follows Charlie
            ("alice", "diana"),    # Alice follows Diana
            ("alice", "eve"),      # Alice follows Eve

            # Bob follows his collaborators
            ("bob", "alice"),      # Bob follows Alice
            ("bob", "charlie"),    # Bob follows Charlie
            ("bob", "diana"),      # Bob follows Diana

            # Charlie follows his collaborators
            ("charlie", "alice"),  # Charlie follows Alice
            ("charlie", "bob"),    # Charlie follows Bob
            ("charlie", "eve"),    # Charlie follows Eve

            # Diana follows her collaborators
            ("diana", "alice"),    # Diana follows Alice
            ("diana", "bob"),      # Diana follows Bob
            ("diana", "eve"),      # Diana follows Eve

            # Eve follows her collaborators
            ("eve", "alice"),      # Eve follows Alice
            ("eve", "bob"),        # Eve follows Bob
            ("eve", "charlie"),    # Eve follows Charlie
        ]

        # Create follow relationships
        for follower_name, following_name in follow_relationships:
            follower = profiles[follower_name]
            following = profiles[following_name]

            if not follower.is_following(following):
                follower.follow(following)
                created_count += 1
                self.stdout.write(f"  {follower_name} now follows {following_name}")
            else:
                self.stdout.write(
                    f"  {follower_name} already follows {following_name}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully loaded {created_count} new follow relationships"
            )
        )
