from django import template
# from django.shortcuts import get_object_or_404
from ..models import Advertiser, Campaign_Minigo

register = template.Library()

@register.simple_tag(name="rejected_campaigns")
def get_recent_rejected_campaigns():
    campaigns = Campaign_Minigo.objects.filter(status='Rejected')
    return campaigns
