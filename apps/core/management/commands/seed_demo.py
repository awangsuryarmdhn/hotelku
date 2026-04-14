from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from apps.accounts.models import User
from apps.rooms.models import RoomType, Room
from apps.guests.models import Guest
from apps.reservations.models import Reservation, ReservationRoom
from apps.pos.models import MenuCategory, MenuItem

class Command(BaseCommand):
    help = 'Seeds the database with Indonesian Demo Data for MantaHotel'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Demo Data Seeding...")

        # 1. Room Types
        types = [
            {'name': 'Standard Room', 'description': 'Kamar nyaman dan minimalis.', 'base_rate': 450000, 'max_occupancy': 2},
            {'name': 'Deluxe Ocean View', 'description': 'Pemandangan laut lepas dengan balkon.', 'base_rate': 850000, 'max_occupancy': 2},
            {'name': 'Family Suite', 'description': 'Ruang luas untuk keluarga.', 'base_rate': 1500000, 'max_occupancy': 4},
        ]
        room_types = {}
        for t in types:
            rt, _ = RoomType.objects.get_or_create(name=t['name'], defaults=t)
            room_types[t['name']] = rt
            
        # 2. Rooms
        if not Room.objects.exists():
            Room.objects.create(room_number='101', room_type=room_types['Standard Room'], floor='1', status='available')
            Room.objects.create(room_number='102', room_type=room_types['Standard Room'], floor='1', status='occupied')
            Room.objects.create(room_number='103', room_type=room_types['Standard Room'], floor='1', status='dirty')
            
            Room.objects.create(room_number='201', room_type=room_types['Deluxe Ocean View'], floor='2', status='available')
            Room.objects.create(room_number='202', room_type=room_types['Deluxe Ocean View'], floor='2', status='occupied')
            Room.objects.create(room_number='203', room_type=room_types['Deluxe Ocean View'], floor='2', status='maintenance')
            
            Room.objects.create(room_number='301', room_type=room_types['Family Suite'], floor='3', status='available')
            Room.objects.create(room_number='302', room_type=room_types['Family Suite'], floor='3', status='available')

        # 3. Guests
        g1, _ = Guest.objects.get_or_create(email='budi@example.com', defaults={'full_name': 'Budi Santoso', 'phone': '081234567890', 'id_number': '3201234567', 'nationality': 'ID'})
        g2, _ = Guest.objects.get_or_create(email='siti@example.com', defaults={'full_name': 'Siti Aminah', 'phone': '081298765432', 'id_number': '3209876543', 'nationality': 'ID'})
        g3, _ = Guest.objects.get_or_create(email='john@example.com', defaults={'full_name': 'John Doe', 'phone': '+123456789', 'id_number': 'P1234567', 'nationality': 'US'})

        # 4. Reservations (Some past, some active currently)
        today = timezone.now().date()
        if not Reservation.objects.exists():
            # Active checking in today
            r1 = Reservation.objects.create(guest=g1, source='direct', check_in=today, check_out=today + timedelta(days=2), adults=2, total_amount=1700000, status='checked_in')
            r1_room = Room.objects.get(room_number='202')
            ReservationRoom.objects.create(reservation=r1, room=r1_room, nightly_rate=850000)
            
            # Future booking
            r2 = Reservation.objects.create(guest=g2, source='ota', check_in=today + timedelta(days=1), check_out=today + timedelta(days=3), adults=2, total_amount=900000, status='confirmed')
            r2_room = Room.objects.get(room_number='101')
            ReservationRoom.objects.create(reservation=r2, room=r2_room, nightly_rate=450000)
            
            # In-house currently
            r3 = Reservation.objects.create(guest=g3, source='direct', check_in=today - timedelta(days=1), check_out=today + timedelta(days=1), adults=1, total_amount=450000, status='checked_in')
            r3_room = Room.objects.get(room_number='102')
            ReservationRoom.objects.create(reservation=r3, room=r3_room, nightly_rate=450000)

        # 5. Menu Categories & Items
        if not MenuCategory.objects.exists():
            cat_makan = MenuCategory.objects.create(name='Makanan Utama', description='Main courses')
            cat_minum = MenuCategory.objects.create(name='Minuman', description='Beverages')
            
            MenuItem.objects.create(category=cat_makan, name='Nasi Goreng Spesial', price=45000, is_available=True)
            MenuItem.objects.create(category=cat_makan, name='Mie Goreng Seafood', price=55000, is_available=True)
            MenuItem.objects.create(category=cat_makan, name='Sate Ayam Madura', price=60000, is_available=True)
            
            MenuItem.objects.create(category=cat_minum, name='Es Teh Manis', price=15000, is_available=True)
            MenuItem.objects.create(category=cat_minum, name='Jus Jeruk Segar', price=25000, is_available=True)
            MenuItem.objects.create(category=cat_minum, name='Kopi Tubruk', price=20000, is_available=True)

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data in Bahasa Indonesia!'))
