"""
Management command to load sample notifications for collaborative editing spec.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from conduit.apps.authentication.models import User, UserNotification


class Command(BaseCommand):
    help = "Load sample notifications for collaborative editing features"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Loading sample notifications..."))

        # Get users
        users = {
            username: User.objects.filter(username=username).first()
            for username in ["alice", "bob", "charlie", "diana", "eve"]
        }

        if not all(users.values()):
            self.stdout.write(
                self.style.ERROR("Error: Please run 'load_users' command first")
            )
            return

        created_count = 0

        # Notifications for collaborative article editing scenarios
        notifications_data = [
            # Mentions
            {
                "recipient": "diana",
                "notification_type": "mention",
                "message": "@diana Your feedback on the introduction is important. Can you review the latest changes?",
                "actor": "alice",
                "link": "/articles/real-time-collaborative-writing",
                "is_read": False
            },
            {
                "recipient": "eve",
                "notification_type": "mention",
                "message": "@eve Bob mentioned your technical expertise in the development section.",
                "actor": "bob",
                "link": "/articles/real-time-collaborative-writing#comment-2",
                "is_read": False
            },
            # Comments
            {
                "recipient": "alice",
                "notification_type": "comment",
                "message": "Diana commented on your article: 'Great overview! How does conflict resolution work?'",
                "actor": "diana",
                "link": "/articles/real-time-collaborative-writing#comment-1",
                "is_read": True
            },
            {
                "recipient": "charlie",
                "notification_type": "comment",
                "message": "Bob replied to your question: 'The system uses operational transformation to merge concurrent edits.'",
                "actor": "bob",
                "link": "/articles/version-control-writers#comment-4",
                "is_read": False
            },
            # Replies
            {
                "recipient": "diana",
                "notification_type": "reply",
                "message": "Alice replied to your discussion about threaded comments.",
                "actor": "alice",
                "link": "/articles/inline-comments-workflows#comment-5",
                "is_read": False
            },
            {
                "recipient": "bob",
                "notification_type": "reply",
                "message": "Charlie asked about reverting to previous versions in your article.",
                "actor": "charlie",
                "link": "/articles/version-control-writers#comment-4",
                "is_read": True
            },
            # Follow notifications
            {
                "recipient": "alice",
                "notification_type": "follow",
                "message": "Eve followed you and is interested in your content.",
                "actor": "eve",
                "link": "/profiles/eve",
                "is_read": True
            },
            {
                "recipient": "bob",
                "notification_type": "follow",
                "message": "Diana is now following you.",
                "actor": "diana",
                "link": "/profiles/diana",
                "is_read": False
            },
            # Article collaboration invitations (treated as comment notifications)
            {
                "recipient": "bob",
                "notification_type": "comment",
                "message": "Alice invited you to collaborate on 'Real-Time Collaborative Writing: The Future of Content Creation'",
                "actor": "alice",
                "link": "/articles/real-time-collaborative-writing/collaborate",
                "is_read": False
            },
            {
                "recipient": "charlie",
                "notification_type": "comment",
                "message": "Alice invited you to collaborate on the same article. A collaboration session has been created.",
                "actor": "alice",
                "link": "/articles/real-time-collaborative-writing/collaborate",
                "is_read": False
            },
            # Publication notifications
            {
                "recipient": "bob",
                "notification_type": "comment",
                "message": "Alice published the collaborative article 'Real-Time Collaborative Writing: The Future of Content Creation'. Thank you for your contributions!",
                "actor": "alice",
                "link": "/articles/real-time-collaborative-writing",
                "is_read": False
            },
            {
                "recipient": "charlie",
                "notification_type": "comment",
                "message": "The article you collaborated on has been published. You are listed as a co-author!",
                "actor": "alice",
                "link": "/articles/real-time-collaborative-writing",
                "is_read": False
            }
        ]

        for notif_data in notifications_data:
            recipient_user = users.get(notif_data.pop("recipient"))
            actor_user = users.get(notif_data.pop("actor"))

            if not recipient_user or not actor_user:
                continue

            notification, created = UserNotification.objects.get_or_create(
                recipient=recipient_user,
                notification_type=notif_data["notification_type"],
                message=notif_data["message"],
                actor=actor_user,
                defaults={
                    "link": notif_data["link"],
                    "is_read": notif_data["is_read"],
                    "read_at": timezone.now() if notif_data["is_read"] else None
                }
            )

            if created:
                created_count += 1
                notif_type = notif_data["notification_type"]
                self.stdout.write(
                    f"  Created {notif_type} notification for {recipient_user.username}"
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully loaded {created_count} new notifications")
        )
