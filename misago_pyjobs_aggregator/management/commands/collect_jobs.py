from django.core.management.base import BaseCommand

from ...utils import collect_jobs


class Command(BaseCommand):
    help = "Fetch matching recent job advertisements and publish them to Misago."

    def handle(self, *args, **options):
        result = collect_jobs()
        self.stdout.write(self.style.SUCCESS(f"Job collection completed: {result}"))
