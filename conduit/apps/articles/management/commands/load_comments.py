"""
Management command to load sample comments with threading for collaborative editing spec.
"""
from django.core.management.base import BaseCommand
from conduit.apps.articles.models import Comment, Article
from conduit.apps.profiles.models import Profile
from conduit.apps.authentication.models import User


class Command(BaseCommand):
    help = "Load sample comments with threaded discussions for collaborative editing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Loading sample comments..."))

        # Get or create users
        users = {
            username: User.objects.filter(username=username).first()
            for username in ["alice", "bob", "charlie", "diana", "eve"]
        }

        if not all(users.values()):
            self.stdout.write(
                self.style.ERROR("Error: Please run 'load_users' command first")
            )
            return

        # Get profiles
        profiles = {
            username: Profile.objects.get(user=user)
            for username, user in users.items() if user
        }

        # Get articles
        articles = Article.objects.filter(
            slug__in=[
                "real-time-collaborative-writing",
                "version-control-writers",
                "inline-comments-workflows"
            ]
        )

        if not articles.exists():
            self.stdout.write(
                self.style.ERROR("Error: Please run 'load_articles' command first")
            )
            return

        created_count = 0

        # Comments on "real-time-collaborative-writing" article
        article1 = articles.get(slug="real-time-collaborative-writing")

        # Top-level comment
        comment1, created1 = Comment.objects.get_or_create(
            article=article1,
            author=profiles["diana"],
            body="Great overview! How does conflict resolution work when two users edit the same paragraph?",
            parent=None
        )
        if created1:
            created_count += 1
            self.stdout.write(f"  Created comment by diana on {article1.title}")

            # Reply to comment1
            comment1_reply, created = Comment.objects.get_or_create(
                article=article1,
                author=profiles["bob"],
                body="Good question! The system uses operational transformation to merge concurrent edits. We detect conflicts and show a side-by-side comparison for resolution.",
                parent=comment1
            )
            if created:
                created_count += 1
                self.stdout.write(f"    - Created reply by bob")

            # Another reply to comment1
            comment1_reply2, created = Comment.objects.get_or_create(
                article=article1,
                author=profiles["alice"],
                body="@bob That's exactly right. The system also keeps a version history so users can see what changed and when.",
                parent=comment1
            )
            if created:
                created_count += 1
                self.stdout.write(f"    - Created reply by alice")

        # Another top-level comment
        comment2, created2 = Comment.objects.get_or_create(
            article=article1,
            author=profiles["eve"],
            body="The mention feature is fantastic! Being able to tag specific collaborators makes feedback much clearer.",
            parent=None
        )
        if created2:
            created_count += 1
            self.stdout.write(f"  Created comment by eve on {article1.title}")

            # Reply to comment2
            comment2_reply, created = Comment.objects.get_or_create(
                article=article1,
                author=profiles["charlie"],
                body="@eve Agreed! The @mention notifications ensure that contributors don't miss important feedback.",
                parent=comment2
            )
            if created:
                created_count += 1
                self.stdout.write(f"    - Created reply by charlie")

        # Comments on "version-control-writers" article
        article2 = articles.get(slug="version-control-writers")

        comment3, created3 = Comment.objects.get_or_create(
            article=article2,
            author=profiles["alice"],
            body="This article clearly explains the importance of tracking edits. The revision timeline view is incredibly useful.",
            parent=None
        )
        if created3:
            created_count += 1
            self.stdout.write(f"  Created comment by alice on {article2.title}")

        comment4, created4 = Comment.objects.get_or_create(
            article=article2,
            author=profiles["charlie"],
            body="How do you handle reverting to a previous version? Can editors cherry-pick specific changes?",
            parent=None
        )
        if created4:
            created_count += 1
            self.stdout.write(f"  Created comment by charlie on {article2.title}")

            # Reply to comment4
            comment4_reply, created = Comment.objects.get_or_create(
                article=article2,
                author=profiles["bob"],
                body="@charlie Great question! Users can view any previous revision and selectively restore changes or revert the entire article.",
                parent=comment4
            )
            if created:
                created_count += 1
                self.stdout.write(f"    - Created reply by bob")

        # Comments on "inline-comments-workflows" article
        article3 = articles.get(slug="inline-comments-workflows")

        comment5, created5 = Comment.objects.get_or_create(
            article=article3,
            author=profiles["diana"],
            body="The section about threaded discussions could use more examples. How do you handle resolved vs unresolved discussions?",
            parent=None
        )
        if created5:
            created_count += 1
            self.stdout.write(f"  Created comment by diana on {article3.title}")

            # Reply to comment5
            comment5_reply, created = Comment.objects.get_or_create(
                article=article3,
                author=profiles["alice"],
                body="@diana That's a great suggestion! Discussions can be marked as resolved once the suggestion is implemented.",
                parent=comment5
            )
            if created:
                created_count += 1
                self.stdout.write(f"    - Created reply by alice")

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully loaded {created_count} new comments")
        )
