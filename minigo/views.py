from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Advertiser, Country, Campaign_Minigo
from .services.advertiser import create_advertiser
from .services.campaign.api import create_campaign, update_campaign_status, get_campaign_reports, get_daily_reports, get_country_campaign_records
from .services.country.country import get_country_records
from .services.city.city import get_city_records
from .services.placements.placements import get_placement_records, get_oem_records, get_inapp_records, get_directapp_records, get_site_id_records, get_event_reports
from .services.cost.cost import get_cost, get_daily_cost, get_lifetime_cost, get_campaign_cost, get_daily_campaign_cost, get_lifetime_campaign_cost
from .services.hour_report.hour import get_hour_records
from .services.isp_report.isp import get_isp_records
from .services.connection_report.connection import get_conn_records
from .services.os_report.os import get_os_records
from .services.device_report.device import get_device_records
from .services.daily_report.daily import get_daily_records
from .services.advertiser import create_advertiser
import os
from collections import defaultdict
import pytz
import csv
from datetime import datetime, time, timedelta, date
from .forms import SignupForm, LoginForm, CampaignStepOneForm



def get_advertiser(email):
    return get_object_or_404(Advertiser, email=email)


class SignupView(View):
    """View for user signup."""
    
    def get(self, request):
        """Render the signup form."""
        form = SignupForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        """Handle user signup."""
        form = SignupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            data = {
                "name": name,
                "email": email,
                "password": password,
                "status" : "pending"
            }
            advertiser_id = create_advertiser(data)
            Advertiser.objects.create(advertiser_id=advertiser_id, name=name, email=email, password=password)
            User.objects.create_user(email=email, username=email, password=password)
            messages.success(request, "Your Advertiser Account is Under Verification.")
            
            # return redirect('login')
        return render(request, 'signup.html', {'form': form})


def login_view(request):
    """View for user login."""
    reload_login = request.user.is_authenticated
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            try:
                status = Advertiser.objects.get(email=email).status
            except Advertiser.DoesNotExist:
                status = 'pending'
            if user is not None:
                if status == 'active':
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, "Your Advertiser Account is Under Verification.")
            else:
                messages.error(request, "Email/Password is wrong!!!")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'reload_login' :reload_login})

@login_required    
def logout(request):
    auth.logout(request)
    return redirect('login')


def timezone_helper():
    # Get the user's timezone offset from UTC in hours and minutes
    offset_hours = timezone.localtime(timezone.now()).strftime('%z')
    offset_minutes = int(offset_hours[-2:]) // 15 * 15  # Round minutes to nearest 15
    offset_hours = int(offset_hours[:-2]) + offset_minutes // 60
    offset_minutes %= 60

    # Format the offset into a string like "UTC ±HH:MM"
    offset_sign = '+' if offset_hours >= 0 else '-'
    offset_hours = abs(offset_hours)
    offset_minutes_str = '{:02d}'.format(offset_minutes)
    timezone_string = f"Time Zone: UTC {offset_sign}{offset_hours:02d}:{offset_minutes_str}"
    
    return timezone_string

@login_required
def dashboard_section_view(request):
    """View for the dashboard section."""
    
    advertiser_email = request.user.username
    advertiser = get_object_or_404(Advertiser, email=advertiser_email)
    campaigns = Campaign_Minigo.objects.filter(advertiser=advertiser)
    
    account = {
            'balance' : get_cost(advertiser_id=advertiser.advertiser_id),
            'daily' : get_daily_cost(advertiser_id=advertiser.advertiser_id),
            'lifetime' : get_lifetime_cost(advertiser_id=advertiser.advertiser_id)
        }

    campaign_data = []
    status = {
        'Active': 0,
        'Paused' : 0,
        'Pending': 0,
        'Rejected': 0,
    }
    
    cost_records = get_campaign_cost(advertiser_id=advertiser.advertiser_id)
    daily_camp_rec = get_daily_campaign_cost(advertiser_id=advertiser.advertiser_id)
    lifetime_camp_rec = get_lifetime_campaign_cost(advertiser_id=advertiser.advertiser_id)
    
    ## campaign status
    for i, campaign in enumerate(campaigns):
        campaign_data.append({
            'index': i + 1,
            'campaign_id': campaign.campaign_id,
            'advertiser_id': advertiser.advertiser_id,
            'balance' : cost_records[campaign.campaign_id] if campaign.campaign_id in cost_records.keys() else 0.0,
            'daily' : daily_camp_rec[campaign.campaign_id] if campaign.campaign_id in daily_camp_rec.keys() else 0.0,
            'lifetime' : lifetime_camp_rec[campaign.campaign_id] if campaign.campaign_id in lifetime_camp_rec.keys() else 0.0,
        })
        if campaign.status != 'Disabled':
            status[campaign.status] += 1
    campaign_data = campaign_data[:5] if len(campaign_data)>5 else campaign_data
    
    return render(request, 'index.html', {'campaign_data': campaign_data,'status' : status, 'timezone' : timezone_helper(), 'advertiser_id' : advertiser.advertiser_id, "account" : account})

@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign_id')
        status = request.POST.get('status')
        if update_campaign_status(campaign_id=campaign_id, status = status):
            try:
                camp_xelo = Campaign_Minigo.objects.get(campaign_id=campaign_id)
                camp_xelo.status = status.capitalize()
                camp_xelo.save()
            except:
                pass
            
        return JsonResponse({'message': 'Status updated successfully'})
    return JsonResponse({'message': 'Invalid request'}, status=400)


def get_custom_search(request):
    search = request.GET.get('search', '')
    start_date = request.GET.get('from_date', datetime.now().date().strftime("%Y-%m-%d"))
    end_date = request.GET.get('to_date', datetime.now().date().strftime("%Y-%m-%d"))
    filter_checkboxes = request.GET.getlist('filter_checkboxes[]', [])
    table_checkboxes = request.GET.getlist('table_checkboxes[]', [])
    order_by = request.GET.get('order_by', '')
    
    order = {'6': 'impressions', '7' : 'clicks', '8' : 'grossConversions'}

    advertiser_email = request.user.username
    advertiser = get_object_or_404(Advertiser, email=advertiser_email)
    
    if search:
        campaigns = list(Campaign_Minigo.objects.filter(advertiser=advertiser).filter(Q(campaign_name__icontains=search) | Q(campaign_id__icontains=search) | Q(placement__icontains=search)))
        campaigns = [campaign.campaign_id for campaign in campaigns]
    else :
        campaigns = None

    records = get_campaign_reports(advertiser_id=advertiser.advertiser_id, campaign_id=campaigns, start_date=start_date, end_date=end_date)

    custom_table_filters = {'all': True, 'impression': True, 'cost': True, 'ctr': True, 'cvr': True, 'ecpm': True, 'cpc': True, 'cpi': True}

    # modified_selected_filters = dict(selected_filters)
    modified_custom_table_filters = dict(custom_table_filters)

    if table_checkboxes:
        for key in custom_table_filters.keys():
            modified_custom_table_filters[key] = key in table_checkboxes
            
    if not 'all' in filter_checkboxes:
        filtered_records = []
        for record in records:
            if record['status'] in filter_checkboxes:
                filtered_records.append(record)
        records = filtered_records
        
    if '-' in order_by:
        col = order[order_by[0]]
        records = descend_counting_sort(data=records, key=col)
        
    elif '+' in order_by:
        col = order[order_by[0]]
        records = ascend_counting_sort(data=records, key=col)
    
    context = {
        'customs': modified_custom_table_filters,
        'records': records,
    }

    return render(request, 'table_manage_ads.html', context)
    

def descend_counting_sort(data, key='clicks'):
    counts = defaultdict(list)
    for item in data:
        counts[item[key]].append(item)
    
    sorted_data = []
    for count in range(max(counts.keys()), -1, -1):
        sorted_data.extend(counts[count])
    
    return sorted_data


def ascend_counting_sort(data, key='clicks'):
    counts = defaultdict(list)
    for item in data:
        counts[item[key]].append(item)
    
    sorted_data = []
    for count in range(min(counts.keys()), max(counts.keys()) + 1):
        sorted_data.extend(counts[count])
    
    return sorted_data

@login_required
def manage_ads_section_view(request):
    """View for managing ads."""

    advertiser = get_advertiser( request.user.username)
    
    selected_filters = {'all': True, 'active': True, 'pending': True, 'pause': True, 'rejected': True}
    custom_table_filters = {'all': True, 'impression': True, 'cost': True, 'ctr': True, 'cvr': True, 'ecpm': True, 'cpc': True, 'cpi': True}

    records = get_campaign_reports(advertiser_id = advertiser.advertiser_id)
            
    context = {
        'filters' : selected_filters,
        'customs' : custom_table_filters,
        'records': records,
        'advertiser_id': advertiser.advertiser_id, 
        'timezone': timezone_helper(),        
    }
    
    return render(request, 'manage_ad.html', context)

@login_required
def create_campaign_section_view(request):
    advertiser_email = request.user.username
    advertiser = get_object_or_404(Advertiser, email=advertiser_email)
    current_step = request.path.strip('/').split('/')[-1]

    if current_step == 'campaign':
        form = CampaignStepOneForm(request.POST, request.FILES)
        if request.method == 'POST' and form.is_valid():
            csv_gaid_path = save_uploaded_file(request.FILES.get('csv_gaid'), 'csv_gaids')
            data_step1 = {
                'campaign_type': form.cleaned_data['campaign_type'],
                'campaign_name': form.cleaned_data['campaign_name'],
                'promotion_goal': form.cleaned_data['promotion_goal'],
                'secondary_goal': form.cleaned_data['secondary_goal'],
                're_target' : form.cleaned_data['re_target'],
                'csv_gaid' : csv_gaid_path
            }
            request.session['data_step1'] = data_step1
            return redirect('targeting')

        return render(request, 'create_ad.html', {'form': form, 'advertiser_id': advertiser.advertiser_id})

    else:
        return HttpResponse("Invalid step")
    
def save_uploaded_file(file, folder):
    if not file:
        return None
    original_file_name, file_extension = os.path.splitext(file.name)
    new_file_name = f"{slugify(original_file_name)}{file_extension}"
    file_path = os.path.join(settings.MEDIA_ROOT, folder, new_file_name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path
 