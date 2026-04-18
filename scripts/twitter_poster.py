import os
import logging
import json
from datetime import datetime
from pathlib import Path
import requests
from requests_oauthlib import OAuth1
from audit_logger import audit

logger = logging.getLogger('TwitterPoster')

DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')

def get_auth():
    return OAuth1(
        TWITTER_API_KEY, TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    )

def post_tweet(content: str) -> dict:
    if len(content) > 280:
        logger.warning(f'Tweet too long ({len(content)} chars), truncating')
        content = content[:277] + '...'
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would tweet: {content}')
        return {'id': 'DRY_RUN', 'text': content}
    url = 'https://api.twitter.com/2/tweets'
    response = requests.post(url, json={'text': content}, auth=get_auth())
    result = response.json()
    audit.log('twitter_post', 'twitter_poster', 'twitter',
              {'content': content}, 'approved',
              'success' if 'data' in result else 'failed', 'human')
    return result

def post_thread(tweets: list) -> list:
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would post thread of {len(tweets)} tweets')
        return [{'id': f'DRY_RUN_{i}', 'text': t} for i, t in enumerate(tweets)]
    results = []
    reply_to_id = None
    for tweet_text in tweets:
        data = {'text': tweet_text[:280]}
        if reply_to_id:
            data['reply'] = {'in_reply_to_tweet_id': reply_to_id}
        response = requests.post(
            'https://api.twitter.com/2/tweets',
            json=data, auth=get_auth()
        ).json()
        if 'data' in response:
            reply_to_id = response['data']['id']
            results.append(response['data'])
    return results

def get_tweet_metrics(tweet_id: str) -> dict:
    if DRY_RUN:
        return {'retweets': 0, 'likes': 0, 'replies': 0, 'impressions': 0}
    url = f'https://api.twitter.com/2/tweets/{tweet_id}'
    response = requests.get(url, params={
        'tweet.fields': 'public_metrics'
    }, auth=get_auth())
    return response.json()

if __name__ == '__main__':
    import sys
    content = sys.argv[1] if len(sys.argv) > 1 else 'Test tweet from AI Employee'
    result = post_tweet(content)
    print(json.dumps(result, indent=2))