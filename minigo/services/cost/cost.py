import requests
import json
from datetime import datetime, timedelta

from ...services.campaign.calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi
from ...models import Campaign_Minigo, Bid

def get_current_month_dates():
    now = datetime.now()
    start_date = now.replace(day=1).strftime('%Y-%m-%d')
    end_date = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    end_date = end_date.strftime('%Y-%m-%d')
    return start_date, end_date

def get_cost(advertiser_id=None, campaign_id=None, group=None): 
    
    start_date, end_date = get_current_month_dates()
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id"], "adv_ids[]" : advertiser_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    cost = 0
    for record in records_dict:   
        
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id = record["campaign_id"])
            bid = Bid.objects.get(campaign=camp_xelo)
            bid_type = bid.bid_type
            bid_value = bid.value
        except:
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None
            
        record['payout'] = bid_value if bid else 0.11

        if bid_type == 'CPC':
            cost += float(record['clicks'] * record['payout'])
        else:
            cost += float(record['grossConversions'] * record['payout'])


    return round(cost,2)


def get_daily_cost(advertiser_id=None, campaign_id=None, group=None): 
    
    start_date, end_date = datetime.now().date().strftime("%Y-%m-%d"), datetime.now().date().strftime("%Y-%m-%d")
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id"], "adv_ids[]" : advertiser_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    cost = 0
    for record in records_dict:   
        
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id = record["campaign_id"])
            bid = Bid.objects.get(campaign=camp_xelo)
            bid_type = bid.bid_type
            bid_value = bid.value
        except:
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None
            
        record['payout'] = bid_value if bid else 0.11

        if bid_type == 'CPC':
            cost += float(record['clicks'] * record['payout'])
        else:
            cost += float(record['grossConversions'] * record['payout'])


    return round(cost,2)


def get_lifetime_cost(advertiser_id=None, campaign_id=None, group=None): 
    
    start_date, end_date = datetime.now().date().strftime("%Y-%m-%d"), datetime.now().date().strftime("%Y-%m-%d")
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id"], "adv_ids[]" : advertiser_id, "start" : "2024-02-27", "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    cost = 0
    for record in records_dict:   
        
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id = record["campaign_id"])
            bid = Bid.objects.get(campaign=camp_xelo)
            bid_type = bid.bid_type
            bid_value = bid.value
        except:
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None
            
        record['payout'] = bid_value if bid else 0.11

        if bid_type == 'CPC':
            cost += float(record['clicks'] * record['payout'])
        else:
            cost += float(record['grossConversions'] * record['payout'])


    return round(cost,2)
    
    
def get_campaign_cost(advertiser_id=None, campaign_id=None, group=None): 
    
    start_date, end_date = get_current_month_dates()
    
    print(start_date, end_date)
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id"],"adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    cost_records = {}
    for record in records_dict:   
        
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id = record['campaign_id'])
            bid = Bid.objects.get(campaign=camp_xelo)
            bid_type = bid.bid_type
            bid_value = bid.value
        except:
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None
            
        record['payout'] = bid_value if bid else 0.11

        if bid_type == 'CPC':
            cost = round(record['clicks'] * record['payout'], 2)
        else:
            cost = round(record['grossConversions'] * record['payout'], 2)
            
        cost_records[record['campaign_id']] = cost

    # print("Month", cost_records)
    return cost_records


def get_daily_campaign_cost(advertiser_id=None, campaign_id=None, group=None): 
    
    start_date, end_date = datetime.now().date().strftime("%Y-%m-%d"), datetime.now().date().strftime("%Y-%m-%d")
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id"], "adv_ids[]" : advertiser_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    cost_records = {}
    for record in records_dict:   
        
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id = record["campaign_id"])
            bid = Bid.objects.get(campaign=camp_xelo)
            bid_type = bid.bid_type
            bid_value = bid.value
        except:
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None
            
        record['payout'] = bid_value if bid else 0.11

        if bid_type == 'CPC':
            cost = round(record['clicks'] * record['payout'], 2)
        else:
            cost = round(record['grossConversions'] * record['payout'], 2)

        cost_records[record['campaign_id']] = cost

    return cost_records


def get_lifetime_campaign_cost(advertiser_id=None, campaign_id=None, group=None): 
    
    start_date, end_date = datetime.now().date().strftime("%Y-%m-%d"), datetime.now().date().strftime("%Y-%m-%d")
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id"], "adv_ids[]" : advertiser_id, "start" : "2024-02-27", "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    merged_cost = {}
    for record in records_dict:   
        
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id = record["campaign_id"])
            bid = Bid.objects.get(campaign=camp_xelo)
            bid_type = bid.bid_type
            bid_value = bid.value
        except:
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None
            
        record['payout'] = bid_value if bid else 0.11

        if bid_type == 'CPC':
            cost = round(record['clicks'] * record['payout'], 2)
        else:
            cost = round(record['grossConversions'] * record['payout'], 2)

        merged_cost[record['campaign_id']] = cost
      
    # print("Life", merged_cost)    
    return merged_cost