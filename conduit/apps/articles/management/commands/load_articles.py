"""
Management command to load sample articles and revisions for collaborative editing spec.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from conduit.apps.articles.models import Article, ArticleRevision, Tag, Category
from conduit.apps.profiles.models import Profile
from conduit.apps.authentication.models import User


class Command(BaseCommand):
    help = "Load sample articles with revision history for collaborative editing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Loading sample articles..."))

        # Get or create users
        alice = User.objects.filter(username="alice").first()
        bob = User.objects.filter(username="bob").first()
        charlie = User.objects.filter(username="charlie").first()

        if not all([alice, bob, charlie]):
            self.stdout.write(
                self.style.ERROR("Error: Please run 'load_users' command first")
            )
            return

        alice_profile = Profile.objects.get(user=alice)
        bob_profile = Profile.objects.get(user=bob)
        charlie_profile = Profile.objects.get(user=charlie)

        # Create sample categories
        category_names = ["Technology", "Business", "Creative Writing", "Data Science"]
        categories = {}
        for cat_name in category_names:
            cat, _ = Category.objects.get_or_create(
                slug=slugify(cat_name),
                defaults={
                    "name": cat_name,
                    "description": f"Articles about {cat_name}",
                    "is_active": True,
                    "order": list(category_names).index(cat_name)
                }
            )
            categories[cat_name] = cat

        # Create sample tags
        tag_names = ["collaboration", "editing", "real-time", "workflow", "revision"]
        tags = {}
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                slug=slugify(tag_name),
                defaults={"tag": tag_name}
            )
            tags[tag_name] = tag

        # Sample articles data
        articles_data = [
            {
                "title": "Real-Time Collaborative Writing: The Future of Content Creation",
                "slug": "real-time-collaborative-writing",
                "description": "How real-time collaboration transforms the way teams create content",
                "body": "Real-time collaborative editing has revolutionized how teams work together on documents...\n\n" +
                        "In the past, content creation was a linear process: one author writes, others review...\n\n" +
                        "Today, multiple authors can edit simultaneously, see changes instantly, and communicate seamlessly.",
                "author": alice_profile,
                "category": "Technology",
                "tags": ["collaboration", "editing", "real-time"],
                "is_published": True,
                "featured": True,
                "revisions": [
                    {
                        "version": 1,
                        "title": "Real-Time Collaborative Writing",
                        "description": "How collaboration changes content creation",
                        "body": "Real-time editing is the future of content creation.",
                        "edited_by": alice_profile,
                        "revision_note": "Initial draft"
                    },
                    {
                        "version": 2,
                        "title": "Real-Time Collaborative Writing: The Future of Content Creation",
                        "description": "How real-time collaboration transforms the way teams create content",
                        "body": "Real-time collaborative editing has revolutionized how teams work together on documents...",
                        "edited_by": bob_profile,
                        "revision_note": "Expanded introduction and added examples"
                    },
                    {
                        "version": 3,
                        "title": "Real-Time Collaborative Writing: The Future of Content Creation",
                        "description": "How real-time collaboration transforms the way teams create content",
                        "body": "Real-time collaborative editing has revolutionized how teams work together on documents...\n\n" +
                                "In the past, content creation was a linear process: one author writes, others review...\n\n" +
                                "Today, multiple authors can edit simultaneously, see changes instantly, and communicate seamlessly.",
                        "edited_by": charlie_profile,
                        "revision_note": "Added conclusion section"
                    }
                ]
            },
            {
                "title": "Version Control for Writers: Edit History Best Practices",
                "slug": "version-control-writers",
                "description": "Managing article versions and maintaining quality through edit tracking",
                "body": "Just like developers use version control, writers need robust edit history systems...\n\n" +
                        "Each revision should capture who made what changes and why...\n\n" +
                        "This enables transparency and prevents accidental overwrites.",
                "author": bob_profile,
                "category": "Technology",
                "tags": ["revision", "workflow"],
                "is_published": True,
                "featured": False,
                "revisions": [
                    {
                        "version": 1,
                        "title": "Version Control for Writers",
                        "description": "Managing article versions",
                        "body": "Writers need version control like developers do.",
                        "edited_by": bob_profile,
                        "revision_note": "Initial draft"
                    },
                    {
                        "version": 2,
                        "title": "Version Control for Writers: Edit History Best Practices",
                        "description": "Managing article versions and maintaining quality through edit tracking",
                        "body": "Just like developers use version control, writers need robust edit history systems...\n\n" +
                                "Each revision should capture who made what changes and why...\n\n" +
                                "This enables transparency and prevents accidental overwrites.",
                        "edited_by": alice_profile,
                        "revision_note": "Expanded with best practices and examples"
                    }
                ]
            },
            {
                "title": "Inline Comments and Discussion Workflows",
                "slug": "inline-comments-workflows",
                "description": "Using threaded discussions to improve collaboration quality",
                "body": "Inline comments allow collaborators to provide context-specific feedback...\n\n" +
                        "Instead of general comments on the whole article, writers can highlight specific passages...\n\n" +
                        "This creates a structured discussion around improvements.",
                "author": charlie_profile,
                "category": "Business",
                "tags": ["collaboration", "workflow"],
                "is_published": True,
                "featured": False,
                "revisions": [
                    {
                        "version": 1,
                        "title": "Inline Comments and Discussion Workflows",
                        "description": "Using threaded discussions to improve collaboration",
                        "body": "Inline comments are powerful collaboration tools.",
                        "edited_by": charlie_profile,
                        "revision_note": "Initial draft"
                    }
                ]
            }
        ]

        created_count = 0
        for article_data in articles_data:
            revisions = article_data.pop("revisions", [])
            tags_list = article_data.pop("tags", [])
            category = categories.get(article_data.pop("category"))

            article, created = Article.objects.get_or_create(
                slug=article_data["slug"],
                defaults={
                    "title": article_data["title"],
                    "description": article_data["description"],
                    "body": article_data["body"],
                    "author": article_data["author"],
                    "category": category,
                    "is_published": article_data.get("is_published", True),
                    "featured": article_data.get("featured", False),
                    "view_count": 0
                }
            )

            if created:
                # Add tags
                for tag_name in tags_list:
                    article.tags.add(tags[tag_name])

                # Create revision history
                for rev_data in revisions:
                    ArticleRevision.objects.get_or_create(
                        article=article,
                        version_number=rev_data["version"],
                        defaults={
                            "title": rev_data["title"],
                            "description": rev_data["description"],
                            "body": rev_data["body"],
                            "edited_by": rev_data["edited_by"],
                            "revision_note": rev_data["revision_note"]
                        }
                    )

                self.stdout.write(f"  Created article: {article.title}")
                self.stdout.write(f"    - With {len(revisions)} revision(s)")
                created_count += 1
            else:
                self.stdout.write(f"  Article already exists: {article.title}")

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully loaded {created_count} new articles")
        )
