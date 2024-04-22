import requests
import json
from decimal import Decimal
from collections import defaultdict
from .trachier_response import upgrade_json_to_model
from .calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi
from ...models import Campaign_Minigo, Bid

def create_campaign(data, xelo_data):
    """
    Create a campaign using API data.

    Args:
        data (dict): Data for the campaign.

    Returns:
        Campaign_Trachier: The created campaign or None if creation fails.
    """
    url = 'https://api.trackier.com/v2/campaigns'
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    upgrade_json_to_model(response_data, xelo_data)
    return True


def getall_campaigns(advertiser_id=None, campaign_id=None):
    
    url = 'https://api.trackier.com/v2/campaigns'
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }

    params = {"advertiser[]" : advertiser_id}
    response = requests.get(url, params=params, headers=headers)
    campaigns = response.json()["campaigns"]
    
    if campaign_id:
        campaigns = [campaign for campaign in campaigns if campaign['id'] in campaign_id]

    try:
        response_data = []
        for campaign in campaigns:
            response_data.append({
                'status' : campaign['status'],
                'commModel' : campaign['commModel'],
                'campaign_name' : campaign['title'],
                'campaign_id' : campaign['id'],
                'promotional_goal' : 'Install',
            })
        
        return response_data
    
    except:
        return None


def update_campaign_status(campaign_id, status):
    url = f'https://api.trackier.com/v2/campaigns/status'
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    payload = {
        "campaignIds": [campaign_id],
        "status": status
    }
    
    response = requests.post(url, json=payload, headers=headers)
    # response = requests.get(url, headers=headers)
    response_data = response.json()

    return response_data['success']


def get_campaign_reports(advertiser_id=None, campaign_id=None, start_date=None, end_date=None, group = None): 
    
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)
    
    campaigns = getall_campaigns(advertiser_id, campaign_id)

    response_data = response.json()
    records = response_data["records"]
    
    if not campaigns:
        return [{}]
    
    records_dict = {}
    for record in records:
        if record['goal_name'] in ['Install', 'default']:
            records_dict[(record['campaign_id'])] = record

    merged_records = []
    for campaign in campaigns:
        
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id = campaign["campaign_id"])
        except:
            camp_xelo = None
            
        try:
            record = records_dict[(campaign['campaign_id'])]
        except KeyError:
            record = {
                'campaign_id': campaign['campaign_id'],
                'campaign_name' : campaign['campaign_name'],
                'placement' : camp_xelo.placement if camp_xelo else 'In App',
                'clicks': 0,
                'impressions': 0,
                'grossConversions': 0,
                'ctr': '0.00',
                'cvr': '0.00',
                'cost': '0.00',
                'ecpm': '0.00',
                'cpc': '0.0000',
                'cpi': '0.0000',
                'campaign_type':camp_xelo.campaign_type,
                'application': camp_xelo.application,
                'promotional_goal':camp_xelo.promotion_goal,
                'status':camp_xelo.status,
                'country':camp_xelo.countries,
                'langauage':camp_xelo.languages,
                'network':camp_xelo.networks,
                'os':camp_xelo.os,
                'device':camp_xelo.devices,
                'currency':camp_xelo.currency,
                'daily_budget':camp_xelo.daily_budget_amount,
                'total_budget':camp_xelo.total_budget_amount,
                'bid':camp_xelo.total_budget_payout
                
            }
        
        record['payout'] = camp_xelo.total_budget_payout if camp_xelo else 0.11
        record['campaign_type'] = camp_xelo.campaign_type,
        record['application'] = camp_xelo.application,
        record['promotional_goal'] = camp_xelo.promotion_goal,
        record['status'] = camp_xelo.status,
        record['country'] = camp_xelo.countries,
        record['langauage'] = camp_xelo.languages,
        record['network'] = camp_xelo.networks,
        record['os'] = camp_xelo.os,
        record['device'] = camp_xelo.devices,
        record['currency'] = camp_xelo.currency,
        record['daily_budget'] = camp_xelo.daily_budget_amount,
        record['total_budget'] = camp_xelo.total_budget_amount,
        record['bid']=camp_xelo.total_budget_payout

        if campaign['commModel'] == 'cpc':
            record['cost'] = float(record['clicks'] * record['payout'])
            record['cpc'] = record['payout']
            record['cpi'] = "{:.4f}".format(calculate_cpi(cost=record['cost'], installs=record['grossConversions']))
        else:
            record['cost'] = float(record['grossConversions'] * record['payout'])
            record['cpi'] = record['payout']
            record['cpc'] = "{:.4f}".format(calculate_cpc(cost=record['cost'],clicks= record['clicks']))
            

        record['placement'] = camp_xelo.placement if camp_xelo else 'In App'
        record['impressions'] = generate_impression(campaign_id=campaign['campaign_id'], start_date=start_date, end_date=end_date)
        record['campaign_name'] = campaign['campaign_name']
        record['ctr'] = "{:.2f}".format(calculate_ctr(clicks=record['clicks'], impressions=record['impressions']))
        record['cvr'] = "{:.2f}".format(calculate_cvr(installs=record['grossConversions'],clicks= record['clicks']))
        record['ecpm'] = "{:.2f}".format(calculate_ecpm(cost=record['cost'], impressions=record['impressions']))

        del record['campaign_id']
        record.update(campaign)
        merged_records.append(record)

    return merged_records
    

def get_country_campaign_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None, group=None):
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }

    params = {
        "kpi[]": ['clicks', 'impressions', 'grossConversions'],
        "group[]": ["goal_name", "country", "campaign_id"],
        "adv_ids[]": advertiser_id,
        "camp_ids[]": campaign_id,
        "start": start_date,
        "end": end_date
    }

    response = requests.get(url, params=params, headers=headers)
    records = response.json()["records"]
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)

    country_data = {}

    for record in records_dict:

        camp_xelo = Campaign_Minigo.objects.filter(campaign_id=record["campaign_id"]).first()
        if camp_xelo:
            bid = Bid.objects.filter(campaign=camp_xelo).first()
            if bid:
                bid_value = bid.value
                bid_type = bid.bid_type
                record['payout'] = bid_value
            else:
                bid_value = 0.11
                bid_type = None
                record['payout'] = bid_value
        else:
            bid_value = 0.11
            bid_type = None
            record['payout'] = bid_value

        country = record["country"]
        clicks = record["clicks"]
        gross_conversions = record["grossConversions"]
        cost = Decimal(round(clicks * bid_value, 2)) if bid_type == 'CPC' else Decimal(round(gross_conversions * bid_value, 2))
        impressions = record['impressions'] = generate_impression(campaign_id=record['campaign_id'], start_date=start_date, end_date=end_date)
        ctr = calculate_ctr(clicks=clicks, impressions=impressions)
        cvr = calculate_cvr(installs=gross_conversions, clicks=clicks)
        cpc = Decimal(calculate_cpc(cost=cost, clicks=clicks)) if bid_type == 'CPI' else Decimal(bid_value)
        cpi = Decimal(calculate_cpi(cost=cost, installs=gross_conversions)) if bid_type == 'CPC' else Decimal(bid_value)
        ecpm = calculate_ecpm(cost=cost, impressions=impressions)

        if country in country_data:
            country_data[country]["country"] = country
            country_data[country]["clicks"] += clicks
            country_data[country]["grossConversions"] += gross_conversions
            country_data[country]["cost"] += cost
            country_data[country]["ctr"] += ctr
            country_data[country]["cvr"] += cvr
            country_data[country]["ecpm"] += ecpm
            country_data[country]["cpc"] += cpc
            country_data[country]["cpi"] += cpi
            country_data[country]["impressions"] += impressions
        else:
            country_data[country] = {
                "country": country,
                "clicks": clicks,
                "grossConversions": gross_conversions,
                "cost": cost,
                "ctr": ctr,
                "cvr": cvr,
                "ecpm": ecpm,
                "cpc": cpc,
                "cpi": cpi,
                "impressions": impressions
            }


    return list(country_data.values())
  
    

def get_daily_reports(advertiser_id=None, start_date=None, end_date=None): 
    
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "created"], "adv_ids[]" : advertiser_id, "start" : start_date, "end" : end_date}
    
    try:
        response = requests.get(url, params=params, headers=headers) 
        records = response.json()["records"]
        records_dict = []
        for record in records:
            if record['goal_name'] in ['Install', 'Default']:
                if record['goal_name'] in ['Default', 'default']:
                    record['goal_name'] = 'Install' 
                records_dict.append(record)
        return records_dict

    except:
        return [{}]
