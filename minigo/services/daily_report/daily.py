import requests
from datetime import datetime
from decimal import Decimal
from ...models import Campaign_Minigo, Bid
from ..campaign.calculations import calculate_ctr, calculate_cvr, calculate_ecpm, generate_impression, calculate_cpc, calculate_cpi


def get_daily_records(advertiser_id=None, campaign_id=None, start_date=None, end_date=None):
    url = f"https://api.trackier.com/v2/reports/custom"

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }
    
    params = {"kpi[]" : ['clicks','impressions','grossConversions'],"group[]" : ["goal_name", "created", "campaign_id"], "adv_ids[]" : advertiser_id, "camp_ids[]" : campaign_id, "start" : start_date, "end" : end_date}
    response = requests.get(url, params=params, headers=headers)

    records_dict = []
    try:
        records = response.json()["records"]
        for record in records:
            if record['goal_name'] in ['Install', 'Default','default']:
                if record['goal_name'] == 'Default':
                    record['goal_name'] = 'Install' 
                records_dict.append(record)
    
    except Exception as e:
        print(e)
    
    created_data = {}

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

        created = datetime.strptime(record["created"],"%Y-%m-%d").strftime("%d-%m-%Y")
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

        if created in created_data:
            created_data[created]["created"] = created
            created_data[created]["goal_name"] = goal_name
            created_data[created]["clicks"] += clicks
            created_data[created]["grossConversions"] += gross_conversions
            created_data[created]['cost'] += cost

        else:
            created_data[created] = {
                "created" : created,
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

    datewise_data = sorted(list(created_data.values()), key=lambda x: datetime.strptime(x['created'], "%d-%m-%Y"))
    
    return datewise_data

