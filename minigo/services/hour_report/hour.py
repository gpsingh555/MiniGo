import requests
from decimal import Decimal
from datetime import datetime
from collections import deque
from ...models import Campaign_Minigo, Bid
from ..campaign.calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi


def get_hour_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "hour", "campaign_id"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default' or record['goal_name'] == 'default' :
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    hour_data = {}

    for record in records_dict:
        camp_xelo = Campaign_Minigo.objects.filter(campaign_id=record["campaign_id"]).first()
        if camp_xelo:
            bid = Bid.objects.filter(campaign=camp_xelo).last()
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

        hour = record["hour"]
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

        if hour in hour_data:
            hour_data[hour]["hour"] = hour
            hour_data[hour]["goal_name"] = goal_name
            hour_data[hour]["clicks"] += clicks
            hour_data[hour]["grossConversions"] += gross_conversions
            hour_data[hour]['cost'] += cost

        else:
            hour_data[hour] = {
                "hour" : hour,
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

    if records:
        for hr in range(0,int(datetime.now().hour)):
            hr = str(hr).zfill(2)
            if hr not in hour_data.keys():
                hour_data[hr] = {
                    "hour" : hr,
                    "clicks": 0,
                    "grossConversions": 0,
                    "cost": "{:.2f}".format(0),
                    "ctr": "{:.2f}".format(0),
                    "cvr": "{:.2f}".format(0),
                    "ecpm": "{:.2f}".format(0),
                    "cpc": "{:.4f}".format(cpc),
                    "cpi": "{:.4f}".format(cpi),
                    "impressions": impressions
                }


    sorted_data = deque()

    # Iterate over the keys of the dictionary in sorted order
    for key in sorted(hour_data.keys(), key=lambda x: int(x)):
        sorted_data.append((key, hour_data[key]))

    # # Convert the deque to a dictionary
    sorted_data = dict(sorted_data)

    return list(sorted_data.values())

