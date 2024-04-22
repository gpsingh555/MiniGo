from django.db.models import Sum
from datetime import timedelta, datetime
from ...models import Impressions_minute


def calculate_ctr(clicks, impressions):
    try:
        
        ctr = (clicks*100) / impressions
        return round(ctr,2)
    
    except:
        
        return 0.00
    
    
def calculate_cvr(installs, clicks):
    try:
        
        cvr = (installs*100) / clicks
        return round(cvr, 2)
    
    except:
        
        return 0.00
    
    
def calculate_ecpm(cost, impressions):
    try:
        
        ecpm = (cost*1000)/ impressions
        return round(ecpm, 2)
    
    except:
        
        return 0.00
     
def calculate_cpc(cost, clicks):
    try:
        cpc = cost/clicks
        return cpc
    except:
        return 0.00
    
def calculate_cpi(cost, installs):
    try:
        cpi = cost/installs
        return cpi
    except:
        return 0.00
    

def generate_impression(campaign_id, start_date, end_date):
    
    start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now().date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now().date()
    
    print('start : end', start_date, end_date)
    
    date_range = end_date - start_date

    print('date range', date_range)
    
    total_impressions = 0

    for i in range(date_range.days + 1):
        current_date = start_date + timedelta(days=i)

        # Ensure created_at contains only the date part (without time)
        impressions = Impressions_minute.objects.filter(
            created_at__date=current_date, campaign_id=campaign_id
        ).aggregate(total_impressions=Sum('impression'))['total_impressions']

        # Add the impressions for the current date to the total impressions
        total_impressions += impressions or 0

    print(total_impressions)
    return total_impressions

