# listings/management/commands/seed.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from faker import Faker
import random
from datetime import timedelta, date
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = 'Seed database with sample listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        # Create host user
        host, _ = User.objects.get_or_create(username='demo_host', defaults={'email': 'demo@host.com'})

        # Create guest user
        guest, _ = User.objects.get_or_create(username='demo_guest', defaults={'email': 'demo@guest.com'})

        listings = []
        for _ in range(5):
            listing = Listing.objects.create(
                host=host,
                name=fake.company(),
                description=fake.text(),
                location=fake.city(),
                pricepernight=round(random.uniform(50, 300), 2),
            )
            listings.append(listing)

        for listing in listings:
            start_date = fake.date_between(start_date='-30d', end_date='today')
            end_date = start_date + timedelta(days=random.randint(1, 10))
            Booking.objects.create(
                property=listing,
                user=guest,
                start_date=start_date,
                end_date=end_date,
                total_price=(listing.pricepernight * (end_date - start_date).days),
                status=random.choice(['pending', 'confirmed', 'canceled']),
            )

            Review.objects.create(
                property=listing,
                user=guest,
                rating=random.randint(1, 5),
                comment=fake.sentence(),
            )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))
