#!/bin/zsh


# Script to test endpoint

STREAM_ENDPOINT="https://api.twitter.com/2/tweets/search/stream/rules"
CONTENT_TYPE="application/json"
AUTHORIZATION="Bearer $(echo $APP_ACCESS_TOKEN)"


# Add your rule to the stream
curl -X POST $STREAM_ENDPOINT -H "Content-type: ${CONTENT_TYPE}" -H "Authorization: ${AUTHORIZATION}" -d \
'{
	"delete": {"ids": [1521116032240594944, 1521430215850741761, 1521454449113571329]}
}'




# You can validate that your rule was added successfully by sending the following GET request to the rules endpoint.
#curl -X GET ${STREAM_ENDPOINT} -H "Authorization: ${AUTHORIZATION}"
#
#
## Identify and specify which fields you would like to retrieve
#curl -X GET -H "Authorization: ${AUTHORIZATION}" "https://api.twitter.com/2/tweets/search/stream?tweet.fields=created_at&expansions=author_id&user.fields=created_at"
