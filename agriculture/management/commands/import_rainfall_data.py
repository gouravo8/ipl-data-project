# C:\Users\Gourav Rajput\CropCareConnect\agriculture\management\commands\import_rainfall_data.py

import csv
from django.core.management.base import BaseCommand, CommandError
from agriculture.models import RainfallData
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Imports rainfall data from the NRSC-rainfall-districtwise-jan22_0.csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The path to the CSV file to import')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file_path']

        # Construct the full path relative to the project base directory
        # Assuming the CSV is in the same directory as manage.py or a known location
        if not os.path.isabs(csv_file_path):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            csv_file_path = os.path.join(project_root, csv_file_path)

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" does not exist.')

        self.stdout.write(f"Starting import from {csv_file_path}...")

        records_added = 0
        records_skipped = 0

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Extract data from the row
                    state = row.get('State', '').strip()
                    district = row.get('District', '').strip()
                    date_str = row.get('Date', '').strip()
                    year_str = row.get('Year', '')
                    month_str = row.get('Month', '')
                    avg_rainfall_str = row.get('Avg_rainfall', '0.0')
                    agency_name = row.get('Agency_name', '').strip()

                    # Validate and convert types
                    if not all([state, district, date_str, year_str, month_str, avg_rainfall_str, agency_name]):
                        self.stdout.write(self.style.WARNING(f"Skipping row due to missing required data: {row}"))
                        records_skipped += 1
                        continue

                    try:
                        # Parse date assuming YYYY-MM-DD format as seen in your CSV head
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping row due to invalid date format '{date_str}': {row}"))
                        records_skipped += 1
                        continue

                    try:
                        year = int(year_str)
                        month = int(month_str)
                        avg_rainfall = float(avg_rainfall_str)
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping row due to invalid numeric data: {row}"))
                        records_skipped += 1
                        continue

                    # Use get_or_create to avoid duplicates based on the unique_together constraint
                    obj, created = RainfallData.objects.get_or_create(
                        state=state,
                        district=district,
                        date=parsed_date,
                        defaults={
                            'year': year,
                            'month': month,
                            'avg_rainfall': avg_rainfall,
                            'agency_name': agency_name
                        }
                    )

                    if created:
                        records_added += 1
                    else:
                        records_skipped += 1 # Count as skipped if already exists
                        # self.stdout.write(self.style.NOTICE(f"Skipping duplicate record: {state}, {district}, {date_str}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row {row}: {e}"))
                    records_skipped += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported rainfall data."))
        self.stdout.write(self.style.SUCCESS(f"Records added: {records_added}"))
        self.stdout.write(self.style.WARNING(f"Records skipped (duplicates or errors): {records_skipped}"))