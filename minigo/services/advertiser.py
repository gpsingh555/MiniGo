import requests
from datetime import datetime
from django.http import JsonResponse
# # from ..models import Trackier_Response

# def create_trachier_response_data(data):
#     try:
#         trachier_response = Trackier_Response.objects.create(
#             number=data.get('id'),
#             name=data.get('name'),
#             redirectType=data.get('redirectType'),
#             modified=datetime.strptime(data.get('modified'), '%Y-%m-%dT%H:%M:%S.%fZ'),
#             created=datetime.strptime(data.get('created'), '%Y-%m-%dT%H:%M:%S.%fZ'),
#             blockedPubs=data.get('blockedPubs', []),
#             fallbackUrl=data.get('fallbackUrl'),
#             meta=data.get('meta', {}),
#             status=data.get('status'),
#             company=data.get('company'),
#             signup_ip=data.get('signup_ip'),
#             tags=data.get('tags', []),
#             region=data.get('region', {}),
#             managers=data.get('managers', []),
#             currency=data.get('currency'),
#             login_attempts=data.get('login_attempts', 0),
#             login=datetime.strptime(data.get('login'), '%Y-%m-%dT%H:%M:%S.%fZ') if data.get('login') else None,
#             phone=data.get('phone'),
#             email=data.get('email'),
#             username=data.get('username'),
#             hashId=data.get('hashId')
#         )
#         return trachier_response
#     except Exception as e:
#         # Handle any exceptions here
#         print(e)
#         return None

def create_advertiser(data):
    url = 'https://api.trackier.com/v2/advertisers'
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '65c217354bf9f72871b1fa131c765c217354bfd1'
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    print(response_data)
    # create_trachier_response_data(response_data)
    return response_data['advertiser']['id']
    
