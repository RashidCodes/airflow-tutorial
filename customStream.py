#!/usr/bin/env python

import os
from helpers.helpers import ListenAndSave, BearerTokenAuth, set_rules

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
sample_rules = [{"value": "cat"}]

if __name__ == "__main__":

	# Authenticate
	bearer_token = BearerTokenAuth(consumer_key, consumer_secret)

	
	# Set up the rules for filtered streams
	set_rules(auth, sample_rules)

	
	# get some tweets and save them
	get_tweets = ListenAndSave(auth=bearer_token)


	# stream in some tweets and save them
	get_tweets.save_data()

	
