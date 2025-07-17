# C:\Users\Gourav Rajput\CropCareConnect\agriculture\models.py

from django.db import models

# Model for Market Prices Data
class MarketPrice(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    market = models.CharField(max_length=100)
    commodity = models.CharField(max_length=100)
    variety = models.CharField(max_length=100)
    grade = models.CharField(max_length=100, blank=True, null=True)
    arrival_date = models.DateField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    modal_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='Quintal') # e.g., Quintal, Kg

    def __str__(self):
        return f"{self.commodity} in {self.market}, {self.district}, {self.state} on {self.arrival_date}"

    class Meta:
        verbose_name_plural = "Market Prices"
        # Add a unique_together constraint if a combination of these fields should be unique
        # For example, one commodity price per market per day
        unique_together = ('state', 'district', 'market', 'commodity', 'arrival_date')


# Model for Rainfall Data (if you're using it, otherwise can be removed)
class RainfallData(models.Model):
    date = models.DateField(unique=True)
    rainfall_mm = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Rainfall on {self.date}: {self.rainfall_mm} mm"

    class Meta:
        verbose_name_plural = "Rainfall Data"


# Model for Crop Advisories
class CropAdvisory(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_published = models.DateField(auto_now_add=True)
    # NEW FIELDS:
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ('Weather', 'Weather Alert'),
            ('Pest', 'Pest Outbreak'),
            ('Disease', 'Disease Warning'),
            ('Price', 'Price Trend Alert'),
            ('General', 'General Advisory'),
            ('Fertilizer', 'Fertilizer Advisory'),
            ('Irrigation', 'Irrigation Advisory'),
        ],
        default='General'
    )
    severity = models.CharField(
        max_length=20,
        choices=[
            ('Green', 'Informational'),
            ('Yellow', 'Warning'),
            ('Red', 'Critical'),
        ],
        default='Green'
    )
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Specific location or region for the advisory")
    
    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title} ({self.date_published})"

    class Meta:
        verbose_name_plural = "Crop Advisories"
        ordering = ['-date_published', '-severity'] # Order by newest first, then by severity# C:\Users\Gourav Rajput\CropCareConnect\agriculture\models.py

from django.db import models

class MarketPrice(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    market = models.CharField(max_length=100)
    commodity = models.CharField(max_length=100)
    variety = models.CharField(max_length=100)
    grade = models.CharField(max_length=50, blank=True, null=True) # Made blank/null true for flexibility
    arrival_date = models.DateField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    modal_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='Quintal') # Added default unit

    def __str__(self):
        return f"{self.commodity} in {self.market}, {self.district}, {self.state} on {self.arrival_date}"

    class Meta:
        verbose_name_plural = "Market Prices"
        unique_together = ('state', 'district', 'market', 'commodity', 'variety', 'grade', 'arrival_date')
        app_label = 'agriculture'


class RainfallData(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    date = models.DateField()
    avg_rainfall = models.FloatField()
    agency_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Rainfall for {self.district}, {self.state} on {self.date}: {self.avg_rainfall} mm"

    class Meta:
        unique_together = ('state', 'district', 'date')
        verbose_name_plural = "Rainfall Data"
        app_label = 'agriculture'


class CropAdvisory(models.Model):
    # Original fields
    crop_name = models.CharField(max_length=100, help_text="e.g., Wheat, Rice, Tomato", blank=True, null=True) # Made optional
    advisory_type = models.CharField(
        max_length=20,
        choices=[
            ('DISEASE', 'Disease Alert'),
            ('PEST', 'Pest Alert'),
            ('BEST_PRACTICE', 'Best Practice Advisory'),
            ('GENERAL', 'General Advisory'),
        ],
        default='GENERAL'
    )
    title = models.CharField(max_length=200, help_text="Concise title for the advisory")
    description = models.TextField(help_text="Detailed description of the issue or advice")
    recommendation = models.TextField(blank=True, null=True, help_text="Recommended actions or solutions")
    date_published = models.DateField(auto_now_add=True)

    # NEW FIELDS for enhanced advisories
    alert_type = models.CharField( # This field will be used for broader categorization in UI
        max_length=50,
        choices=[
            ('Weather', 'Weather Alert'),
            ('Pest', 'Pest Outbreak'),
            ('Disease', 'Disease Warning'),
            ('Price', 'Price Trend Alert'),
            ('General', 'General Advisory'),
            ('Fertilizer', 'Fertilizer Advisory'),
            ('Irrigation', 'Irrigation Advisory'),
        ],
        default='General'
    )
    severity = models.CharField( # This field will control badge color and sorting
        max_length=20,
        choices=[
            ('Green', 'Informational'),
            ('Yellow', 'Warning'),
            ('Red', 'Critical'),
        ],
        default='Green'
    )
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Specific location or region for the advisory")
    
    def __str__(self):
        # Updated __str__ to reflect new fields
        return f"[{self.get_severity_display()}] {self.title} ({self.date_published})"

    class Meta:
        verbose_name_plural = "Crop Advisories"
        # Updated ordering to prioritize severity
        ordering = ['-date_published', '-severity'] # Order by newest first, then by severity (Red > Yellow > Green)
        app_label = 'agriculture'


class PMKisanBeneficiary(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, null=True, blank=True)
    total_beneficiaries = models.IntegerField(default=0)
    male_beneficiaries = models.IntegerField(null=True, blank=True, default=0)
    female_beneficiaries = models.IntegerField(null=True, blank=True, default=0)
    sc_beneficiaries = models.IntegerField(null=True, blank=True, default=0)
    st_beneficiaries = models.IntegerField(null=True, blank=True, default=0)
    general_beneficiaries = models.IntegerField(null=True, blank=True, default=0)
    as_on_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "PM-KISAN Beneficiaries"
        unique_together = ('state', 'as_on_date')
        app_label = 'agriculture'

    def __str__(self):
        return f"PM-KISAN in {self.state} ({self.as_on_date}): {self.total_beneficiaries} beneficiaries"


class CropProduction(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    crop = models.CharField(max_length=100)
    year = models.IntegerField()
    season = models.CharField(max_length=50, blank=True, null=True)
    area_in_hectares = models.FloatField(null=True, blank=True)
    production_in_tonnes = models.FloatField(null=True, blank=True)
    
    class Meta:
        unique_together = ('state', 'district', 'crop', 'year', 'season')
        verbose_name_plural = "Crop Production Data"
        app_label = 'agriculture'

    def __str__(self):
        return f"{self.crop} - {self.state} ({self.year} {self.season})"


class FarmerDiaryEntry(models.Model):
    # Core Event Details
    event_date = models.DateField(help_text="Date of the farming event")
    crop_type = models.CharField(max_length=100, help_text="e.g., Wheat, Rice, Cotton")
    event_description = models.TextField(help_text="Brief description of the event (e.g., 'Sowing', 'Fertilizer Application', 'Harvesting')")

    # Financial Inputs
    purchase_price_seed = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Cost of seeds/saplings (per unit or total)"
    )
    fertilizer_quantity_kg = models.FloatField(
        null=True, blank=True,
        help_text="Quantity of fertilizer used (in kg)"
    )
    fertilizer_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Total cost of fertilizer"
    )
    diesel_usage_liters = models.FloatField(
        null=True, blank=True,
        help_text="Diesel used for machinery (in liters)"
    )
    diesel_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Total cost of diesel"
    )
    labor_expenses = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Total cost of labor"
    )
    # Custom Input for other expenses/notes
    other_expenses_description = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Description of other expenses (e.g., 'Pesticide cost', 'Irrigation fees')"
    )
    other_expenses_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Amount of other expenses"
    )
    notes = models.TextField(
        null=True, blank=True,
        help_text="Any additional notes or custom inputs for this event"
    )

    # Automatically record when the entry was created/last updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Farmer Diary Entries"
        ordering = ['-event_date', '-created_at'] # Order by newest event first
        app_label = 'agriculture'

    def __str__(self):
        return f"{self.crop_type} - {self.event_description} on {self.event_date}"

    # Property to calculate total expenses for an entry
    @property
    def total_expenses(self):
        total = 0
        if self.purchase_price_seed:
            total += self.purchase_price_seed
        if self.fertilizer_cost:
            total += self.fertilizer_cost
        if self.diesel_cost:
            total += self.diesel_cost
        if self.labor_expenses:
            total += self.labor_expenses
        if self.other_expenses_amount:
            total += self.other_expenses_amount
        return total
