from django.contrib import admin
from .models import Advertiser, Campaign_Minigo, Campaign_Trachier, Country, TransactionHistory, Accounts, impressions, Impressions_minute, Bid, Cost_minute, SiteID
from django.utils.html import format_html
from django.conf import settings

admin.site.register(Advertiser)
admin.site.register(Campaign_Trachier)
admin.site.register(Country)
admin.site.register(impressions)

class TransactionHistoryAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        if obj.image:
            return format_html('<a href="{}">{}</a>'.format(obj.image.url, 'check invoice'))
        else:
            return format_html('<a href="{}">{}</a>'.format(obj.invoice_download, 'check invoice'))
        
    image_tag.short_description = 'invoice_download'

    list_display=['id','advertiser','transfer_date_time','image_tag','amount','credit_mode', 'status', 'update_time']
    list_filter = ['advertiser','transfer_date_time','update_time','status','credit_mode']

admin.site.register(TransactionHistory, TransactionHistoryAdmin)


class AccountsAdmin(admin.ModelAdmin):
        

    list_display=['id','advertiser','balance']
    filter = ['advertiser']

admin.site.register(Accounts, AccountsAdmin)

class Campaign_XeloAdmin(admin.ModelAdmin):
    
    list_display = ('campaign_id', 'advertiser', 'campaign_type', 'campaign_name', 'promotion_goal', 'status', 'start_date', 'end_date', 'total_budget_amount')
    list_filter = ('campaign_id', 'advertiser', 'campaign_type', 'campaign_name', 'promotion_goal', 'status', 'start_date', 'end_date', 'placement')
    
admin.site.register(Campaign_Minigo, Campaign_XeloAdmin)

class BidAdmin(admin.ModelAdmin):
    
    list_display=['id','advertiser','campaign', 'created_at', 'value']
    list_filter = ['advertiser', 'campaign', 'created_at']
    
admin.site.register(Bid, BidAdmin)
    
    
class Cost_minuteAdmin(admin.ModelAdmin):
    
    list_display=['id','advertiser','campaign', 'bid', 'value', 'created_at']
    list_filter = ['advertiser', 'campaign', 'bid', 'created_at']
    
admin.site.register(Cost_minute, Cost_minuteAdmin)

    
class SiteIDAdmin(admin.ModelAdmin):
    
    list_display=['id','site_id','pub_id']
    list_filter = ['site_id','pub_id']
    
admin.site.register(SiteID, SiteIDAdmin)


class ImpAdmin(admin.ModelAdmin):
    
    list_display=['id','campaign_id', 'impression', 'clicks', 'created_at']
    list_filter = ['campaign_id', 'clicks', 'created_at']
    
admin.site.register(Impressions_minute, ImpAdmin)


