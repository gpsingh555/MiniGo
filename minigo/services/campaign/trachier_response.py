from ...models import Campaign_Trachier, Campaign_Minigo
from django.utils import timezone
     

def upgrade_json_to_model(json_data, data):
    """
    Upgrade JSON data to Campaign_Trachier model instance.

    Args:
        json_data (dict): JSON data to upgrade.

    Returns:
        Campaign_Trachier: Upgraded Campaign_Trachier instance or None if the upgrade fails.
    """
    campaign_data = json_data.get('campaign')

    if json_data.get('success') == True:
        
        Campaign_Trachier.objects.create(
            device=', '.join(campaign_data.get('device')),
            os=', '.join(campaign_data.get('os')),
            cities=', '.join(campaign_data.get('cities')),
            citiesExclude=', '.join(campaign_data.get('citiesExclude')),
            isps=', '.join(campaign_data.get('isps')),
            region=', '.join(campaign_data.get('region')),
            flow=', '.join(campaign_data.get('flow')),
            categories=', '.join(campaign_data.get('categories')),
            trafficChannels=', '.join(campaign_data.get('trafficChannels')),
            title=campaign_data.get('title'),
            description=campaign_data.get('description'),
            url=campaign_data.get('url'),
            currency=campaign_data.get('currency'),
            status=campaign_data.get('status'),
            iurl=campaign_data.get('iurl'),
            created=timezone.datetime.strptime(campaign_data.get('created'), '%Y-%m-%dT%H:%M:%S.%fZ'),
            modified=timezone.datetime.strptime(campaign_data.get('modified'), '%Y-%m-%dT%H:%M:%S.%fZ'),
            payouts=', '.join(campaign_data.get('payouts')),
            creatives=', '.join(campaign_data.get('creatives')),
            hashId=campaign_data.get('hashId'),
            advertiserId=campaign_data.get('advertiserId'),
            campaign_id=campaign_data.get('id'),
            previewUrl=campaign_data.get('previewUrl'),
            commModel=campaign_data.get('commModel'),
            geo=', '.join(campaign_data.get('geo')),
            blockedPubs=', '.join(campaign_data.get('blockedPubs')),
            fallbackUrl=campaign_data.get('fallbackUrl'),
            convTracking=campaign_data.get('convTracking'),
            visibility=campaign_data.get('visibility'),
            subIdsBlocked=', '.join(campaign_data.get('subIdsBlocked')),
            subIdsAllowed=', '.join(campaign_data.get('subIdsAllowed')),
            blacklistPostbackPubs=json_data.get('blacklistPostbackPubs', []),
            whitelistPostbackPubs=json_data.get('whitelistPostbackPubs', []),
            allowSpilloverConv=campaign_data.get('allowSpilloverConv'),
            cancelFallbackConv=campaign_data.get('cancelFallbackConv'),
            redirectType=campaign_data.get('redirectType'),
            impressionUrl=campaign_data.get('impressionUrl'),
            cancelBlockedPbConv=campaign_data.get('cancelBlockedPbConv'),
            scheduleZone=data['timezone'],
            startDate=campaign_data.get('startDate'),
            endDate=campaign_data.get('endDate'),
            s2sRedirectUrl=campaign_data.get('s2sRedirectUrl'),
            s2spubs=', '.join(campaign_data.get('s2spubs')),
            s2sPubSetting=campaign_data.get('s2sPubSetting'),
            whitelistPubsVta=', '.join(campaign_data.get('whitelistPubsVta')),
            s2s_Pubs=', '.join(campaign_data.get('s2sPubs')),
            allowTrafficDiversion=campaign_data.get('allowTrafficDiversion'),
            verticals=', '.join(campaign_data.get('verticals'))
        )
    
        Campaign_Minigo.objects.create(
            campaign_id=campaign_data.get('id'),
            advertiser=data['advertiser_id'],
            campaign_type=data['campaign_type'],
            campaign_name=data['campaign_name'],
            promotion_goal=data['promotion_goal'],
            secondary_goal=data['secondary_goal'],
            re_target=data['re_target'],
            csv_gaid=data['csv_gaid'] if data['re_target'] else None,
            targeting_name=data['targeting_name'],
            application=data['application'],
            preview_url=data['preview_url'],
            currency=data['currency'],
            status=data['status'],
            placement=data['placement'],
            settings=data['settings'],
            countries=str(data['countries']),
            regions=str(data['regions']),
            languages=str(data['language']),
            interest_tags=str(data['interest_tag']),
            age = data['age'],
            networks=str(data['network']),
            os=data['os'],
            os_versions = data['os_versions'],
            devices=data['devices'],
            timezones=data['timezone'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            daily_budget_amount=data['daily_budget_amount'],
            total_budget_amount=data['total_budget_amount'],
            total_budget_payout=data['total_budget_payout'],
            creative_name=data['creative_name'],
            thumbnail=data['thumbnail'],
            creative_optional=data['creative_optional'],
            cta_url=data['cta_url'],
            vta_url=data['vta_url'],
            deeplink=data['deeplink'],
            visibility=data['visibility'],
            ad_title=data['ad_title'],
            ad_description=data['ad_description'],
            kpi=data['kpi'],
            event_screenshot_image_format=data['event_screenshot_image_format'],
            event_screenshot_url_format=data['event_screenshot_url_format'],
            mmp_activation_image_format=data['mmp_activation_screenshot_image_format'],
            mmp_activation_url_format=data['mmp_activation_screenshot_url_format'],
            campaign_description=data['campaign_description'],
            attribution_tools=data['attribution_tools']
            )
            
    
