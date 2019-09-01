# This Python file uses the following encoding: utf-8
# License: GPL-3 (https://choosealicense.com/licenses/gpl-3.0/)
# Original author: Killed_Mufasa (https://twitter.com/Killed_Mufasa | https://www.reddit.com/user/Killed_Mufasa | https://github.com/KilledMufasa)

# This wonderfull little program is used by u/AmputatorBot (https://www.reddit.com/user/AmputatorBot) to scan u/AmputatorBot's inbox for mentions, and to reply to the correct comment.

# Import a couple of libraries
from bs4 import BeautifulSoup
from random import choice
import requests
import praw
import config
import os
import re
import traceback
import logging

# Set default variables
headers = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0']

# Login to Reddit API using Praw. Reads configuration details out of config.py (not public)
def bot_login():
	print("Loggin in...")
	r = praw.Reddit(username = config.username,
					password = config.password,
					client_id = config.client_id,
					client_secret = config.client_secret,
					user_agent = "eu.pythoneverywhere.com:AmputatorBot:v1.1 (by /u/Killed_Mufasa)")
	print("Successfully logged in!\n")
	return r

def random_headers():
	# Get randomized user agent, set default accept and request English page, all of this is done to prevent 403 errors.
	return {'User-Agent': choice(headers),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Language':'en-US'}

def contains_amp_url(string_to_check):
	# If the string contains an AMP link, return True
	if "/amp" in string_to_check or ".amp" in string_to_check or "amp." in string_to_check or "?amp" in string_to_check or "amp?" in string_to_check or "=amp" in string_to_check or "amp=" in string_to_check and "https://" in string_to_check:
		string_contains_amp_url = True
		return string_contains_amp_url
	
	# If no AMP link was found in the string, return False
	string_contains_amp_url = False
	return string_contains_amp_url

# Main function. Gets the inbox stream, filters for mentions, scans the context for AMP links and replies with the direct link (https://praw.readthedocs.io/en/latest/code_overview/reddit/inbox.html)
def run_bot(r, forbidden_subreddits, mentions_replied_to, mentions_unable_to_reply):
	print("Obtaining the stream of inbox items as they become available.")

	# Get the inbox stream using Praw (initially returns 100 historical items).
	for mention in praw.models.util.stream_generator(r.inbox.mentions):

		# Resets for every mention
		reply_to_parent = False
		mention_could_not_reply = False
		mention_could_reply = False
		parent_is_comment = False
		parent_is_submission = False
		mentions_urls = []
		mentions_non_amp_urls = []
		mentions_non_amps_urls_amount = 0
		mentions_canonical_url = ""
		
		# Print a notice that u/AmputatorBot has been mentioned
		parent = mention.parent()
		print("\n\nu/AmputatorBot has been mentioned. Mention comment ID: " + mention.id + "\nParent comment ID: "+ parent.id)

		# Firguring out if parent is a submission or comment
		print("Checking if parent is a comment or submission...")
		try:
			# Check if the parent is a comment, if yes get comment body
			if(isinstance(parent, praw.models.Comment)):
				print(" [ OK ] The parent #" + parent.id + " is a comment.")
				parent_body = parent.body
				parent_is_comment = True

			# Check if the parent is a submission, if yes get submission body
			if(isinstance(parent, praw.models.Submission)):
				print(" [ OK ] The parent #" + parent.id + " is a submission.")
				parent_body = parent.url
				parent_is_submission = True

		except:
			logging.error(traceback.format_exc())
			print(" [ERROR:Exception] There was a weird instance found.")
			mention_could_not_reply = True

		# Check if the parent comment contains an AMP link
		string_contains_amp_url = contains_amp_url(parent_body)
		if string_contains_amp_url:
			print(" [ OK ] #" + parent.id + " (the parent comment) contains one or more of the keywords.")

			# Check: Is AmputatorBot allowed in called subreddit?
			if mention.subreddit.display_name not in forbidden_subreddits:
				print(" [ OK ] #" + parent.id + " called in a subreddit were the bot is not forbidden.")

				# Check: Has AmputatorBot tried (and failed) to respond to this mention already?
				if parent.id not in mentions_unable_to_reply: 
					print(" [ OK ] #" + parent.id + " hasn't been tried and failed yet.")

					# Check: Has AmputatorBot replied to this mention already?
					if parent.id not in mentions_replied_to:
						print(" [ OK ] #" + parent.id + " hasn't been replied to yet.")

						# Check: Is the mention posted by u/AmputatorBot?
						if not parent.author == r.user.me():
							reply_to_parent = True
							print(" [ OK ] #" + parent.id + " isn't posted by me.\n")
							
						else:
							print(" [ STOP ] #" + parent.id + " is posted by me.\n")

					else:
						print(" [ STOP ] #" + parent.id + " has already been replied to.\n")
				
				else:
					print(" [ STOP ] #" + parent.id + " has already been tried, but failed.\n")
				
			else:
				print(" [ STOP ] #" + parent.id + " was called in a subreddit were bot is forbidden.\n")

		else:
			print(" [ STOP ] #" + parent.id + " parent did not contain an amp link.\n")

		# If the parent is a comment, try to reply with the direct link
		if reply_to_parent:
			try:
				print(parent_body)
				print("Trying to find the submitted url...\n")

				# Scan the comment body for the links
				mentions_urls = re.findall("(?P<url>https?://[^\s]+)", parent_body)
				mentions_urls_amount = len(mentions_urls)

				# Loop through all submitted links	
				for x in range(mentions_urls_amount):

					# Isolate the actual URL (remove markdown) (part 1)
					try:
						mentions_urls[x] = mentions_urls[x].split('](')[-1]
						print("A link: "+ mentions_urls[x] +" was stripped of markdown.\n")
					except Exception as e:
						logging.error(traceback.format_exc())
						print("A link couldn't of didn't have to be trimmed.\n")

					# Isolate the actual URL (remove markdown) (part 2)
					if mentions_urls[x].endswith(')?'):
						mentions_urls[x] = mentions_urls[x][:-2]
						print("Trimmed the link with 2 characters.")
					if mentions_urls[x].endswith(')'):
						mentions_urls[x] = mentions_urls[x][:-1]
						print("Trimmed the link with 1 character.")
					print(mentions_urls[x]+"\n")

					# Check: Is the isolated URL really an amp link?
					string_contains_amp_url = contains_amp_url(mentions_urls[x])
					if string_contains_amp_url:
						print(" [ OK ] The correct Amp link was found: " + mentions_urls[x] + "\n")
						print("Retrieving amp page...\n")

						# Fetch the submitted amp page, if canonical (direct link) was found, save these for later
						try:
							# Fetch submitted amp page
							print("\nNow scanning the Amp link: " + mentions_urls[x] + "\n")
							req = requests.get(mentions_urls[x],headers=random_headers())

							# Make the received data searchable
							print("Making a soup...\n")
							soup = BeautifulSoup(req.text, features= "lxml")
							print("Making a searchable soup...\n")
							soup.prettify()

							# Scan the received data for the direct link
							print("Scanning for all links...\n")
							try:
								# Check for every link on the amp page if it is of the type rel='canonical'
								for link in soup.find_all(rel='canonical'):
									# Get the direct link
									mentions_canonical_url = link.get('href')
									print("Found the normal link: "+mentions_canonical_url+"\n")

									# If the canonical url is the same as the submitted url, don't use it
									if mentions_canonical_url == mentions_urls[x]:
										print(" [Error:If] False positive encounterd (mentions_canonical_url == mentions_urls[x]).")
										mention_could_not_reply = True

									# If the canonical url is unique, add the direct link to the array
									else:
										mentions_non_amps_urls_amount = len(mentions_non_amp_urls)
										mentions_canonical_url_markdown = "["+str(mentions_non_amps_urls_amount+1)+"] **"+mentions_canonical_url+"**"
										mentions_non_amp_urls.append(mentions_canonical_url_markdown)
										print(mentions_non_amp_urls)

							# If no direct links were found, throw an exception	
							except Exception as e:
								logging.error(traceback.format_exc())
								print(" [ERROR:Exception] The direct link could not be found.")
								mention_could_not_reply = True

						# If the submitted page could't be fetched (or something else went wrong), throw an exception
						except Exception as e:
							logging.error(traceback.format_exc())
							print(" [ERROR:Exception] Submitted page could not be fetched or something else")
							mention_could_not_reply = True
							
					# If the program fails to get the correct amp link, ignore it.
					else:
						print(" [ERROR:else:] This link is no AMP link: "+mentions_urls[x])

			# If the program fails to find any link at all, throw an exception
			except Exception as e:
					logging.error(traceback.format_exc())
					print(" [ERROR:Exception] Looks like something went wrong trying to find the non_amp url.")
					mention_could_not_reply = True

			# If no direct links were found, don't reply
			mentions_non_amps_urls_amount = len(mentions_non_amp_urls)
			print("The array of submitted urls")
			print(mentions_non_amp_urls)
			print("The amount of non amp urls found")
			print(mentions_non_amps_urls_amount)
			if mentions_non_amps_urls_amount == 0:
				print(" [ERROR:If] There were no correct direct links found. There will be no reply made.")
				submission_could_not_reply = True

			# If there were direct links found, reply
			else:

				# Try to reply to OP
				try:

					# If there was only one url found, generate a simple comment
					if mentions_non_amps_urls_amount == 1:
						mention_reply = "Beep boop, I'm a bot. It looks like someone shared a Google AMP link. Google AMP pages often load faster, but AMP is a [major threat to the Open Web](https://www.socpub.com/articles/chris-graham-why-google-amp-threat-open-web-15847) and [your privacy](https://www.reddit.com/r/AmputatorBot/comments/c88zm3/why_did_i_build_amputatorbot).\n\nYou might want to visit **the normal page** instead: **"+mentions_canonical_url+"**.\n\n*****\n\n​[^(Why & About)](https://www.reddit.com/r/AmputatorBot/comments/c88zm3/why_did_i_build_amputatorbot)^( | )[^(Mention me to summon me!)](https://www.reddit.com/r/AmputatorBot/comments/cchly3/you_can_now_summon_amputatorbot/)^( | Summoned by a good human )[^(here)](https://www.reddit.com"+mention.context+")^."
					# If there were multiple urls found, generate a multi-url comment
					if mentions_non_amps_urls_amount > 1:
						# Generate string of all found links
						mention_reply_generated = '\n\n'.join(mentions_non_amp_urls)
						# Generate entire comment
						mention_reply = "Beep boop, I'm a bot. It looks like someone shared a couple of Google AMP links. Google AMP pages often load faster, but AMP is a [major threat to the Open Web](https://www.socpub.com/articles/chris-graham-why-google-amp-threat-open-web-15847) and [your privacy](https://www.reddit.com/r/AmputatorBot/comments/c88zm3/why_did_i_build_amputatorbot).\n\nYou might want to visit **the normal pages** instead: \n\n"+mention_reply_generated+"\n\n*****\n\n​[^(Why & About)](https://www.reddit.com/r/AmputatorBot/comments/c88zm3/why_did_i_build_amputatorbot)^( | )[^(Mention me to summon me!)](https://www.reddit.com/r/AmputatorBot/comments/cchly3/you_can_now_summon_amputatorbot/)^( | Summoned by a good human )[^(here)](https://www.reddit.com"+mention.context+")^."

					# Reply to mention
					parent.reply(mention_reply)
					print("Replied to comment #"+parent.id+".\n")
					mention_could_reply = True
					print("Operation succesfull.\n")
					
					# Reply to summoner with confirmation and link.
					r.redditor(str(mention.author)).message("Thx for summoning me!", "The bot has successfully replied to your comment: https://www.reddit.com"+parent.permalink+".\n\nAn easy way to find the comment, is by checking my comment history. Thanks for summoning me, I couldn't do this without you (no but literally). You're a very good human.\n\nYou can leave feedback by contacting u/killed_mufasa, by posting on r/AmputatorBot or by [opening an issue on GitHub](https://github.com/KilledMufasa/AmputatorBot/issues/new).")

				# If the reply didn't got through, throw an exception (can occur when comment gets deleted or when rate limits are exceeded)
				except Exception as e:
					logging.error(traceback.format_exc())
					print(" [ERROR:Exception] Could not reply to post.")
					mention_could_not_reply = True

			# If the reply was successfully send, note this
			if mention_could_reply:
				with open ("mentions_replied_to.txt", "a") as f:
					f.write(parent.id + ",")
					mentions_replied_to.append(parent.id)
					print("Added the mention id to file: mentions_replied_to.txt.\n")
			
			# If the reply could not be made or send, note this
			if mention_could_not_reply:
				with open ("mentions_unable_to_reply.txt", "a") as f:
					f.write(parent.id + ",")
					mentions_unable_to_reply.append(parent.id)
					print("Added the mention id to file: mentions_unable_to_reply.txt.\n")

					# Reply to summoner with confirmation and link.
					r.redditor(str(mention.author)).message("AmputatorBot ran into an error..", "AmputatorBot couldn't reply to the comment or submission you summoned it for: https://www.reddit.com"+parent.permalink+".\n\nThis error has been logged and is being investigated.\n\nThat said, you can leave feedback by contacting u/killed_mufasa, by posting on r/AmputatorBot or by [opening an issue on GitHub](https://github.com/KilledMufasa/AmputatorBot/issues/new).\n\nYou're a very good human for trying <3")

# Get the data of which subreddits the bot is forbidden to post in
def get_forbidden_subreddits():
	if not os.path.isfile("forbidden_subreddits.txt"):
		forbidden_subreddits = []
		print("ERROR: forbidden_subreddits.txt could not be found.")

	else:
		with open("forbidden_subreddits.txt", "r") as f:
			forbidden_subreddits = f.read()
			forbidden_subreddits = forbidden_subreddits.split(",")
			print("forbidden_subreddits.txt was found, the array is now as follows:")
			print(forbidden_subreddits)
			print("The bot is not allowed in these subreddits:", ", ".join(forbidden_subreddits))

	return forbidden_subreddits

# Get the data of which mentions have been replied to
def get_saved_mentions_repliedtos():
	if not os.path.isfile("mentions_replied_to.txt"):
		mentions_replied_to = []
		print("ERROR: mentions_replied_to.txt could not be found")

	else:
		with open("mentions_replied_to.txt", "r") as f:
			mentions_replied_to = f.read()
			mentions_replied_to = mentions_replied_to.split(",")
			print("mentions_replied_to.txt was found, the array is now as follows:")
			print(mentions_replied_to)

	return mentions_replied_to

# Get the data of which mentions could not be replied to (for any reason)
def get_saved_mentions_unabletos():
	if not os.path.isfile("mentions_unable_to_reply.txt"):
		mentions_unable_to_reply = []
		print("ERROR: mentions_unable_to_reply.txt could not be found.")

	else:
		with open("mentions_unable_to_reply.txt", "r") as f:
			mentions_unable_to_reply = f.read()
			mentions_unable_to_reply = mentions_unable_to_reply.split(",")
			print("mentions_unable_to_reply.txt was found, the array is now as follows:")
			print(mentions_unable_to_reply)

	return mentions_unable_to_reply

# Uses these functions to run the bot
r = bot_login()
forbidden_subreddits = get_forbidden_subreddits()
mentions_replied_to = get_saved_mentions_repliedtos()
mentions_unable_to_reply = get_saved_mentions_unabletos()

# Run the program
while True:
	run_bot(r, forbidden_subreddits, mentions_replied_to, mentions_unable_to_reply)