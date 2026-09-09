from django.core.management.base import BaseCommand
from django.db.models import Count
from main.models import Booking, Availability


class Command(BaseCommand):
    help = 'Sync existing bookings with availability system'

    def handle(self, *args, **options):
        self.stdout.write('Syncing existing bookings with availability system...')

        # Get all unique dates that have bookings
        booking_dates = Booking.objects.values_list('event_date', flat=True).distinct()

        synced_count = 0
        for date in booking_dates:
            if not date:
                continue

            # Count confirmed bookings for this date
            confirmed_count = Booking.objects.filter(
                event_date=date,
                status='confirmed'
            ).count()

            if confirmed_count > 0:
                # Create or update availability record
                Availability.objects.update_or_create(
                    date=date,
                    defaults={
                        'is_available': False,
                        'is_blocked_by_admin': False,
                        'reason': f'{confirmed_count} confirmed booking(s)'
                    }
                )
                synced_count += 1
                self.stdout.write(f'  Synced {date}: {confirmed_count} confirmed bookings')
            else:
                # Check if there are any non-confirmed bookings
                total_bookings = Booking.objects.filter(event_date=date).count()
                if total_bookings > 0:
                    # If there are bookings but none confirmed, date should be available
                    availability = Availability.objects.filter(date=date).first()
                    if availability and not availability.is_blocked_by_admin:
                        availability.is_available = True
                        availability.reason = f'{total_bookings} pending booking(s)'
                        availability.save()
                        self.stdout.write(f'  Updated {date}: {total_bookings} pending bookings')

        self.stdout.write(self.style.SUCCESS(f'Successfully synced {synced_count} dates with bookings'))