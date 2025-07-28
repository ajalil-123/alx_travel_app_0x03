from rest_framework import serializers
from .models import Listing, Booking

class ListingSerializer(serializers.ModelSerializer):
    host_username = serializers.CharField(source='host.username', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'listing_id',
            'host',
            'host_username',
            'title',
            'description',
            'location',
            'price_per_night',
            'created_at',
        ]
        read_only_fields = ['listing_id', 'created_at', 'host_username']


class BookingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'user',
            'user_username',
            'listing',
            'listing_title',
            'check_in',
            'check_out',
            'total_price',
            'created_at',
        ]
        read_only_fields = ['booking_id', 'created_at', 'user_username', 'listing_title']
