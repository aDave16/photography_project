from django.db import migrations


def create_default_slots(apps, schema_editor):
    BookingSlot = apps.get_model('main', 'BookingSlot')
    defaults = [
        {'name': 'full_day', 'label': 'Full Day', 'order': 0, 'capacity': 1, 'is_active': True},
        {'name': 'morning', 'label': 'Morning (09:00-12:00)', 'order': 1, 'capacity': 3, 'is_active': True},
        {'name': 'afternoon', 'label': 'Afternoon (12:00-16:00)', 'order': 2, 'capacity': 3, 'is_active': True},
        {'name': 'evening', 'label': 'Evening (16:00-20:00)', 'order': 3, 'capacity': 3, 'is_active': True},
    ]
    for s in defaults:
        BookingSlot.objects.update_or_create(name=s['name'], defaults=s)


def remove_default_slots(apps, schema_editor):
    BookingSlot = apps.get_model('main', 'BookingSlot')
    names = ['full_day', 'morning', 'afternoon', 'evening']
    BookingSlot.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_availability_bookingslot_booking_payment_status_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_slots, remove_default_slots),
    ]
