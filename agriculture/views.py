# C:\Users\Gourav Rajput\CropCareConnect\agriculture\views.py

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from datetime import datetime, date, timedelta # Import timedelta for date calculations
import json
from django.contrib import messages # For displaying success/error messages
from decimal import Decimal # For precise calculations

from .forms import CityInputForm, FarmerDiaryEntryForm, ForecastInputForm # Import all necessary forms
from .models import MarketPrice, RainfallData, CropAdvisory, FarmerDiaryEntry # Import all necessary models


# NEW VIEW FUNCTION FOR THE HOME PAGE
def home_page(request):
    # Define the options for your home page boxes.
    # Each dictionary represents a box: 'name' is display text, 'url_name' is the Django URL name
    # The 'url_name' should match what you defined in agriculture/urls.py (e.g., 'market_price_list', 'crop_advisory_list')
    options = [
        {'name': 'Market Prices', 'url_name': 'agriculture:market_price_list', 'description': 'Check daily market prices for various commodities.'},
        {'name': 'Crop Advisories & Alerts', 'url_name': 'agriculture:crop_advisory_list', 'description': 'Get advisories on diseases, pests, and best farming practices.'},
        # Option for Real-time Weather
        {'name': 'Real-time Weather', 'url_name': 'agriculture:realtime_weather', 'description': 'Get live temperature, humidity, and rain status for your city.'},
        # NEW Option for Weather Forecast
        {'name': 'Weather Forecast', 'url_name': 'agriculture:weather_forecast', 'description': 'Get future weather predictions for any date and city.'},
        # Option for Farmer Diary
        {'name': 'Farmer Diary', 'url_name': 'agriculture:diary_list', 'description': 'Record your farming events, inputs, and expenses over time.'},
    ]
    context = {
        'options': options,
        'title': 'CropCareConnect - Your Agricultural Hub'
    }
    return render(request, 'agriculture/home_page.html', context)


def market_price_list(request):
    all_prices = MarketPrice.objects.all()

    # --- 1. Get filter parameters (including search query and date range) ---
    selected_state = request.GET.get('state', '')
    selected_district = request.GET.get('district', '')
    selected_market = request.GET.get('market', '')
    selected_commodity = request.GET.get('commodity', '')
    search_query = request.GET.get('q', '')

    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # Initialize parsed dates to None
    start_date = None
    end_date = None

    # Attempt to parse dates
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass # Invalid date format, will remain None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass # Invalid date format, will remain None

    # --- 2. Apply filters to the queryset ---
    filters = Q() # Initialize an empty Q object

    # Apply dropdown filters
    if selected_state:
        filters &= Q(state=selected_state)
    if selected_district:
        filters &= Q(district=selected_district)
    if selected_market:
        filters &= Q(market=selected_market)
    if selected_commodity:
        filters &= Q(commodity=selected_commodity)

    # Apply free-text search filter
    if search_query:
        # Use OR (|) to search across multiple fields
        filters &= (
            Q(state__icontains=search_query) |
            Q(district__icontains=search_query) |
            Q(market__icontains=search_query) |
            Q(commodity__icontains=search_query) |
            Q(variety__icontains=search_query) |
            Q(grade__icontains=search_query)
        )

    # Apply date range filters
    if start_date:
        filters &= Q(arrival_date__gte=start_date) # Greater than or equal to start_date
    if end_date:
        filters &= Q(arrival_date__lte=end_date)   # Less than or equal to end_date

    # Apply all combined filters
    filtered_prices = all_prices.filter(filters) # Renamed to filtered_prices for clarity

    # --- Logic for Charting Data and Price Summary ---
    chart_labels = []
    chart_data = []
    chart_commodity = ""
    chart_market = ""
    chart_state = ""
    price_summary = None # Initialize price_summary

    # Check if filters result in a single commodity for a specific market and state for meaningful charts/summary
    # Also ensure there's at least one record before trying to access .first()
    if filtered_prices.values('commodity', 'market', 'state').distinct().count() == 1 and filtered_prices.exists():
        single_entry = filtered_prices.first()
        if single_entry:
            chart_commodity = single_entry.commodity
            chart_market = single_entry.market
            chart_state = single_entry.state

            # Fetch data points for the chart for this specific commodity/market/state
            # Ensure this queryset is ordered by date for trend calculation
            chart_prices_queryset = MarketPrice.objects.filter(
                commodity=chart_commodity,
                market=chart_market,
                state=chart_state
            ).order_by('arrival_date')

            if start_date:
                chart_prices_queryset = chart_prices_queryset.filter(arrival_date__gte=start_date)
            if end_date:
                chart_prices_queryset = chart_prices_queryset.filter(arrival_date__lte=end_date)

            chart_prices = chart_prices_queryset

            for price in chart_prices:
                chart_labels.append(price.arrival_date.strftime('%Y-%m-%d')) # Date for X-axis
                chart_data.append(float(price.modal_price)) # Modal Price for Y-axis
            
            # Calculate Price Summary
            if chart_prices.exists():
                first_price_obj = chart_prices.first()
                last_price_obj = chart_prices.last()
                
                avg_price_agg = chart_prices.aggregate(avg_price=Avg('modal_price'))
                avg_modal_price = avg_price_agg['avg_price'] if avg_price_agg['avg_price'] is not None else Decimal('0.00')

                first_modal_price = first_price_obj.modal_price
                last_modal_price = last_price_obj.modal_price
                price_change = last_modal_price - first_modal_price
                
                trend_status = "Stable"
                if price_change > Decimal('0.01'): # Using Decimal for comparison
                    trend_status = "Upward"
                elif price_change < Decimal('-0.01'):
                    trend_status = "Downward"
                
                price_summary = {
                    'avg_modal_price': avg_modal_price,
                    'price_change': price_change,
                    'trend_status': trend_status,
                }

    # --- Order the filtered data for the table ---
    # Use filtered_prices here, not all_prices
    filtered_prices = filtered_prices.order_by('-arrival_date', 'state', 'market', 'commodity')

    # --- Get unique values for filter dropdowns (from ALL data, not just filtered) ---
    # These should still come from all_prices to populate all options
    unique_states = MarketPrice.objects.values_list('state', flat=True).distinct().order_by('state')
    unique_districts = MarketPrice.objects.values_list('district', flat=True).distinct().order_by('district')
    unique_markets = MarketPrice.objects.values_list('market', flat=True).distinct().order_by('market')
    unique_commodities = MarketPrice.objects.values_list('commodity', flat=True).distinct().order_by('commodity')

    # --- Add Pagination ---
    paginator = Paginator(filtered_prices, 20) # Show 20 records per page

    page = request.GET.get('page')
    try:
        prices = paginator.page(page)
    except PageNotAnInteger:
        prices = paginator.page(1)
    except EmptyPage:
        prices = paginator.page(paginator.num_pages)

    # --- Prepare data to send to the HTML template ---
    context = {
        'prices': prices,
        'unique_states': unique_states,
        'unique_districts': unique_districts,
        'unique_markets': unique_markets,
        'unique_commodities': unique_commodities,
        'selected_state': selected_state,
        'selected_district': selected_district,
        'selected_market': selected_market,
        'selected_commodity': selected_commodity,
        'search_query': search_query,
        'start_date': start_date.isoformat() if start_date else '',
        'end_date': end_date.isoformat() if end_date else '',

        # --- Chart Data for Template ---
        'chart_labels': json.dumps(chart_labels), # Pass as JSON string
        'chart_data': json.dumps(chart_data),   # Pass as JSON string
        'chart_commodity': chart_commodity,
        'chart_market': chart_market,
        'chart_state': chart_state,
        'price_summary': price_summary, # NEW: Pass the price summary
    }
    return render(request, 'agriculture/market_price_list.html', context)


def crop_advisory_list(request):
    # Fetch all crop advisories, ordered by date published (newest first)
    # and then by severity (Red > Yellow > Green)
    advisories = CropAdvisory.objects.all().order_by('-date_published', '-severity')

    # --- SIMULATED ADVISORY GENERATION (FOR DEMO PURPOSES) ---
    # In a real application, these would come from external APIs or a data pipeline.
    # We'll add some if the database is empty or for testing.
    if not advisories.exists():
        # Example: Generate a few sample advisories if none exist
        from datetime import date, timedelta
        if not CropAdvisory.objects.filter(title="Heavy Rainfall Expected").exists():
            CropAdvisory.objects.create(
                title="Heavy Rainfall Expected",
                description="Heavy rainfall is expected in the central districts over the next 48 hours. Farmers are advised to secure crops and drainage systems. Avoid irrigation.", # Corrected from 'content' to 'description'
                alert_type="Weather",
                severity="Red",
                location="Central Districts",
                crop_name="General",
                advisory_type="GENERAL"
            )
        if not CropAdvisory.objects.filter(title="Pest Alert: Aphid Infestation").exists():
            CropAdvisory.objects.create(
                title="Pest Alert: Aphid Infestation",
                description="Reports of aphid infestation in paddy fields in southern regions. Monitor crops closely and apply recommended organic pesticides if necessary.", # Corrected from 'content' to 'description'
                alert_type="Pest",
                severity="Yellow",
                location="Southern Regions",
                crop_name="Paddy",
                advisory_type="PEST"
            )
        if not CropAdvisory.objects.filter(title="Wheat Price Drop Advisory").exists():
            CropAdvisory.objects.create(
                title="Wheat Price Drop Advisory",
                description="Wheat prices have shown a slight downward trend in major markets this week. Consider holding stock if possible, or consult local market experts.", # Corrected from 'content' to 'description'
                alert_type="Price",
                severity="Yellow",
                location="National Markets",
                crop_name="Wheat",
                advisory_type="GENERAL" # Or a new 'PRICE' advisory_type if you add it to choices
            )
        if not CropAdvisory.objects.filter(title="General Advisory: Soil Health").exists():
            CropAdvisory.objects.create(
                title="General Advisory: Soil Health",
                description="Regular soil testing is recommended to maintain optimal nutrient levels for healthy crop growth. Consider adding organic matter.", # Corrected from 'content' to 'description'
                alert_type="General",
                severity="Green",
                location="All Regions",
                crop_name="General",
                advisory_type="BEST_PRACTICE"
            )
        if not CropAdvisory.objects.filter(title="Irrigation Tips for Dry Spell").exists():
            CropAdvisory.objects.create(
                title="Irrigation Tips for Dry Spell",
                description="During dry spells, efficient irrigation techniques like drip irrigation can conserve water. Water early in the morning or late evening.", # Corrected from 'content' to 'description'
                alert_type="Irrigation",
                severity="Green",
                location="Arid Zones",
                crop_name="General",
                advisory_type="BEST_PRACTICE"
            )
        # Re-fetch advisories after creating samples
        advisories = CropAdvisory.objects.all().order_by('-date_published', '-severity')
    # --- END SIMULATED ADVISORY GENERATION ---

    # Filter logic for advisories (by type)
    selected_type = request.GET.get('alert_type', '')
    if selected_type:
        advisories = advisories.filter(alert_type=selected_type)

    # Get unique alert types for filter dropdown
    unique_alert_types = CropAdvisory.objects.values_list('alert_type', flat=True).distinct().order_by('alert_type')

    context = {
        'advisories': advisories,
        'unique_alert_types': unique_alert_types,
        'selected_type': selected_type,
        'title': 'Crop Advisories & Alerts'
    }
    return render(request, 'agriculture/crop_advisory_list.html', context)


# View function for Real-time Weather Data
def realtime_weather_view(request):
    form = CityInputForm()
    weather_data = None
    prediction_message = None
    weather_error = None # To store any errors from API calls

    if request.method == 'POST':
        form = CityInputForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            
            # --- Step 2.1: Geocoding (City Name to Lat/Lon) using Open-Meteo Geocoding API ---
            # Open-Meteo Geocoding API: https://open-meteo.com/en/docs/geocoding-api
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
            
            try:
                geocode_response = requests.get(geocode_url, timeout=5) # 5-second timeout
                geocode_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                geocode_data = geocode_response.json()

                if geocode_data and 'results' in geocode_data and geocode_data['results']:
                    first_result = geocode_data['results'][0]
                    latitude = first_result.get('latitude')
                    longitude = first_result.get('longitude')
                    display_city_name = first_result.get('name', city_name) # Use the name returned by API
                    display_country = first_result.get('country', '')
                    display_admin1 = first_result.get('admin1', '') # State/Province
                    
                    # --- Step 2.2: Fetch Weather Data using Open-Meteo Forecast API ---
                    # Open-Meteo Forecast API: https://open-meteo.com/en/docs
                    weather_url = (f"https://api.open-meteo.com/v1/forecast?"
                                   f"latitude={latitude}&longitude={longitude}&"
                                   f"current=temperature_2m,relative_humidity_2m,is_day,precipitation,rain,showers,weather_code&" # Include weather_code for rain status
                                   f"timezone=auto&forecast_days=1") # We only need current day

                    weather_response = requests.get(weather_url, timeout=5)
                    weather_response.raise_for_status()
                    current_weather_data = weather_response.json()

                    if current_weather_data and 'current' in current_weather_data:
                        current = current_weather_data['current']
                        weather_data = {
                            'city': display_city_name,
                            'state': display_admin1,
                            'country': display_country,
                            'temperature': current.get('temperature_2m'),
                            'humidity': current.get('relative_humidity_2m'),
                            'precipitation': current.get('precipitation'), # Total liquid precipitation (rain, showers, snow)
                            'rain': current.get('rain'), # Rain only
                            'showers': current.get('showers'), # Showers only
                            'weather_code': current.get('weather_code'), # Numerical code for weather condition
                            'is_day': current.get('is_day') == 1 # 1 for day, 0 for night
                        }

                        # --- Step 2.3: Determine Real-time Rain Status ---
                        # Open-Meteo Weather Codes: https://www.open-meteo.com/en/docs/weather-codes
                        # WMO Weather interpretation codes (WWMO)
                        # 51, 53, 55 (drizzle), 61, 63, 65 (rain), 66, 67 (freezing rain) etc.
                        # Also check 'precipitation' > 0 or 'rain' > 0
                        
                        realtime_rain_status = False
                        if weather_data['weather_code'] in [51, 53, 55, 61, 63, 65, 66, 67, 80, 81, 82] or \
                           (weather_data['precipitation'] is not None and weather_data['precipitation'] > 0) or \
                           (weather_data['rain'] is not None and weather_data['rain'] > 0):
                           realtime_rain_status = True
                        
                        # --- Step 2.4: Simulate Model's Prediction ---
                        # IMPORTANT: This is a placeholder. In a real scenario, you would
                        # call your actual trained ML model here to get its prediction.
                        # For now, we'll use a fixed value.
                        model_predicted_rain_probability = 0.96 # Example: 96% chance of rain by your model

                        # For simple comparison, let's say if model predicts >= 50% it means 'high chance of rain'
                        model_predicts_high_rain = (model_predicted_rain_probability >= 0.50)

                        # --- Step 2.5: Comparison Logic and Notification ---
                        if model_predicts_high_rain and not realtime_rain_status:
                            prediction_message = "ALERT: Your model predicted a high chance of rain, but current real-time data shows no rain. Prediction may be incorrect or delayed."
                        elif not model_predicts_high_rain and realtime_rain_status:
                            prediction_message = "NOTE: Your model predicted low/no rain, but current real-time data shows rain. Please check conditions."
                        else:
                            prediction_message = "Prediction matches real-time conditions (or no strong contradiction)."

                    else:
                        weather_error = "Could not fetch current weather data for this location."
                else:
                    weather_error = f"City '{city_name}' not found. Please try a different name or spelling."

            except requests.exceptions.RequestException as e:
                weather_error = f"Could not connect to weather service. Error: {e}"
            except ValueError:
                weather_error = "Invalid response from weather service."
            except Exception as e:
                weather_error = f"An unexpected error occurred: {e}"

    context = {
        'form': form,
        'weather_data': weather_data,
        'prediction_message': prediction_message,
        'weather_error': weather_error
    }
    return render(request, 'agriculture/realtime_weather.html', context)

# NEW: View function for Weather Forecast
def weather_forecast_view(request):
    form = ForecastInputForm()
    forecast_data = None
    weather_error = None
    
    if request.method == 'POST':
        form = ForecastInputForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            forecast_date = form.cleaned_data['forecast_date']

            # Validate forecast_date is not in the past and within a reasonable future range (e.g., 16 days for Open-Meteo)
            today = date.today()
            max_forecast_date = today + timedelta(days=16) # Open-Meteo free tier typically supports up to 16 days forecast

            if forecast_date < today:
                weather_error = "Forecast date cannot be in the past."
            elif forecast_date > max_forecast_date:
                weather_error = f"Forecast available only up to {max_forecast_date.strftime('%Y-%m-%d')} (16 days from today)."
            else:
                # --- Step 1: Geocoding (City Name to Lat/Lon) using Open-Meteo Geocoding API ---
                geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
                
                try:
                    geocode_response = requests.get(geocode_url, timeout=5)
                    geocode_response.raise_for_status()
                    geocode_data = geocode_response.json()

                    if geocode_data and 'results' in geocode_data and geocode_data['results']:
                        first_result = geocode_data['results'][0]
                        latitude = first_result.get('latitude')
                        longitude = first_result.get('longitude')
                        display_city_name = first_result.get('name', city_name)
                        display_country = first_result.get('country', '')
                        display_admin1 = first_result.get('admin1', '')
                        
                        # --- Step 2: Fetch Daily Weather Forecast Data using Open-Meteo Forecast API ---
                        # We request daily data for a range including our forecast_date
                        # Open-Meteo Forecast API: https://open-meteo.com/en/docs
                        weather_url = (f"https://api.open-meteo.com/v1/forecast?"
                                       f"latitude={latitude}&longitude={longitude}&"
                                       f"daily=temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,precipitation_sum,weather_code&"
                                       f"timezone=auto&start_date={forecast_date.strftime('%Y-%m-%d')}&end_date={forecast_date.strftime('%Y-%m-%d')}")

                        weather_response = requests.get(weather_url, timeout=5)
                        weather_response.raise_for_status()
                        daily_forecast_data = weather_response.json()

                        if daily_forecast_data and 'daily' in daily_forecast_data:
                            daily = daily_forecast_data['daily']
                            
                            # Find the data for the specific forecast_date
                            # The API returns arrays, we need to find the index for our date
                            if 'time' in daily and len(daily['time']) > 0:
                                # Assuming only one date is requested, so data will be at index 0
                                forecast_data = {
                                    'city': display_city_name,
                                    'state': display_admin1,
                                    'country': display_country,
                                    'date': forecast_date.strftime('%Y-%m-%d'),
                                    'temperature_max': daily['temperature_2m_max'][0] if daily['temperature_2m_max'] else None,
                                    'temperature_min': daily['temperature_2m_min'][0] if daily['temperature_2m_min'] else None,
                                    'humidity_mean': daily['relative_humidity_2m_mean'][0] if daily['relative_humidity_2m_mean'] else None,
                                    'precipitation_sum': daily['precipitation_sum'][0] if daily['precipitation_sum'] else None,
                                    'weather_code': daily['weather_code'][0] if daily['weather_code'] else None,
                                }
                            else:
                                weather_error = "No forecast data available for the selected date."
                        else:
                            weather_error = "Could not fetch daily weather forecast data for this location."
                    else:
                        weather_error = f"City '{city_name}' not found. Please try a different name or spelling."

                except requests.exceptions.RequestException as e:
                    weather_error = f"Could not connect to weather service. Error: {e}"
                except ValueError:
                    weather_error = "Invalid response from weather service."
                except Exception as e:
                    weather_error = f"An unexpected error occurred: {e}"

    context = {
        'form': form,
        'forecast_data': forecast_data,
        'weather_error': weather_error,
        'title': 'Weather Forecast'
    }
    return render(request, 'agriculture/weather_forecast.html', context)


# Farmer Diary - Create Entry View
def diary_create_view(request):
    if request.method == 'POST':
        form = FarmerDiaryEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diary entry added successfully!')
            return redirect('agriculture:diary_list') # Redirect to the list view after saving
    else:
        form = FarmerDiaryEntryForm()
    
    context = {
        'form': form,
        'title': 'Add New Farmer Diary Entry'
    }
    return render(request, 'agriculture/diary_form.html', context)

# Farmer Diary - List Entries View
def diary_list_view(request):
    entries = FarmerDiaryEntry.objects.all() # Fetch all entries
    
    # Optional: Add filtering by crop_type or event_date
    crop_type_filter = request.GET.get('crop_type')
    if crop_type_filter:
        entries = entries.filter(crop_type__icontains=crop_type_filter) # Case-insensitive search

    # Optional: Add pagination if many entries
    paginator = Paginator(entries, 10) # Show 10 entries per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Get unique crop types for filter dropdown
    unique_crop_types = FarmerDiaryEntry.objects.values_list('crop_type', flat=True).distinct().order_by('crop_type')

    context = {
        'page_obj': page_obj,
        'unique_crop_types': unique_crop_types,
        'selected_crop_type': crop_type_filter,
        'title': 'Farmer Diary Entries'
    }
    return render(request, 'agriculture/diary_list.html', context)

# Farmer Diary - Detail View (to see one entry)
def diary_detail_view(request, pk):
    entry = get_object_or_404(FarmerDiaryEntry, pk=pk) # Get entry by primary key (pk) or show 404
    context = {
        'entry': entry,
        'title': f"Diary Entry: {entry.event_description}"
    }
    return render(request, 'agriculture/diary_detail.html', context)

# Farmer Diary - Update Entry View
def diary_update_view(request, pk):
    entry = get_object_or_404(FarmerDiaryEntry, pk=pk)
    if request.method == 'POST':
        form = FarmerDiaryEntryForm(request.POST, instance=entry) # Pass instance to update existing
        if form.is_valid():
            form.save()
            messages.success(request, 'Diary entry updated successfully!')
            return redirect('agriculture:diary_detail', pk=entry.pk) # Redirect to detail view
    else:
        form = FarmerDiaryEntryForm(instance=entry) # Populate form with existing data
    
    context = {
        'form': form,
        'entry': entry,
        'title': f"Edit Diary Entry: {entry.event_description}"
    }
    return render(request, 'agriculture/diary_form.html', context) # Reuse form template

# Farmer Diary - Delete Entry View
def diary_delete_view(request, pk):
    entry = get_object_or_404(FarmerDiaryEntry, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Diary entry deleted successfully!')
        return redirect('agriculture:diary_list')
    
    context = {
        'entry': entry,
        'title': f"Confirm Delete: {entry.event_description}"
    }
    return render(request, 'agriculture/diary_confirm_delete.html', context) # New template for confirmation