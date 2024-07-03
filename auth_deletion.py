from firebase_admin import auth
from firebase_admin import credentials
import firebase_admin
from datetime import datetime, timedelta
import json
import time

def user_record_to_json(user_record):
    user_data = {
        'uid': user_record.uid,
        'email': user_record.email,
        'email_verified': user_record.email_verified,
        'phone_number': user_record.phone_number,
        'display_name': user_record.display_name,
        'photo_url': user_record.photo_url,
        'disabled': user_record.disabled,
        'custom_claims': user_record.custom_claims,
        'metadata': {
            'creation_timestamp': user_record.user_metadata.creation_timestamp,
            'last_sign_in_timestamp': user_record.user_metadata.last_sign_in_timestamp,
        },
        'provider_data': [
            {
                'provider_id': provider.provider_id,
                'uid': provider.uid,
                'email': provider.email,
                'display_name': provider.display_name,
                'photo_url': provider.photo_url
            } for provider in user_record.provider_data
        ]
    }
    return json.dumps(user_data, indent=4)

def check_expired_sign_in(user_record):
    last_sign_in_timestamp = user_record.user_metadata.last_sign_in_timestamp
    if (last_sign_in_timestamp is not None):
        last_sign_in_date = datetime.fromtimestamp(last_sign_in_timestamp / 1000) 
        current_date = datetime.now()
        return (current_date - last_sign_in_date) > timedelta(days=30)
    else:
        return True

def check_not_last_created_in_ten_days(user_record):
    creation_timestamp = user_record.user_metadata.creation_timestamp
    if (creation_timestamp is not None):
        creation_timestamp = datetime.fromtimestamp(creation_timestamp / 1000) 
        current_date = datetime.now()
        return (current_date - creation_timestamp) > timedelta(days=10)
    else:
        return True

cred = credentials.Certificate(f'google-services-firebase.json')


kioskApp = firebase_admin.initialize_app(name="kioskApp", credential=cred)


page = auth.list_users(app=kioskApp)
index = 0
k=[]
while page:
    k=[]
    for user in page.users:
        if (len(user.provider_data)==0) and (check_expired_sign_in(user) or check_not_last_created_in_ten_days(user)):
            k.append(user.uid)
    print(k)
    index += len(k)
    print(index)
    auth.delete_users(k, app=kioskApp)
    page = page.get_next_page()
    
