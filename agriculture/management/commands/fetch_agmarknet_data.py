# C:\Users\Gourav Rajput\CropCareConnect\agriculture\management\commands\fetch_agmarknet_data.py

import requests
from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime
import os
import json
from django.apps import apps # NEW: Import apps to safely get models

class Command(BaseCommand):
    help = 'Fetches agricultural market price data from data.gov.in Agmarknet API and stores it.'

    def add_arguments(self, parser):
        # Keep the --date argument for flexibility, though the default API call fetches broadly
        parser.add_argument(
            '--date',
            type=str,
            help='Fetch data for a specific date (YYYY-MM-DD). (Note: Default API call might fetch all available data)',
            default=None,
        )
        # Add an argument to control the limit of records fetched per API call.
        # Max limit is often 100000 on data.gov.in
        parser.add_argument(
            '--limit',
            type=int,
            help='Number of records to fetch per API call. Max is usually 100000.',
            default=5000, # Set default to 5000 as per your provided code
        )

    def handle(self, *args, **options):
        # Safely get the MarketPrice model after Django's app registry is ready
        MarketPrice = apps.get_model('agriculture', 'MarketPrice')

        # --- Configuration ---
        # It's crucial to get the API key from environment variables for security in production.
        API_KEY = os.environ.get('DATA_GOV_IN_API_KEY')
        if not API_KEY:
            # Example API key (replace with your actual key from data.gov.in)
            # For production, ensure DATA_GOV_IN_API_KEY is set in Render environment variables.
            API_KEY = '579b464db66ec23bdd000001f32472fcad67493659ed611d77c0d998'
            self.stdout.write(self.style.WARNING("DATA_GOV_IN_API_KEY environment variable not set. Using hardcoded example key. Please set it in Render for production."))

        # Specific Dataset ID for Agmarknet Daily Market Prices (as identified)
        DATASET_ID = '9ef84268-d588-465a-a308-a864a43d0070'

        fetch_limit = options['limit']
        
        self.stdout.write(self.style.MIGRATE_HEADING(f"Attempting to fetch market data from Dataset ID: {DATASET_ID} with limit={fetch_limit}"))

        # --- Construct API URL (WITHOUT DATE FILTER, with offset and limit) ---
        # This URL will attempt to fetch a large number of records.
        # If more than 'limit' records exist, you would need to implement pagination
        # by incrementing the 'offset' parameter in a loop. For simplicity, we're
        # assuming 5000 records are sufficient for a single fetch.
        api_url = (
            f"https://api.data.gov.in/resource/{DATASET_ID}?"
            f"api-key={API_KEY}&format=json&limit={fetch_limit}&offset=0"
        )
        
        self.stdout.write(self.style.MIGRATE_HEADING(f"API URL: {api_url}"))

        # --- Fetch Data ---
        try:
            # Increased timeout to handle potentially large data transfers
            response = requests.get(api_url, timeout=120)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
        except requests.exceptions.Timeout:
            raise CommandError("The request to data.gov.in timed out after 120 seconds.")
        except requests.exceptions.RequestException as e:
            raise CommandError(f"Error fetching data from data.gov.in: {e}")
        except json.JSONDecodeError:
            raise CommandError("Failed to decode JSON response from data.gov.in. Response was not valid JSON.")

        records_processed = 0
        records_added = 0
        records_updated = 0
        records_skipped = 0 # Initialize records_skipped here to ensure it's always defined

        if 'records' in data and isinstance(data['records'], list):
            if not data['records']:
                self.stdout.write(self.style.WARNING("No records found in the API response. Empty response."))
                return

            for record in data['records']:
                try:
                    # Map API response fields to your Django model fields.
                    # These field names ('state', 'district', etc.) are based on the Agmarknet API response.
                    # .strip() is used to remove leading/trailing whitespace.
                    state_val = record.get('state', '').strip()
                    district_val = record.get('district', '').strip()
                    market_val = record.get('market', '').strip()
                    commodity_val = record.get('commodity', '').strip()
                    variety_val = record.get('variety', '').strip()
                    grade_val = record.get('grade', '').strip()
                    arrival_date_str = record.get('arrival_date', '').strip()
                    
                    # Prices might come with commas, so remove them before converting to float
                    min_price_str = record.get('min_price', '0').replace(',', '').strip()
                    max_price_str = record.get('max_price', '0').replace(',', '').strip()
                    modal_price_str = record.get('modal_price', '0').replace(',', '').strip()
                    unit_val = record.get('unit', 'Quintal').strip() # Default to 'Quintal' if unit is missing

                    # Basic validation: ensure critical fields are present
                    if not all([state_val, district_val, market_val, commodity_val, arrival_date_str, modal_price_str]):
                        self.stdout.write(self.style.WARNING(f"Skipping incomplete record (missing critical fields): {record}"))
                        records_skipped += 1
                        continue

                    # Type conversion
                    try:
                        # IMPORTANT: Date format is '%d/%m/%Y' as observed from data.gov.in Agmarknet API
                        arrival_date_obj = datetime.strptime(arrival_date_str, '%d/%m/%Y').date()
                        min_price_dec = float(min_price_str) if min_price_str else None
                        max_price_dec = float(max_price_str) if max_price_str else None
                        modal_price_dec = float(modal_price_str)
                    except (ValueError, TypeError) as e:
                        self.stdout.write(self.style.WARNING(f"Skipping record due to data conversion error ({e}): {record}"))
                        records_skipped += 1
                        continue

                    # Use update_or_create to prevent duplicates and update existing records.
                    # The 'unique_together' constraint in your MarketPrice model is crucial for this.
                    obj, created = MarketPrice.objects.update_or_create(
                        state=state_val,
                        district=district_val,
                        market=market_val,
                        commodity=commodity_val,
                        variety=variety_val, # Include all fields from unique_together
                        grade=grade_val,     # Include all fields from unique_together
                        arrival_date=arrival_date_obj,
                        defaults={
                            'min_price': min_price_dec,
                            'max_price': max_price_dec,
                            'modal_price': modal_price_dec,
                            'unit': unit_val,
                        }
                    )
                    if created:
                        records_added += 1
                    else:
                        records_updated += 1
                    records_processed += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing record {record}: {e}"))
                    records_skipped += 1
                    continue
        else:
            self.stdout.write(self.style.WARNING("API response did not contain a 'records' list or was malformed."))

        self.stdout.write(self.style.SUCCESS(f"Finished fetching Agmarknet data."))
        self.stdout.write(self.style.SUCCESS(f"Records processed: {records_processed}"))
        self.stdout.write(self.style.SUCCESS(f"Records added: {records_added}"))
        self.stdout.write(self.style.SUCCESS(f"Records updated: {records_updated}"))
        self.stdout.write(self.style.WARNING(f"Records skipped (due to missing data, format errors, etc.): {records_skipped}"))