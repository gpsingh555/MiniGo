import requests
import datetime
import pytz
from collections import defaultdict
from ...models import Campaign_Minigo, Bid, Advertiser
from ..campaign.calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi


def get_country_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None, group = None):
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "country", "campaign_id"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default']:
            if record['goal_name'] == 'Default':
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
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
            record['cost'] = round(record['clicks'] * record['payout'], 2)
        else:
            record['cost'] = round(record['grossConversions'] * record['payout'], 2)

        record['impressions'] = generate_impression(campaign_id=record['campaign_id'], clicks=record['clicks'])
        record['ctr'] = "{:.2f}".format(calculate_ctr(clicks=record['clicks'], impressions=record['impressions']))
        record['cvr'] = "{:.2f}".format(calculate_cvr(installs=record['grossConversions'],clicks= record['clicks']))
        record['cpc'] = "{:.4f}".format(calculate_cpc(cost=record['cost'],clicks= record['clicks']))
        record['cpi'] = "{:.4f}".format(calculate_cpi(cost=record['cost'], installs=record['grossConversions']))
        record['ecpm'] = "{:.2f}".format(calculate_ecpm(cost=record['cost'], impressions=record['impressions']))
            
    return records_dict


def get_clicks(id, campaign_id=None, start_date=None, end_date=None):
    url = f"https://api.trackier.com/v2/reports/clicks"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }

    params = {"fields[]" : ["city", "advertiser_id"]}

    response = requests.get(url, params=params, headers=headers)

    records = response.json()["clicks"]
    
    counts_dict = {}

    # Iterate over the data list
    for entry in records:
        advertiser_id = entry["advertiser_id"]
        city = entry["city"]

        # Check if the advertiser_id key exists in the dictionary
        if advertiser_id in counts_dict:
            # Check if the city key exists for this advertiser_id
            if city in counts_dict[advertiser_id]:
                # Increment the count
                counts_dict[advertiser_id][city] += 1
            else:
                # Initialize the city count
                counts_dict[advertiser_id][city] = 1
        else:
            # Initialize the advertiser_id and city count
            counts_dict[advertiser_id] = {city: 1}
            
    return counts_dict[id]
    

def get_installs(advertiser_id, campaign_id=None, start_date=None, end_date=None):
    end_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
    # start_date = datetime.datetime(2024, 3, 16, tzinfo=pytz.timezone('Asia/Kolkata'))
    
    url = f"https://api.trackier.com/v2/network/conversions"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    params = {"fields[]" : ["city", "advertiser_id", "goal_name"],'adv_ids[]' : advertiser_id, 'end' : end_date, 'start' : "2024-02-27 04:00:00"}

    response = requests.get(url, params=params, headers=headers)

    records = response.json()["conversions"]
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default']:
            if record['goal_name'] == 'Default':
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    counts_dict = {}

    # Iterate over the data list
    for entry in records_dict:
        advertiser_id = entry["advertiser_id"]
        city = entry["city"]

        # Check if the advertiser_id key exists in the dictionary
        if advertiser_id in counts_dict:
            # Check if the city key exists for this advertiser_id
            if city in counts_dict[advertiser_id]:
                # Increment the count
                counts_dict[advertiser_id][city] += 1
            else:
                # Initialize the city count
                counts_dict[advertiser_id][city] = 1
        else:
            # Initialize the advertiser_id and city count
            counts_dict[advertiser_id] = {city: 1}
            
    return counts_dict[advertiser_id]


def get_city_records(advertiser_id, campaign_id=None, start_date=None, end_date=None):
    
    Clicks = get_clicks(advertiser_id, campaign_id, start_date, end_date)
    Installs = get_installs(advertiser_id, campaign_id, start_date, end_date)
    
    try:
        # camp_xelo = Campaign_Xelo.objects.get(campaign_id = campaign_id)
        advertiser = Advertiser.objects.get(advertiser_id=advertiser_id)
        bid = Bid.objects.filter(advertiser=advertiser).order_by('-id').first()
        bid_type = bid.bid_type
        bid_value = bid.value
    except:
        camp_xelo = None
        bid = None
        bid_type = None
        bid_value = None
    
    all_cities = set(list(Clicks.keys()) + list(Installs.keys()))

    combined_data = []
    for city in all_cities:
        clicks = Clicks.get(city, 0)
        installs = Installs.get(city, 0)
        impressions = 0
        cost = clicks * bid_value if bid_type == 'CPC' else installs * bid_value
        ctr = "{:.2f}".format(calculate_ctr(clicks, impressions))
        cvr = "{:.2f}".format(calculate_cvr(installs,clicks))
        cpc = "{:.4f}".format(calculate_cpc(cost=cost,clicks=clicks))
        cpi = "{:.4f}".format(calculate_cpi(cost=cost, installs=installs))
        ecpm = "{:.2f}".format(calculate_ecpm(cost, impressions))
        combined_data.append({
            'city': city,
            'clicks': clicks,
            'installs': installs,
            'impressions' : impressions,
            'cost' : cost,
            'ctr' : ctr,
            'cvr' : cvr,
            'ecpm' : ecpm,
            'cpc' : cpc,
            'cpi' : cpi,
        })

    # print(combined_data)
    return combined_data

           