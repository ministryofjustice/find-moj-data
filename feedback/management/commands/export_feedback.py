import csv
from sys import stdout

from django.core.management.base import BaseCommand

from feedback.models import Feedback


class Command(BaseCommand):
    help = "Export feedback survey data"

    def handle(self, *args, **options):
        writer = csv.writer(stdout)
        writer.writerow(["satisfaction_rating", "how_can_we_improve"])

        for feedback in Feedback.objects.all():
            writer.writerow([feedback.satisfaction_rating, feedback.how_can_we_improve])
