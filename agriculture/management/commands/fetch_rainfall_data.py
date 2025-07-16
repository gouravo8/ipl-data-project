# agriculture/management/commands/fetch_rainfall_data.py

import requests
from django.core.management.base import BaseCommand
from agriculture.models import RainfallData # Import your RainfallData model
from datetime import datetime # Not strictly needed for this data, but good for consistency

class Command(BaseCommand):
    help = 'Fetches Sub Divisional Monthly Rainfall data from data.gov.in API (1901-2017).'

    def handle(self, *args, **options):
        # IMPORTANT: Use your actual API key from data.gov.in
        # This is the resource ID for "Sub Divisional Monthly Rainfall from 1901 to 2017"
        resource_id = '66532087-251f-474c-a134-2e67303e39b7'
        api_key = '579b464db66ec23bdd000001f32472fcad67493659ed611d77c0d998' # Your provided API key

        base_url = f'https://api.data.gov.in/resource/{resource_id}'

        # Map month names from API response to month numbers for your model
        month_map = {
            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
        }

        # Parameters for the API request
        params = {
            'api-key': api_key,
            'format': 'json',
            'offset': 0,
            'limit': 1000 # Max limit per request, check Data.gov.in docs for this specific API
        }

        self.stdout.write("Fetching rainfall data from data.gov.in API...")
        total_records_fetched = 0
        records_added = 0
        records_updated = 0
        records_skipped = 0

        while True:
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                data = response.json()

                records = data.get('records', [])

                if not records:
                    self.stdout.write("No more records found or end of data.")
                    break # No more data to fetch

                for record in records:
                    subdivision = record.get('Subdivision', '').strip() # Exact key from API
                    year_str = record.get('YEAR', '').strip()         # Exact key from API

                    if not subdivision or not year_str:
                        self.stdout.write(self.style.WARNING(f"Skipping record due to missing Subdivision or Year: {record}"))
                        records_skipped += 1
                        continue

                    try:
                        year = int(year_str)
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping record due to invalid year format: {year_str}"))
                        records_skipped += 1
                        continue

                    # Iterate through each month's rainfall data in the record
                    for month_name_api, month_num in month_map.items():
                        rainfall_str = record.get(month_name_api)

                        if rainfall_str is None or rainfall_str.strip() == '':
                            # Data might be missing for some months/subdivisions/years. Just skip this specific month.
                            continue

                        try:
                            rainfall_mm = float(rainfall_str)
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f"Skipping rainfall value '{rainfall_str}' for {subdivision}, {month_name_api} {year} due to invalid format."))
                            records_skipped += 1
                            continue

                        # Create or update the RainfallData entry for this specific month
                        obj, created = RainfallData.objects.update_or_create(
                            subdivision=subdivision,
                            year=year,
                            month=month_num,
                            defaults={'rainfall_mm': rainfall_mm}
                        )
                        if created:
                            records_added += 1
                        else:
                            records_updated += 1
                    
                    total_records_fetched += 1 # Count each full record (year/subdivision) from API


                # Handle pagination
                total_records_in_api = data.get('total', 0)
                current_offset = params['offset']
                
                # Check if there are more records to fetch
                if current_offset + params['limit'] < total_records_in_api:
                    params['offset'] += params['limit']
                    self.stdout.write(f"Fetched {current_offset + params['limit']} of {total_records_in_api} records. Continuing...")
                else:
                    self.stdout.write("All records fetched.")
                    break # All data fetched

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"API request failed: {e}"))
                break
            except ValueError as e: # For JSON decoding errors
                self.stdout.write(self.style.ERROR(f"Error decoding JSON response: {e}"))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
                break

        self.stdout.write(self.style.SUCCESS(f"Finished fetching rainfall data."))
        self.stdout.write(self.style.SUCCESS(f"Total API records processed: {total_records_fetched}"))
        self.stdout.write(self.style.SUCCESS(f"Individual monthly rainfall entries added: {records_added}"))
        self.stdout.write(self.style.SUCCESS(f"Individual monthly rainfall entries updated: {records_updated}"))
        self.stdout.write(self.style.WARNING(f"Individual monthly rainfall entries skipped (errors/missing data): {records_skipped}"))