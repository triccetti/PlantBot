#!/usr/bin/python
from google.cloud import vision
import praw

reddit = praw.Reddit("bot1", user_agent="bot1 user agent") 
subreddit = reddit.subreddit("whatsthisplant")

for submission in subreddit.hot(limit=5):
	print("Title: ", submission.title)
	print("Text: ", submission.selftext)
	print("Url: ", submission.url)
	print("Score: ", submission.score)
	print("---------------------------------\n")

	if("NYC" in submission.title):
		client = vision.ImageAnnotatorClient()
		response = client.annotate_image({
			'image': {'source': {'image_uri': submission.url}},
			'features': [{'type': vision.enums.Feature.Type.TYPE_UNSPECIFIED}],
		})