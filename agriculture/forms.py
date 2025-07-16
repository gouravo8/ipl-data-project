# agriculture/forms.py
from django import forms

class CityInputForm(forms.Form):
    city_name = forms.CharField(
        label='Enter City Name',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., New Delhi, Mumbai'})
    )
    # agriculture/forms.py

from django import forms
from .models import FarmerDiaryEntry # Import the new model

# ... (Keep your existing CityInputForm) ...

class FarmerDiaryEntryForm(forms.ModelForm):
    class Meta:
        model = FarmerDiaryEntry
        fields = [
            'event_date', 'crop_type', 'event_description',
            'purchase_price_seed', 'fertilizer_quantity_kg', 'fertilizer_cost',
            'diesel_usage_liters', 'diesel_cost', 'labor_expenses',
            'other_expenses_description', 'other_expenses_amount', 'notes'
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}), # HTML5 date picker
            'event_description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'event_date': 'Date of the farming activity.',
            'crop_type': 'e.g., Wheat, Rice, Tomato.',
            'event_description': 'What happened? (e.g., Sowing, Fertilizing, Harvesting).',
            'purchase_price_seed': 'Cost of seeds/saplings.',
            'fertilizer_quantity_kg': 'Quantity of fertilizer in kg.',
            'fertilizer_cost': 'Total cost of fertilizer.',
            'diesel_usage_liters': 'Diesel used in liters.',
            'diesel_cost': 'Total cost of diesel.',
            'labor_expenses': 'Total cost for labor.',
            'other_expenses_description': 'Describe other costs (e.g., pesticide, irrigation).',
            'other_expenses_amount': 'Amount of other expenses.',
            'notes': 'Any additional details or observations.'
        }
# C:\Users\Gourav Rajput\CropCareConnect\agriculture\forms.py

from django import forms
from .models import FarmerDiaryEntry # Keep existing imports

# Keep your existing CityInputForm
class CityInputForm(forms.Form):
    city_name = forms.CharField(label='Enter City Name', max_length=100)

# NEW: Form for Weather Forecast
class ForecastInputForm(forms.Form):
    city_name = forms.CharField(label='Enter City Name', max_length=100,
                                widget=forms.TextInput(attrs={'placeholder': 'e.g., New Delhi, Mumbai'}))
    forecast_date = forms.DateField(label='Select Forecast Date',
                                    widget=forms.DateInput(attrs={'type': 'date'}),
                                    help_text='Select a date within the next 16 days.')