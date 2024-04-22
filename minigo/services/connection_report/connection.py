import requests
from decimal import Decimal
from datetime import datetime
from collections import deque
from ...models import Campaign_Minigo, Bid
from ..campaign.calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi


def get_conn_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','grossConversions'],"group[]" : ["goal_name", "conn", "campaign_id"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records = response.json()["records"]
    records_dict = []
    for record in records:
        if record['goal_name'] in ['Install', 'Default','default']:
            if record['goal_name'] == 'Default':
                record['goal_name'] = 'Install' 
            records_dict.append(record)
    
    conn_data = {}

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

        conn = record["conn"]
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

        if conn in conn_data:
            conn_data[conn]["conn"] = conn
            conn_data[conn]["goal_name"] = goal_name
            conn_data[conn]["clicks"] += clicks
            conn_data[conn]["grossConversions"] += gross_conversions
            conn_data[conn]['cost'] += cost

        else:
            conn_data[conn] = {
                "conn" : conn if conn else "Others",
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

    return list(conn_data.values())

