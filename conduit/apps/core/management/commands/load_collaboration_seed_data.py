"""
Master management command to load all seed data for the collaborative article editing feature.
Runs all individual seed commands in the correct order.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load all seed data for collaborative article editing in the correct order"

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip loading users (useful if they already exist)',
        )
        parser.add_argument(
            '--only',
            type=str,
            choices=[
                'users',
                'articles',
                'comments',
                'notifications',
                'relationships'
            ],
            help='Load only a specific dataset',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "=" * 70
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Loading Collaborative Article Editing Seed Data"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "=" * 70
            )
        )

        only = options.get('only')
        skip_users = options.get('skip_users')

        commands_to_run = []

        if not skip_users and not only:
            commands_to_run.append(('load_users', {}))

        if only == 'users' or (not only and not skip_users):
            if not only:
                commands_to_run.append(('load_articles', {}))
                commands_to_run.append(('load_comments', {}))
                commands_to_run.append(('load_notifications', {}))
                commands_to_run.append(('load_collaboration_relationships', {}))
        elif only == 'articles':
            commands_to_run.append(('load_articles', {}))
        elif only == 'comments':
            commands_to_run.append(('load_comments', {}))
        elif only == 'notifications':
            commands_to_run.append(('load_notifications', {}))
        elif only == 'relationships':
            commands_to_run.append(('load_collaboration_relationships', {}))

        # Run all commands
        for command_name, command_options in commands_to_run:
            self.stdout.write(f"\nRunning '{command_name}'...\n")
            try:
                call_command(command_name, **command_options)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error running {command_name}: {str(e)}")
                )
                if only:
                    raise
                continue

        self.stdout.write(
            self.style.SUCCESS(
                "\n" + "=" * 70
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "All seed data loaded successfully!"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "=" * 70
            )
        )
