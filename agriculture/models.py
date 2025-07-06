# C:\Users\Gourav Rajput\CropCareConnect\agriculture\models.py

from django.db import models

class MarketPrice(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    market = models.CharField(max_length=100)
    commodity = models.CharField(max_length=100)
    variety = models.CharField(max_length=100)
    grade = models.CharField(max_length=50)
    arrival_date = models.DateField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    modal_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.commodity} in {self.market}, {self.district}, {self.state} on {self.arrival_date}"

    class Meta:
        unique_together = ('state', 'district', 'market', 'commodity', 'variety', 'grade', 'arrival_date')
        app_label = 'agriculture'

class RainfallData(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    date = models.DateField()
    year = models.IntegerField()
    month = models.IntegerField()
    avg_rainfall = models.FloatField()
    agency_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Rainfall in {self.district}, {self.state} on {self.date}: {self.avg_rainfall} mm"

    class Meta:
        unique_together = ('state', 'district', 'date')
        app_label = 'agriculture'

# NEW MODEL FOR CROP ADVISORIES AND ALERTS
class CropAdvisory(models.Model):
    ADVISORY_CHOICES = [
        ('DISEASE', 'Disease Alert'),
        ('PEST', 'Pest Alert'),
        ('BEST_PRACTICE', 'Best Practice Advisory'),
        ('GENERAL', 'General Advisory'),
    ]

    crop_name = models.CharField(max_length=100, help_text="e.g., Wheat, Rice, Tomato")
    advisory_type = models.CharField(max_length=20, choices=ADVISORY_CHOICES, default='GENERAL')
    title = models.CharField(max_length=200, help_text="Concise title for the advisory")
    description = models.TextField(help_text="Detailed description of the issue or advice")
    recommendation = models.TextField(blank=True, null=True, help_text="Recommended actions or solutions")
    date_published = models.DateField(auto_now_add=True) # Automatically sets the date when advisory is created
    # You might want to add fields for affected region (State, District) later if needed

    def __str__(self):
        return f"{self.get_advisory_type_display()} for {self.crop_name}: {self.title}"

    class Meta:
        verbose_name_plural = "Crop Advisories" # Improves display name in admin
        ordering = ['-date_published'] # Order by newest first
        app_label = 'agriculture'