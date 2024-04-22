import requests
from decimal import Decimal
from collections import defaultdict
from ..campaign.api import getall_campaigns
from ...models import Campaign_Minigo, Bid
from ..campaign.calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi


def get_country_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "country", "campaign_id"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    records = response.json()["records"]
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    country_data = {}

    for record in records_dict:
        try:
            camp_xelo = Campaign_Minigo.objects.get(campaign_id=record["campaign_id"])
            bid = Bid.objects.filter(campaign=camp_xelo).last()
            bid_type = bid.bid_type
            bid_value = bid.value
            
        except (Campaign_Minigo.DoesNotExist, Bid.DoesNotExist):
            camp_xelo = None
            bid = None
            bid_type = None
            bid_value = None

        country = record["country"]
        goal_name = record["goal_name"]
        clicks = record["clicks"]
        gross_conversions = record["grossConversions"]
        if bid_type == 'CPC':
            cost = Decimal("{:.2f}".format(round(clicks * bid_value, 2)))
            cpi = Decimal("{:.4f}".format(calculate_cpi(cost=cost, installs=gross_conversions))) 
            cpc = Decimal("{:.4f}".format(bid_value))
        else: 
            cost = Decimal("{:.2f}".format(round(gross_conversions * bid_value, 2)))
            cpc = Decimal("{:.4f}".format(calculate_cpc(cost=cost, clicks=clicks)))
            cpi = Decimal("{:.4f}".format(bid_value))
            
        impressions = generate_impression(campaign_id=record['campaign_id'], start_date=start_date, end_date=end_date)
        ctr = "{:.2f}".format(round(calculate_ctr(clicks=clicks, impressions=impressions),2))
        cvr = "{:.2f}".format(round(calculate_cvr(installs=gross_conversions, clicks=clicks),2))
        ecpm = "{:.2f}".format(round(calculate_ecpm(cost=cost, impressions=impressions),2))

        if country in country_data:
            country_data[country]["country"] = country
            country_data[country]["goal_name"] = goal_name
            country_data[country]["clicks"] += clicks
            country_data[country]["grossConversions"] += gross_conversions
            country_data[country]['cost'] += cost

        else:
            country_data[country] = {
                'country' : country,
                'goal_name' : goal_name,
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
    
    
    