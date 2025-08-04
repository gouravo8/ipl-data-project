# agriculture/management/commands/update_prices.py

from django.core.management.base import BaseCommand
from agriculture.tasks import update_daily_market_prices

class Command(BaseCommand):
    help = 'Fetches and updates daily market prices'

    def handle(self, *args, **options):
        self.stdout.write("Starting the task to fetch and update daily market prices...")
        
        # Call the logic directly from your task
        update_daily_market_prices()
        
        self.stdout.write(self.style.SUCCESS('Task completed: Market prices updated successfully!'))

