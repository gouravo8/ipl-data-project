# C:\Users\Gourav Rajput\CropCareConnect\agriculture\management\commands\fetch_agmarknet_data.py

import requests
from django.core.management.base import BaseCommand
from agriculture.models import MarketPrice
from datetime import datetime

class Command(BaseCommand):
    help = 'Fetches latest market price data from data.gov.in Agmarknet API'

    def handle(self, *args, **options):
        # IMPORTANT: Replace with your actual API key
        api_key = '579b464db66ec23bdd000001f32472fcad67493659ed611d77c0d998'
        url = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'

        # Set a higher limit to fetch more data
        params = {
            'api-key': api_key,
            'format': 'json',
            'offset': 0,
            'limit': 5000,  # Increased limit
        }

        self.stdout.write("Fetching data from Agmarknet API...")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()

            records_added = 0
            records_skipped = 0

            if data and 'records' in data:
                for record in data['records']:
                    # Extract data, handling potential missing fields
                    state = record.get('state', '').strip()
                    district = record.get('district', '').strip()
                    market = record.get('market', '').strip()
                    commodity = record.get('commodity', '').strip()
                    variety = record.get('variety', '').strip()
                    grade = record.get('grade', '').strip()
                    arrival_date_str = record.get('arrival_date', '')
                    min_price_str = record.get('min_price', '0').replace(',', '')
                    max_price_str = record.get('max_price', '0').replace(',', '')
                    modal_price_str = record.get('modal_price', '0').replace(',', '')

                    # Basic validation and type conversion
                    try:
                        arrival_date = datetime.strptime(arrival_date_str, '%d/%m/%Y').date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping record due to invalid date format: {arrival_date_str}"))
                        records_skipped += 1
                        continue

                    try:
                        min_price = float(min_price_str)
                        max_price = float(max_price_str)
                        modal_price = float(modal_price_str)
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping record due to invalid price format for {commodity}: Min={min_price_str}, Max={max_price_str}, Modal={modal_price_str}"))
                        records_skipped += 1
                        continue

                    # Attempt to add or get the record
                    try:
                        # Use get_or_create to prevent duplicate entries
                        # The unique_together constraint in your model helps here
                        obj, created = MarketPrice.objects.get_or_create(
                            state=state,
                            district=district,
                            market=market,
                            commodity=commodity,
                            variety=variety,
                            grade=grade,
                            arrival_date=arrival_date,
                            defaults={
                                'min_price': min_price,
                                'max_price': max_price,
                                'modal_price': modal_price
                            }
                        )
                        if created:
                            records_added += 1
                        # If not created, it means an identical record already exists,
                        # so we don't need to do anything.
                    except Exception as e: # <--- THIS WAS THE MISSING 'except' BLOCK!
                        self.stdout.write(self.style.ERROR(f"Error adding record for {commodity} on {arrival_date}: {e}"))
                        records_skipped += 1
            else:
                self.stdout.write(self.style.WARNING("No records found in the API response or response format is unexpected."))

            self.stdout.write(self.style.SUCCESS(f"Successfully fetched Agmarknet data."))
            self.stdout.write(self.style.SUCCESS(f"Records added: {records_added}"))
            self.stdout.write(self.style.WARNING(f"Records skipped (duplicates or errors): {records_skipped}"))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data from API: {e}"))
        except ValueError as e: # For JSON decoding errors
            self.stdout.write(self.style.ERROR(f"Error decoding JSON response: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))