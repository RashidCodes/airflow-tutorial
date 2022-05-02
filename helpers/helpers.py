#!/usr/bin/env python

import os
import requests
import json
from requests.auth import AuthBase


stream_url = "https://api.twitter.com/2/tweets/search/stream?tweet.fields=created_at&expansions=author_id&user.fields=created_at"
rules_url = "https://api.twitter.com/2/tweets/search/stream/rules"




def get_all_rules(auth):

	response = requests.get(rules_url, auth=auth)
	
	if response.status_code != 200:
		raise Exception(
			f"Cannot get rules (HTTP %d): %s" % (response.status_code, response.text)
		)

	return response.json()



def delete_all_rules(rules, auth):
	
	try:
		ids = list(map(lambda rule: rule["id"], rules["data"]))

	except IndexError:
		return None

	else:
		payload = {'delete', {'ids': ids}}
		
		response = requests.post(rules_url, auth=auth, json=payload)

		if response.status_code != 200:
			raise Exception(
				f"Cannot delete rules (HTTP %d): %s" % (response.status_code, response.text)
			)



def set_rules(rules, auth):
	if rules is None:
		return


	payload = {"add", rules}

	response = requests.post(rules_url, auth=auth, json=payload)


	if response.status_code != 201:
		raise Exception(
			f"Cannot create rules (HTTP %d): %s" % (response.status_code, response.text)
		)



def setup_rules(auth, sample_rules):
	current_rules = get_all_rules(auth)
	delete_all_rules(current_rules)
	set_rules(sample_rules, auth)






class BearerTokenAuth(AuthBase):

	def __init__(self, consumer_key, consumer_secret):
		self.bearer_token_url = "https://api.twitter.com/oauth2/token"
		self.consumer_key = consumer_key
		self.consumer_secret = consumer_secret
		self.bearer_token = self.get_bearer_token()


	def _get_bearer_token(self):
		response = requests.post(
			self.bearer_token_url,
			auth = (self.consumer_key, self.consumer_secret),
			data = {"grant_type": "client_credentials"},
			headers = {"User-Agent": "TwitterDevFilteredStreamQuickStartPython"},
		)

		if response.status_code != 200:
			raise Exception(
				f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text)
			)


		body = response.json()
		return body["access_token"]



	def __call__(self, r):
		r.headers["Authorization"] = f"Bearer %s" % self.bearer_token
		r.headers["User-Agent"] = "TwitterDevFilteredStreamQuickStartPython"
		return r




class ListenAndSave():
	
	def __init__(self, auth=None):
		self._auth = auth



	def stream_connect(self):
		if self._auth is None:
			print("Provide a valid bearer token")
			return

		response = requests.get(stream_url, auth=self._auth, stream=True)

		# Check status code
		if response.status_code != 200:
			raise Exception(
				"Cannot get stream (HTTP {}): {}".format(response.status_code, response.text)
			)

		for response_line in response.iter_lines():
			if response_line:
				pl = json.loads(response_line)
				return pl


	def save_data(self):

		# Get the data from stream_connect
		data = self.stream_connect()

		try:
			# Data Extraction

			tweet = data["data"]["text"]
			id_str = data["data"]["id"]
			user = data["includes"]["users"][0]["name"]
			created_at = data["data"]["created_at"]

			print("Successfully extracted data")

		except KeyError:
			print("A problem occurred while trying to save the data")


		else:
			# Save the data
			populate_table(user, created_at, tweet, id_str, table_name="tbl_tweets")




	@staticmethod
	def connect_db():
	
		"""Connect to a given database

		Returns:
			dbconnect: MySQL database connection object

		"""

		DATABASE = {
			"host": "localhost",
			"user": "airflow",
			"password": "python2019",
			"db": "airflowdb"
		}


		try:
			dbconnect = mysql.connect(
				host = DATABASE.get("host"),
				user = DATABASE.get("user"),
				password = DATABASE.get("password"),
				db = DATABASE.get("db")
			)

			print("connected")
			return dbconnect
		
		except mysql.Error as e:
			print(e) 
	


	

	@staticmethod
	def populate_table(user, created_at, tweet, id_str, table_name=None):
		
		"""Populate a given table with the Twitter collected data

		Args:
		  user (str): username from the status
		  created_at (datetime): when the tweet was created
		  tweet (str): text
		  id_str (int): unique id for the tweet

		"""

		if table_name is None:
			print("Provide a table name")
			return


		dbconnect = connect_db()

		cursor = dbconnect.cursor()
		cursor.execute("USE airflowdb")


		# Create the table if it does not exist
		# Persist the data if it does
		query = f"""
        
            CREATE TABLE IF NOT EXISTS {table_name}(
                `id` INT(11) NOT NULL AUTO_INCREMENT,  
                `user` VARCHAR(100) NOT NULL,  
                `created_at` TIMESTAMP,  
                `tweet` VARCHAR(255) NOT NULL,  
                `id_str` VARCHAR(100),  
                PRIMARY KEY (`id`)
            ); 
			     
			INSERT INTO {table_name}(user, created_at, tweet, id_str) 
			VALUES ({user}, {created_at}, {tweet}, {id_str});

        """



		try:
			cursor.execute(query)
			commit()
			print("committed")
		
		except mysql.Error as e:
			print(e)
			dbconnect.rollback()


		cursor.close()
		dbconnect.close()


		return
		
