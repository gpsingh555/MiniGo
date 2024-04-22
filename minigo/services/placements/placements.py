import requests
from decimal import Decimal
from ..campaign.api import getall_campaigns
from ...models import Campaign_Minigo, Bid, SiteID
from ..campaign.calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi


def get_oem_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    publisher_id=[1002, 1003, 1039, 1085, 1009, 1010]
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id", "campaign_name", "publisher_id", "publisher"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "pub_ids[]" : publisher_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    publisher_data = {}

    # Iterate over each entry in the data
    for entry in records_dict:
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id=entry["campaign_id"])
            bid = Bid.objects.filter(campaign=camp_xelo).last()
            bid_type = bid.bid_type
            bid_value = bid.value
            
        except (Campaign_Minigo.DoesNotExist, Bid.DoesNotExist):
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None

        entry['payout'] = bid_value if bid else 0.11

        publisher_id = entry["publisher_id"]
        clicks = entry["clicks"]
        gross_conversions = entry["grossConversions"]
        cost = round(clicks * entry['payout'], 2) if bid_type == 'CPC' else round(gross_conversions * entry['payout'], 2)
        impressions = generate_impression(campaign_id=entry['campaign_id'], start_date=start_date, end_date=end_date)
        ctr = "{:.2f}".format(calculate_ctr(clicks=clicks, impressions=impressions))
        cvr = "{:.2f}".format(calculate_cvr(installs=gross_conversions,clicks= clicks))
        cpc = "{:.4f}".format(calculate_cpc(cost=cost,clicks= clicks)) if bid_type == 'CPI' else "{:.4f}".format(entry['payout'])
        cpi = "{:.4f}".format(calculate_cpi(cost=cost, installs=gross_conversions)) if bid_type == 'CPC' else "{:.4f}".format(entry['payout'])
        ecpm = "{:.2f}".format(calculate_ecpm(cost=cost, impressions=impressions))

        if publisher_id in publisher_data:
            publisher_data[publisher_id]["clicks"] += clicks
            publisher_data[publisher_id]["grossConversions"] += gross_conversions
            if bid_type == 'CPC':
                publisher_data[publisher_id]['cost'] += cost
                publisher_data[publisher_id]['cpc'] = "{:.4f}".format(entry['payout'])
                publisher_data[publisher_id]['cpi'] = "{:.4f}".format(calculate_cpi(cost=publisher_data[publisher_id]['cost'], installs=publisher_data[publisher_id]["grossConversions"]))
                
            else:
                publisher_data[publisher_id]['cost'] += cost
                publisher_data[publisher_id]['cpc'] = "{:.4f}".format(calculate_cpc(cost=publisher_data[publisher_id]['cost'], clicks=publisher_data[publisher_id]["clicks"]))
                publisher_data[publisher_id]['cpi'] = "{:.4f}".format(entry['payout'])
                
            publisher_data[publisher_id]['impressions'] = impressions
            publisher_data[publisher_id]['ctr'] = "{:.2f}".format(calculate_ctr(clicks=publisher_data[publisher_id]["clicks"], impressions=publisher_data[publisher_id]["impressions"]))
            publisher_data[publisher_id]['cvr'] = "{:.2f}".format(calculate_cvr(installs=publisher_data[publisher_id]["grossConversions"], clicks=publisher_data[publisher_id]["clicks"]))
            publisher_data[publisher_id]['ecpm'] = "{:.2f}".format(calculate_ecpm(cost=publisher_data[publisher_id]['cost'], impressions=publisher_data[publisher_id]['impressions']))
            
        else:
            publisher_data[publisher_id] = {
                "publisher" : entry["publisher"],
                "clicks": clicks,
                "grossConversions": gross_conversions,
                "cost": cost,
                'ctr': ctr,
                'cvr': cvr,
                'ecpm': ecpm,
                'cpc': cpc,
                'cpi': cpi,
            }
    
    # print("oem",records)
    return publisher_data


def get_directapp_records(advertiser_id=None, campaign_id=None, publisher_id=None, start_date=None, end_date=None):
    
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    publisher_id=[1005, 1012, 1006]
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", 'campaign_id', "publisher_id", "publisher"], "adv_ids[]" : advertiser_id, "pub_ids[]" : publisher_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    publisher_data = {}

    # Iterate over each entry in the data
    for entry in records_dict:
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id=entry["campaign_id"])
            bid = Bid.objects.filter(campaign=camp_xelo).last()
            bid_type = bid.bid_type
            bid_value = bid.value
            
        except (Campaign_Minigo.DoesNotExist, Bid.DoesNotExist):
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None

        entry['payout'] = bid_value if bid else 0.11

        publisher_id = entry["publisher_id"]
        clicks = entry["clicks"]
        gross_conversions = entry["grossConversions"]
        cost = round(clicks * entry['payout'], 2) if bid_type == 'CPC' else round(gross_conversions * entry['payout'], 2)
        impressions = generate_impression(campaign_id=entry['campaign_id'], start_date=start_date, end_date=end_date)
        ctr = "{:.2f}".format(calculate_ctr(clicks=clicks, impressions=impressions))
        cvr = "{:.2f}".format(calculate_cvr(installs=gross_conversions,clicks= clicks))
        cpc = "{:.4f}".format(calculate_cpc(cost=cost,clicks= clicks)) if bid_type == 'CPI' else "{:.4f}".format(entry['payout'])
        cpi = "{:.4f}".format(calculate_cpi(cost=cost, installs=gross_conversions)) if bid_type == 'CPC' else "{:.4f}".format(entry['payout'])
        ecpm = "{:.2f}".format(calculate_ecpm(cost=cost, impressions=impressions))

        if publisher_id in publisher_data:
            publisher_data[publisher_id]["clicks"] += clicks
            publisher_data[publisher_id]["grossConversions"] += gross_conversions
            if bid_type == 'CPC':
                publisher_data[publisher_id]['cost'] += cost
                publisher_data[publisher_id]['cpc'] = "{:.4f}".format(entry['payout'])
                publisher_data[publisher_id]['cpi'] = "{:.4f}".format(calculate_cpi(cost=publisher_data[publisher_id]['cost'], installs=publisher_data[publisher_id]["grossConversions"]))
                
            else:
                publisher_data[publisher_id]['cost'] += cost
                publisher_data[publisher_id]['cpc'] = "{:.4f}".format(calculate_cpc(cost=publisher_data[publisher_id]['cost'], clicks=publisher_data[publisher_id]["clicks"]))
                publisher_data[publisher_id]['cpi'] = "{:.4f}".format(entry['payout'])
                
            publisher_data[publisher_id]['impressions'] = impressions
            publisher_data[publisher_id]['ctr'] = "{:.2f}".format(calculate_ctr(clicks=publisher_data[publisher_id]["clicks"], impressions=publisher_data[publisher_id]["impressions"]))
            publisher_data[publisher_id]['cvr'] = "{:.2f}".format(calculate_cvr(installs=publisher_data[publisher_id]["grossConversions"], clicks=publisher_data[publisher_id]["clicks"]))
            publisher_data[publisher_id]['ecpm'] = "{:.2f}".format(calculate_ecpm(cost=publisher_data[publisher_id]['cost'], impressions=publisher_data[publisher_id]['impressions']))
            
        else:
            publisher_data[publisher_id] = {
                "publisher" : entry["publisher"],
                "clicks": clicks,
                "grossConversions": gross_conversions,
                "cost": cost,
                'ctr': ctr,
                'cvr': cvr,
                'ecpm': ecpm,
                'cpc': cpc,
                'cpi': cpi,
            }
    
    return publisher_data


def get_inapp_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    
    url = f"https://api.trackier.com/v2/reports/subid"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id", "app_name"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    # print(response.json())
    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default'] and record['app_name']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    app_data = {}

    # Iterate over each entry in the data
    for entry in records_dict:
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id=entry["campaign_id"])
            bid = Bid.objects.filter(campaign=camp_xelo).last()
            bid_type = bid.bid_type
            bid_value = bid.value
            
        except (Campaign_Minigo.DoesNotExist, Bid.DoesNotExist):
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None

        entry['payout'] = bid_value if bid else 0.11

        app_name = entry["app_name"]
        clicks = entry["clicks"]
        gross_conversions = entry["grossConversions"]
        cost = round(clicks * entry['payout'], 2) if bid_type == 'CPC' else round(gross_conversions * entry['payout'], 2)
        impressions = generate_impression(campaign_id=entry['campaign_id'], start_date=start_date, end_date=end_date)
        ctr = "{:.2f}".format(calculate_ctr(clicks=clicks, impressions=impressions))
        cvr = "{:.2f}".format(calculate_cvr(installs=gross_conversions,clicks= clicks))
        cpc = "{:.4f}".format(calculate_cpc(cost=cost,clicks= clicks)) if bid_type == 'CPI' else "{:.4f}".format(entry['payout'])
        cpi = "{:.4f}".format(calculate_cpi(cost=cost, installs=gross_conversions)) if bid_type == 'CPC' else "{:.4f}".format(entry['payout'])
        ecpm = "{:.2f}".format(calculate_ecpm(cost=cost, impressions=impressions))

        if app_name in app_data:
            app_data[app_name]["clicks"] += clicks
            app_data[app_name]["grossConversions"] += gross_conversions
            if bid_type == 'CPC':
                app_data[app_name]['cost'] += cost
                app_data[app_name]['cpc'] = "{:.4f}".format(entry['payout'])
                app_data[app_name]['cpi'] = "{:.4f}".format(calculate_cpi(cost=app_data[app_name]['cost'], installs=app_data[app_name]["grossConversions"]))
                
            else:
                app_data[app_name]['cost'] += cost
                app_data[app_name]['cpc'] = "{:.4f}".format(calculate_cpc(cost=app_data[app_name]['cost'], clicks=app_data[app_name]["clicks"]))
                app_data[app_name]['cpi'] = "{:.4f}".format(entry['payout'])
                
            app_data[app_name]['impressions'] = impressions
            app_data[app_name]['ctr'] = "{:.2f}".format(calculate_ctr(clicks=app_data[app_name]["clicks"], impressions=app_data[app_name]["impressions"]))
            app_data[app_name]['cvr'] = "{:.2f}".format(calculate_cvr(installs=app_data[app_name]["grossConversions"], clicks=app_data[app_name]["clicks"]))
            app_data[app_name]['ecpm'] = "{:.2f}".format(calculate_ecpm(cost=app_data[app_name]['cost'], impressions=app_data[app_name]['impressions']))
            
        else:
            app_data[app_name] = {
                "publisher" : entry["app_name"],
                "clicks": clicks,
                "grossConversions": gross_conversions,
                "cost": cost,
                'ctr': ctr,
                'cvr': cvr,
                'ecpm': ecpm,
                'cpc': cpc,
                'cpi': cpi,
            }
    
    # print("inapp", records)
    return app_data


def get_site_id_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    campaigns = Campaign_Minigo.objects.filter(campaign_id__in=campaign_id) 
    site_ids = SiteID.objects.filter(campaign__in=campaigns) 
    
    # print(site_ids)
    publisher_id= [site_id.pub_id for site_id in site_ids]
    
    # print(publisher_id)
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id", "publisher_id", "publisher"], "adv_ids[]" : advertiser_id, "pub_ids[]" : publisher_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    publisher_data = {}

    # Iterate over each entry in the data
    for entry in records_dict:
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id=entry["campaign_id"])
            bid = Bid.objects.filter(campaign=camp_xelo).last()
            bid_type = bid.bid_type
            bid_value = bid.value
            
        except (Campaign_Minigo.DoesNotExist, Bid.DoesNotExist):
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None

        entry['payout'] = bid_value if bid else 0.11

        publisher_id = entry["publisher_id"]
        clicks = entry["clicks"]
        gross_conversions = entry["grossConversions"]
        cost = round(clicks * entry['payout'], 2) if bid_type == 'CPC' else round(gross_conversions * entry['payout'], 2)
        impressions = generate_impression(campaign_id=entry['campaign_id'], start_date=start_date, end_date=end_date)
        ctr = "{:.2f}".format(calculate_ctr(clicks=clicks, impressions=impressions))
        cvr = "{:.2f}".format(calculate_cvr(installs=gross_conversions,clicks= clicks))
        cpc = "{:.4f}".format(calculate_cpc(cost=cost,clicks= clicks)) if bid_type != 'CPC' else "{:.4f}".format(entry['payout'])
        cpi = "{:.4f}".format(calculate_cpi(cost=cost, installs=gross_conversions)) if bid_type == 'CPC' else "{:.4f}".format(entry['payout'])
        ecpm = "{:.2f}".format(calculate_ecpm(cost=cost, impressions=impressions))

        if publisher_id in publisher_data:
            publisher_data[publisher_id]["clicks"] += clicks
            publisher_data[publisher_id]["grossConversions"] += gross_conversions
            if bid_type == 'CPC':
                publisher_data[publisher_id]['cost'] += cost
                publisher_data[publisher_id]['cpc'] = "{:.4f}".format(entry['payout'])
                publisher_data[publisher_id]['cpi'] = "{:.4f}".format(calculate_cpi(cost=publisher_data[publisher_id]['cost'], installs=publisher_data[publisher_id]["grossConversions"]))
                
            else:
                publisher_data[publisher_id]['cost'] += cost
                publisher_data[publisher_id]['cpc'] = "{:.4f}".format(calculate_cpc(cost=publisher_data[publisher_id]['cost'], clicks=publisher_data[publisher_id]["clicks"]))
                publisher_data[publisher_id]['cpi'] = "{:.4f}".format(entry['payout'])
                
            publisher_data[publisher_id]['impressions'] = impressions
            publisher_data[publisher_id]['ctr'] = "{:.2f}".format(calculate_ctr(clicks=publisher_data[publisher_id]["clicks"], impressions=publisher_data[publisher_id]["impressions"]))
            publisher_data[publisher_id]['cvr'] = "{:.2f}".format(calculate_cvr(installs=publisher_data[publisher_id]["grossConversions"], clicks=publisher_data[publisher_id]["clicks"]))
            publisher_data[publisher_id]['ecpm'] = "{:.2f}".format(calculate_ecpm(cost=publisher_data[publisher_id]['cost'], impressions=publisher_data[publisher_id]['impressions']))
            
        else:
            publisher_data[publisher_id] = {
                "publisher" : str(SiteID.objects.get(campaign=Campaign_Minigo.objects.get(campaign_id=entry['campaign_id']), pub_id = publisher_id).site_id),
                "clicks": clicks,
                "grossConversions": gross_conversions,
                "cost": cost,
                'ctr': ctr,
                'cvr': cvr,
                'ecpm': ecpm,
                'cpc': cpc,
                'cpi': cpi,
            }
            
    return publisher_data


def get_placement_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    placements = [
        ('OEM', get_oem_records),
        ('In App', get_inapp_records),
        ('Direct App', get_directapp_records),
        # ('Site ID', get_site_id_records)
    ]
    
    records = []
    for placement_name, get_records_func in placements:
        start = "2024-03-10" if placement_name == 'In App' else start_date
        placement_records = get_records_func(advertiser_id=advertiser_id, campaign_id=campaign_id, start_date=start, end_date=end_date)
        clicks_sum, gross_conversions_sum, cost_sum = 0, 0, 0
        
        for entry in placement_records.values():
            clicks_sum += entry['clicks']
            gross_conversions_sum += entry['grossConversions']
            cost_sum += entry['cost']

        record = {'clicks': clicks_sum, 'grossConversions': gross_conversions_sum, 'cost': cost_sum, 'placement': placement_name}
        records.append(record)
    
    # print("placements", records)
    return records


def get_event_reports(advertiser_id=None, campaign_id=None, start_date=None, end_date=None): 
    
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "campaign_id", "campaign_name"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)
    
    try:
        records = response.json()['records']
    except:
        records = [{}]

    return records
    
    