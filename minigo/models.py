from django.db import models
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
import uuid
from decimal import Decimal

# Choices for country field
COUNTRY_CHOICES = [
    ('IN', 'India'),
    ('RU', 'Russia'),
    ('US', 'USA'),
]

# Choices for currency field
CURRENCIES_CHOICES = [
    ('ALL', 'ALL'),
    ('USD', 'USD'),
    ('INR', 'INR'),
    ('RUB', 'RUB'),
]

class Advertiser(models.Model):
    """Model representing an advertiser."""
    advertiser_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100,choices = (
        ('pending', 'pending'),
        ('active', 'active'),
        ('disabled', 'disabled'),
        ('rejected','rejected')
    ), default='pending')
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name    
    
    class Meta:
        verbose_name = "Advertiser Record"
        verbose_name_plural = "Advertiser Records"
    
   
class Country(models.Model):
    """Model representing a country."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.name

class Region(models.Model):
    """Model representing a region."""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Campaign_Minigo(models.Model):
    """Model representing a Minigo campaign."""
    campaign_id = models.IntegerField(primary_key=True)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    
    campaign_type = models.CharField(max_length=100)
    campaign_name = models.CharField(max_length=500)
    promotion_goal = models.CharField(max_length=100)
    secondary_goal = models.CharField(max_length=100)
    re_target = models.CharField(max_length=100, default = "non-target", blank=True)
    csv_gaid = models.ImageField(upload_to='csv_gaids/', blank=True)
    
    targeting_name = models.CharField(max_length=200)
    application = models.CharField(max_length=200)
    preview_url = models.URLField()
    currency = models.CharField(max_length=100, default='USD')
    status = models.CharField(max_length=100, default='Pending')
    placement = models.CharField(max_length=255)
    settings = models.CharField(max_length=100, blank=True)
    countries = models.TextField()
    regions = models.TextField()
    languages = models.TextField()
    interest_tags = models.TextField()
    age = models.CharField(max_length = 200,default = "all")
    networks = models.CharField(max_length=255)
    os = models.CharField(max_length=10000)
    os_versions = models.CharField(max_length = 1000)
    devices = models.CharField(max_length=10000)
    timezones = models.CharField(max_length=10000)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.CharField(max_length=100, null=True, blank=True)
    daily_budget_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_budget_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payouts = models.CharField(max_length=100)
    total_budget_payout = models.DecimalField(max_digits=10, decimal_places=5)
    cac = models.DecimalField(max_digits=10, decimal_places=5, null=True)
    
    creative_name = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    creative_optional = models.ImageField(upload_to='creatives/')
    cta_url = models.URLField(max_length=10000)
    vta_url = models.URLField(max_length=10000, blank=True)
    deeplink = models.URLField(max_length=10000, blank=True)
    payouts = models.CharField(max_length=1000)
    
    visibility = models.CharField(max_length=100, default='Private')
    ad_title = models.CharField(max_length=1000)
    ad_description = models.TextField()
    kpi = models.TextField()
    event_screenshot_image_format = models.ImageField(upload_to='event_screenshots/', blank=True, null=True)
    event_screenshot_url_format = models.URLField(max_length=10000, blank=True)
    mmp_activation_image_format = models.ImageField(upload_to='mmp_activation/', blank=True, null=True)
    mmp_activation_url_format = models.URLField(max_length=10000, blank=True)
    campaign_description = models.TextField()
    attribution_tools = models.CharField(max_length=100)
    
    def __str__(self):
        return self.campaign_name
    
    class Meta:
        verbose_name = "Campaign Record"
        verbose_name_plural = "Campaign Records"
        
class Campaign_Trachier(models.Model):
    """Model representing a Trachier campaign."""
    campaign_id = models.IntegerField(primary_key=True)
    device = models.CharField(max_length=255)
    os = models.CharField(max_length=255)
    cities = models.CharField(max_length=255)
    citiesExclude = models.CharField(max_length=255)
    isps = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    flow = models.CharField(max_length=255)
    categories = models.CharField(max_length=255)
    trafficChannels = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(max_length=10000)
    currency = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    iurl = models.URLField(max_length=10000)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    payouts = models.CharField(max_length=255)
    creatives = models.CharField(max_length=255)
    hashId = models.CharField(max_length=255)
    advertiserId = models.CharField(max_length=255)
    previewUrl = models.URLField(max_length=10000)
    commModel = models.CharField(max_length=255)
    geo = models.CharField(max_length=255)
    blockedPubs = models.CharField(max_length=255)
    fallbackUrl = models.CharField(max_length=255)
    convTracking = models.CharField(max_length=255)
    visibility = models.CharField(max_length=255)
    subIdsBlocked = models.CharField(max_length=255)
    subIdsAllowed = models.CharField(max_length=255)
    blacklistPostbackPubs = models.CharField(max_length=255)
    whitelistPostbackPubs = models.CharField(max_length=255)
    allowSpilloverConv = models.IntegerField()
    cancelFallbackConv = models.IntegerField()
    redirectType = models.CharField(max_length=255)
    impressionUrl = models.URLField(max_length=10000)
    cancelBlockedPbConv = models.IntegerField()
    scheduleZone = models.CharField(max_length=255)
    startDate = models.DateTimeField(default=timezone.now)
    endDate = models.CharField(max_length=255,null = True)
    s2sRedirectUrl = models.CharField(max_length=255)
    s2spubs = models.CharField(max_length=255)
    s2s_Pubs= models.CharField(max_length=255)
    s2sPubSetting = models.CharField(max_length=255)
    whitelistPubsVta = models.CharField(max_length=255)
    allowTrafficDiversion = models.IntegerField()
    verticals = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Trackier Response Record"
        verbose_name_plural = "Trackier Response Records"
        

class TransactionHistory(models.Model):
    CREDIT_MODES = (
        ('Self', 'Self'),
        ('Xeloop', 'Xeloop')
    )
    STATUS_MSGS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected")
    )
    
    code = str(uuid.uuid4())
    def user_directory_path(instance, filename): 
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
        return 'advertiser_{0}/{1}_{2}'.format(instance.advertiser.advertiser_id, instance.code, filename)
        
    
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    transfer_date_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True)
    invoice_download = models.CharField(max_length=500, blank=True)
    amount = models.CharField(max_length=15, blank = True, default = '-')
    credit_mode = models.CharField(max_length=200, choices=CREDIT_MODES, default='Xeloop')
    status = models.CharField(max_length=1000, choices=STATUS_MSGS, default = "Pending")
    update_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.advertiser.name} - {self.amount} - {self.transfer_date_time}"
    
    
    def save(self, *args, **kwargs):
        if self.image:
            # Set invoice_download to the URL of the uploaded image
            timestamp = str(timezone.now().timestamp()).replace('.', '')
            self.invoice_download = settings.MEDIA_URL + 'advertiser_{0}/{1}_{2}'.format(self.advertiser.advertiser_id, self.code, self.image.name)
        super(TransactionHistory, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Transaction Record"
        verbose_name_plural = "Transaction Records"
        

class Bid(models.Model):
    advertiser = models.ForeignKey(Advertiser, on_delete = models.CASCADE)  
    campaign = models.ForeignKey(Campaign_Minigo, on_delete = models.CASCADE)  
    bid_type = models.CharField(max_length = 100, default = "CPI")
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits = 10, decimal_places = 2)
    
    class Meta:
        verbose_name = "Bid Record"
        verbose_name_plural = "Bid Records"
        

class Cost_minute(models.Model):
    advertiser = models.ForeignKey(Advertiser, on_delete = models.CASCADE)  
    campaign = models.ForeignKey(Campaign_Minigo, on_delete = models.CASCADE)  
    bid = models.ForeignKey(Bid, on_delete = models.CASCADE)  
    value = models.DecimalField(max_digits = 10, decimal_places = 2)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Cost/min Record"
        verbose_name_plural = "Cost/min Records"
    

class Accounts(models.Model):
    advertiser = models.ForeignKey(Advertiser, on_delete = models.CASCADE)
    balance = models.DecimalField(max_digits = 10, decimal_places = 2)
    
    class Meta:
        verbose_name = "Account Record"
        verbose_name_plural = "Account Records"
        
        
class impressions(models.Model):
    date = models.DateField(default=timezone.now)
    campaign_id = models.IntegerField()
    impression = models.IntegerField()
    clicks = models.IntegerField()
    
    def __str__(self):
        return f"{self.date} - {self.campaign_id}"
    
    class Meta:
        verbose_name = "Impression Record"
        verbose_name_plural = "Impression Records"
        unique_together = (('date', 'campaign_id'),)
        
        
class SiteID(models.Model):
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign_Minigo, on_delete=models.CASCADE)
    site_id = models.CharField(max_length = 10000)
    pub_id = models.CharField(max_length = 10000)
    
    def __str__(self):
        return f"{self.site_id}"
    
    class Meta:
        verbose_name = "Site ID Record"
        verbose_name_plural = "Site ID Records"
        
        
class Impressions_minute(models.Model):
    campaign_id = models.IntegerField()
    impression = models.IntegerField()
    clicks = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Impressions/min Record"
        verbose_name_plural = "Impressions/min Records"
        unique_together = (('created_at', 'campaign_id'),)