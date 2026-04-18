import os
import requests
import logging
import json
from datetime import datetime
from pathlib import Path
from audit_logger import audit

logger = logging.getLogger('FacebookInstagramPoster')

DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))

FB_PAGE_ID = os.getenv('FB_PAGE_ID', '')
FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN', '')
IG_USER_ID = os.getenv('IG_USER_ID', '')
IG_ACCESS_TOKEN = os.getenv('IG_ACCESS_TOKEN', '')

def post_to_facebook(content: str) -> dict:
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would post to Facebook: {content[:80]}...')
        return {'id': 'DRY_RUN', 'success': True}
    url = f'https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed'
    response = requests.post(url, data={
        'message': content,
        'access_token': FB_ACCESS_TOKEN
    })
    result = response.json()
    audit.log('facebook_post', 'facebook_poster', FB_PAGE_ID,
              {'content_preview': content[:100]}, 'approved', 
              'success' if 'id' in result else 'failed', 'human')
    return result

def post_to_instagram(content: str, image_url: str = None) -> dict:
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would post to Instagram: {content[:80]}...')
        return {'id': 'DRY_RUN', 'success': True}
    # Step 1: Create media container
    container_url = f'https://graph.facebook.com/v19.0/{IG_USER_ID}/media'
    data = {'caption': content, 'access_token': IG_ACCESS_TOKEN}
    if image_url:
        data['image_url'] = image_url
    else:
        logger.warning('Instagram requires an image. Skipping.')
        return {'error': 'image_required'}
    container_response = requests.post(container_url, data=data).json()
    if 'id' not in container_response:
        return container_response
    # Step 2: Publish container
    publish_url = f'https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish'
    result = requests.post(publish_url, data={
        'creation_id': container_response['id'],
        'access_token': IG_ACCESS_TOKEN
    }).json()
    audit.log('instagram_post', 'instagram_poster', IG_USER_ID,
              {'content_preview': content[:100]}, 'approved',
              'success' if 'id' in result else 'failed', 'human')
    return result

def get_facebook_insights(post_id: str) -> dict:
    if DRY_RUN:
        return {'likes': 0, 'comments': 0, 'shares': 0, 'reach': 0}
    url = f'https://graph.facebook.com/v19.0/{post_id}/insights'
    response = requests.get(url, params={
        'metric': 'post_impressions,post_reactions_by_type_total',
        'access_token': FB_ACCESS_TOKEN
    })
    return response.json()

if __name__ == '__main__':
    import sys
    platform = sys.argv[1] if len(sys.argv) > 1 else 'facebook'
    content = sys.argv[2] if len(sys.argv) > 2 else 'Test post from AI Employee'
    if platform == 'facebook':
        result = post_to_facebook(content)
    elif platform == 'instagram':
        image_url = sys.argv[3] if len(sys.argv) > 3 else None
        result = post_to_instagram(content, image_url)
    print(json.dumps(result, indent=2))