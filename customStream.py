#!/usr/bin/env python

import os
from helpers.helpers import ListenAndSave, BearerTokenAuth, set_rules

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
sample_rules = [{"value": "#pycon2022 (python OR pycon OR jupyter)"}]

bearer_token = BearerTokenAuth(consumer_key, consumer_secret)

if __name__ == "__main__":

	
	# Set up the rules for filtered streams
	set_rules(bearer_token, sample_rules)

	
	# get some tweets and save them
	get_tweets = ListenAndSave(auth=bearer_token)


	# stream in some tweets and save them
	get_tweets.save_data()

	
