#!/usr/bin/python 
import praw
import os
import requests
import base64
import json 
import time
from datetime import date

# Loads submission id's from already identified posts.
def loadIdentified(savefile): 
	try:
		identifications = {}
		with open(savefile, "r") as f:
			for line in f:
				save = line.split() # submission id, request id, identification
				identifications[save[0]] = {"url":save[1], "request":save[2], "id":save[3]}

		return identifications
	except FileNotFoundError:
		# We haven't responded to any submissions!
		return None


# Returns a dictionary of submissions and the url's of the images in a reddit post.
def getNewPosts(subreddit, identified): 
	if(identified is None):
		identified = {}
	for submission in subreddit.new(limit=2): 
		if(submission.id not in identified):
			print("add submission id: " + submission.id)
			if(submission.url is not "" and "imgur" not in submission.url):
				print(submission.url)
				# try to identify using link
				identified[submission.id] = {"url": submission.url, "request": None, "id":  None} 
			else: 
				# try to get url from titles or text.
				image_endings = [".jpg", ".png", ".JPEG"]
				if (any(st in submission.title for st in image_endings)):
					print(submission.title) 
				elif ( any(st in submission.selftext for st in image_endings)):
					print(submission.selftext)
	return identified
 

# Does a request to the plant.id api for the given posts
def queueForIdentification(posts): 
	for subId, json in posts.items(): 
		# only do a request if we don't already have request id
		if(json.get("request") is not None): 
			image_url = requests.get(json.get("url"))
			image_contents = (base64.b64encode(image_url.content)).decode("ascii")  
			images = [("data:" + image_url.headers['Content-Type'] + ";" + "base64," + image_contents)]

			params = {
				#"latitude": 49.194161, # maybe I can get these from zone information in post?
				#"longitude": 16.603017,
				"week": date.today().isocalendar()[1],
				"images": images,
				"key": secret_access_key
			} 

			headers = { "Content-Type": "application/json" } 

			response = requests.post("https://plant.id/api/identify", json=params, headers=headers)
	 
			if response.status_code == 200: 
				json["request"] = response.json().get("id")  
				print(str(json))
				posts[subId] = json 
	return posts


def getSuggestedIdentification(subbmisionIds): 
	for subId, json in subbmisionIds.items():
		print(json.get("request"))
		
		params = {
			"key": secret_access_key,
			"ids": [json.get("request")]
		}
		headers = {
			'Content-Type': 'application/json'
		}

		while True:
			print("Waiting for suggestions...")
			time.sleep(5)
			resp = requests.post('https://plant.id/api/check_identifications', json=params, headers=headers).json()

			print(resp)
			if resp[0]["suggestions"]:
				return resp[0]["suggestions"]
		



def replyToPost(identifications):
	print(identifications)
	for subId, json in identifications:		
		print(subId + " " + str(json))


# Saves the identifications to the given save file 
def saveIdentifications(identifications, savefile):
	with open(savefile, "w") as f: 
		for subId, json in identifications.items():
			f.write(subId + " ")
			f.write(str(json.get("url")))
			f.write(" ")
			f.write(str(json.get("request")))
			f.write(" ")
			f.write(str(json.get("id")))
			f.write("\n")

# Main
if __name__ == "__main__":

	secret_access_key = os.environ['PLANT_BOT']
	reddit = praw.Reddit("bot1", user_agent="bot1 user agent") 
	subreddit = reddit.subreddit("whatsthisplant")
	savefile = "plant_bot_identifications.txt"

	#Open save for already identified submissions
	identified = loadIdentified(savefile) 

	#Search for new posts!
	posts = getNewPosts(subreddit, identified) 

	if(posts is None):
		# what do we want to do here?
		print("No valid posts at this time")
	else:
		# we got posts with valid urls!
		subbmisionIds = queueForIdentification(posts)
		if(subbmisionIds is not None): 
			subbmisionIds = getSuggestedIdentification(subbmisionIds)
			'''result = replyToPost(subbmisionIds)

			print(result)
			'''
	saveIdentifications(subbmisionIds, savefile)