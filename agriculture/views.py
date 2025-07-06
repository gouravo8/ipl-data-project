# C:\Users\Gourav Rajput\CropCareConnect\agriculture\views.py

from django.shortcuts import render
from .models import MarketPrice, RainfallData, CropAdvisory # Import all models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, date
import json # Import json module for chart data

# NEW VIEW FUNCTION FOR THE HOME PAGE
def home_page(request):
    # Define the options for your home page boxes.
    # Each dictionary represents a box: 'name' is display text, 'url_name' is the Django URL name
    # The 'url_name' should match what you defined in agriculture/urls.py (e.g., 'market_price_list', 'crop_advisory_list')
    options = [
        {'name': 'Market Prices', 'url_name': 'agriculture:market_price_list', 'description': 'Check daily market prices for various commodities.'},
        {'name': 'Crop Advisories & Alerts', 'url_name': 'agriculture:crop_advisory_list', 'description': 'Get advisories on diseases, pests, and best farming practices.'},
        # You can add more options here as you implement them:
        # {'name': 'Government Schemes', 'url_name': 'agriculture:govt_schemes_list', 'description': 'Explore available government agricultural schemes.'},
        # {'name': 'Agricultural News', 'url_name': 'agriculture:news_list', 'description': 'Latest news and updates in agriculture.'},
    ]
    context = {
        'options': options,
        'title': 'CropCareConnect - Your Agricultural Hub'
    }
    return render(request, 'agriculture/home_page.html', context)


def market_price_list(request):
    # ... (Your existing market_price_list view code) ...
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
    all_prices = all_prices.filter(filters)

    # --- Logic for Charting Data ---
    chart_labels = []
    chart_data = []
    chart_commodity = ""
    chart_market = ""
    chart_state = ""

    # Check if the filters result in a single commodity for a specific market and state
    # Ensure there's at least one record before trying to access .first()
    if all_prices.values('commodity', 'market', 'state').distinct().count() == 1 and all_prices.exists():
        single_entry = all_prices.first()
        if single_entry:
            chart_commodity = single_entry.commodity
            chart_market = single_entry.market
            chart_state = single_entry.state

            # Fetch data points for the chart for this specific commodity/market/state
            chart_prices_queryset = MarketPrice.objects.filter(
                commodity=chart_commodity,
                market=chart_market,
                state=chart_state
            )

            if start_date:
                chart_prices_queryset = chart_prices_queryset.filter(arrival_date__gte=start_date)
            if end_date:
                chart_prices_queryset = chart_prices_queryset.filter(arrival_date__lte=end_date)

            chart_prices = chart_prices_queryset.order_by('arrival_date')

            for price in chart_prices:
                chart_labels.append(price.arrival_date.strftime('%Y-%m-%d')) # Date for X-axis
                chart_data.append(float(price.modal_price)) # Modal Price for Y-axis

    # --- Order the filtered data for the table ---
    all_prices = all_prices.order_by('-arrival_date', 'state', 'market', 'commodity')

    # --- Get unique values for filter dropdowns (from ALL data, not just filtered) ---
    unique_states = MarketPrice.objects.values_list('state', flat=True).distinct().order_by('state')
    unique_districts = MarketPrice.objects.values_list('district', flat=True).distinct().order_by('district')
    unique_markets = MarketPrice.objects.values_list('market', flat=True).distinct().order_by('market')
    unique_commodities = MarketPrice.objects.values_list('commodity', flat=True).distinct().order_by('commodity')

    # --- Add Pagination ---
    paginator = Paginator(all_prices, 20) # Show 20 records per page

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
    }
    return render(request, 'agriculture/market_price_list.html', context)


def crop_advisory_list(request):
    # Fetch all crop advisories, ordered by date published (newest first)
    advisories = CropAdvisory.objects.all().order_by('-date_published')

    context = {
        'advisories': advisories,
        'title': 'Crop Advisories & Alerts'
    }
    return render(request, 'agriculture/crop_advisory_list.html', context)