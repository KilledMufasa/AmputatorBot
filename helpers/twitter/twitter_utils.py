import sys
from typing import Optional, List

from helpers import logger
from helpers.utils import check_if_cached

log = logger.get_log(sys)


# Check if the tweet is a retweet (either official or non-official)
def check_if_retweet(tweet, body) -> bool:
    if hasattr(tweet, 'retweeted_status') or "RT @" in body:
        return True

    return False


# Get all URLs of the tweet that are cached
def get_cached_tweet_urls(tweet) -> Optional[List[str]]:
    try:
        urls = tweet.entities['urls']
        expanded_urls = []
        for url in urls:
            expended_url = url['expanded_url']
            if check_if_cached(expended_url):
                expanded_urls.append(expended_url)
        return expanded_urls
    except AttributeError:
        return None


# Get the screen_name of the author of the tweet
def get_twitterer_name(tweet) -> Optional[str]:
    try:
        return tweet.author.screen_name
    except AttributeError:
        log.info(f"Couldn't get user screen_name of tweet {tweet.id}")
        return None


# Generate a reply tweet
def generate_tweet(links) -> Optional[str]:
    # Initialize all variables
    canonical_text_latest, canonical_text_list, canonical_text = "", "", ""
    n_canonicals = 0

    # Loop through all links, and generate the canonical link part of the comment
    for link in links:
        if link.origin and link.origin.is_amp:
            if link.canonical:
                n_canonicals += 1
                canonical_text_latest += link.canonical.url
                canonical_text_list += f"[{n_canonicals}] {link.canonical.url}\n"

    if n_canonicals >= 1:
        if n_canonicals == 1:
            intro_who_wat = "It looks like you shared a cached AMP link. These should load faster, but " \
                            "AMP is controversial because of concerns over privacy and the Open Web: " \
                            "reddit.com/r/AmputatorBot/comments/ehrq3z/why_did_i_build_amputatorbot/ "
            intro_maybe = "Maybe check out the uncached page instead: "
            canonical_text = canonical_text_latest

        else:
            intro_who_wat = "It looks like you shared some cached AMP links. "
            intro_maybe = "Maybe check out the uncached pages instead: "
            canonical_text = canonical_text_list

        tweet_text = intro_who_wat + intro_maybe + canonical_text

        return tweet_text

    log.warning("Couldn't generate reply")
    return None
