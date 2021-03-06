import calendar
import json
import time
import logging

import feedparser
import requests

from constants import *
from feed import Feed
from feedManager import FeedManager
from webPageLoader import *
import htmlProcessor as hp
from minerJobManager import MinerJobManager
from link import Link
from linkManager import LinkManager
from workerJob import WorkerJob

UNECESSARY_FEED_TAGS = [
  FEEDTAG_TYPE,
  FEEDTAG_NEXTPOLLTIME,
  FEEDTAG_POLLFREQUENCY,
  FEEDTAG_LASTPOLLTIME,
  FEEDTAG_URL,
  FEEDTAG_LASTPUBDATE,
  FEEDTAG_ENTRY_SELECTORS]

logger = logging.getLogger('feedProcessor')

def _deleteUnecessaryFeedTags(feedTags):
    """
    Deletes tags which need not be proppogated from a feed to a link.
    """

    for tagName in UNECESSARY_FEED_TAGS:
        feedTags.pop(tagName, None)

def _putNewLinks(feedAndJobId, linksToAdd):
  linkManager = LinkManager()
  jobManager = MinerJobManager()
  latestPubTime = 0

  for link in linksToAdd:
    try:
      existingLink = linkManager.get(link.id)
      logger.info(
        "Link with id '%s' already exists. Not processing it. %s",
        link.id,
        feedAndJobId)
      continue
    except:
      pass

    linkManager.put(link)
    logger.info(
        "Put link with id '%s' in links database. %s.",
        link.id,
        feedAndJobId)

    if latestPubTime < link.tags[LINKTAG_PUBTIME]:
      latestPubTime  = link.tags[LINKTAG_PUBTIME]

  return latestPubTime;

def _retrieveNewTagsFromFeedEntry(jobId, entry):
  """
  Process the summary detail of rss feed entry.
  Computes tags for the link object being prepared from the feed entry.
  """

  newTags = {};

  # add title
  newTags[LINKTAG_TITLE] = entry.title

  # add summary and image tags
  processingResult = hp.processHtml(
      jobId,
      entry.summary,
      ":not(script)",
      ["img"]);
  newTags[LINKTAG_SUMMARY] = entry.summary;
  newTags[LINKTAG_SUMMARYTEXT] = processingResult[0];
  newTags[LINKTAG_SUMMARYIMAGES] = processingResult[1];

  if entry.published_parsed:
    newTags[LINKTAG_PUBTIME] = calendar.timegm(entry.published_parsed);
  else:
    newTags[LINKTAG_PUBTIME] = int(time.time())

  newTags[LINKTAG_ISPROCESSED] = 'false'
  return newTags


def _linkFromFeedEntry(jobId, entry, feed):
  """
  Creates a link from a feed entry and feed objects.
  """

  # Propogate tags from feed to link object
  linkTags = dict(feed.tags)
  _deleteUnecessaryFeedTags(linkTags)

  # Add new tags retrieved from the feed entry
  linkTags.update(_retrieveNewTagsFromFeedEntry(jobId, entry))

  try:
    # Return the final link object
    return Link(entry.link, linkTags)
  except Exception as e:
    logger.info("Could not open link %s. Job id: %s", entry.link, jobId)
    return None;

def processRssFeed(jobId, feed):
  """
  Processes a rss feed (takes as input the feed)
  """

  feedAndJobId = "Feed id: " + feed.id + ". Job id: " + jobId;

  # compute the last pubDate
  lastPubDate = 0;
  if FEEDTAG_LASTPUBDATE in feed.tags:
      lastPubDate = feed.tags[FEEDTAG_LASTPUBDATE]

  # get all feed entries since last poll time
  parsedFeed = feedparser.parse(feed.tags[FEEDTAG_URL])
  newEntries = [entry for entry in parsedFeed.entries
                if (not entry.published_parsed) or (entry.published_parsed > time.gmtime(lastPubDate))]
  logger.info("Got %i new entries. %s", len(newEntries), feedAndJobId)

  # for each entry add link in link database and a process link job
  linksToAdd = []
  for entry in newEntries:
    link = _linkFromFeedEntry(jobId, entry, feed)
    if link:
      linksToAdd.append(link);
  latestPubTime = _putNewLinks(feedAndJobId, linksToAdd)

  # last step update the feed on successful completion of poll
  if latestPubTime > 0:
    feed.tags[FEEDTAG_LASTPUBDATE] = latestPubTime

  feedManager = FeedManager()
  feedManager.updateFeedOnSuccessfullPoll(feed)
  logger.info(
    "Feed updated after being successfully processed. %s.",
    feedAndJobId)

  logger.info("Completed processing rss feed. %s.", feedAndJobId)

def _linkFromWebPageEntry(jobId, entry, feed, entrySelector):
  """
  Creates a link from a web page entry.
  """

  # Propogate tags from feed to link object
  linkTags = dict(feed.tags)
  _deleteUnecessaryFeedTags(linkTags)

  # Try and extract the title. If unsuccessful, just return None.
  extractTitleResult = hp.extractLink(
    jobId,
    entry,
    entrySelector['title'],
    feed.tags[FEEDTAG_URL])
  if not extractTitleResult:
    return None;
  link = extractTitleResult[0];
  linkTags[LINKTAG_TITLE] = extractTitleResult[1];

  if 'titleText' in entrySelector:
    logger.info("titleText selector specified. Using it. %s", jobId)
    linkTags[LINKTAG_TITLE] = hp.extractText(
      jobId,
      entry,
      entrySelector['titleText'],
      None)
    if not linkTags[LINKTAG_TITLE]:
      return None;

  # add summary and image tags
  processingResult = hp.processHtml(
      jobId,
      entry,
      entrySelector['summary'],
      entrySelector['image'],
      feed.tags[FEEDTAG_URL]);
  linkTags[LINKTAG_SUMMARY] = entry;
  linkTags[LINKTAG_SUMMARYTEXT] = processingResult[0];
  linkTags[LINKTAG_SUMMARYIMAGES] = processingResult[1];

  linkTags[LINKTAG_PUBTIME] = int(time.time())
  linkTags[LINKTAG_ISPROCESSED] = 'false'

  try:
    # Return the final link object
    return Link(link, linkTags)
  except Exception as e:
    logger.info("Could not open link %s. Job id: %s", link, jobId)
    return None;

def processWebFeed(jobId, feed):
  feedAndJobId = "Feed id: " + feed.id + ". Job id: " + jobId;

  # get page html
  pageHtml = "";
  if FEEDTAG_IS_FEEDPAGE_STATIC in feed.tags:
    pageHtml = getHtmlStatic(feed.tags[FEEDTAG_URL])
  else:
    pageHtml = loadPageAndGetHtml(feed.tags[FEEDTAG_URL])
  logger.info("Got html for web page. %s.", feedAndJobId)

  # load entry selectors
  entrySelectors = json.loads(feed.tags[FEEDTAG_ENTRY_SELECTORS])
  logger.info(
    "Will use %i entry selectors. %s",
    len(entrySelectors),
    feedAndJobId)

  # Use entry selector to get entries
  linksToAdd = []
  for entrySelector in entrySelectors:
    entries = hp.getSubHtmlEntries(jobId, pageHtml, entrySelector['overall'])
    logger.info(
      "Got %i entries for entry selector %s. %s",
      len(entries),
      entrySelector['overall'],
      feedAndJobId)

    # considering only the top 30 entries to reduce load
    for entry in entries[:30]:
      link = _linkFromWebPageEntry(jobId, entry, feed, entrySelector)
      if link:
        linksToAdd.append(link);
        logger.info("Discovered link: %s. %s", link.id, feedAndJobId)

  if len(linksToAdd) == 0:
    logger.warning("No links found while processing webPage. %s", feedAndJobId)
  else:
    logger.info("Number of links found: %i. %s", len(linksToAdd), feedAndJobId)

  # put links and processLink jobs
  latestPubTime = _putNewLinks(feedAndJobId, linksToAdd)
  if latestPubTime > 0:
    feed.tags[FEEDTAG_LASTPUBDATE] = latestPubTime

  # update Feed on successfull poll
  feedManager = FeedManager()
  feedManager.updateFeedOnSuccessfullPoll(feed)
  logger.info(
    "Feed updated after being successfully processed. %s.",
    feedAndJobId)

  logger.info("Completed processing webPage feed. %s.", feedAndJobId)

def processFeed(jobId, feedId):
  feedAndJobId = "Feed id: " + feedId + ". Job id: " + jobId;
  logger.info("Started processing rss feed. %s.", feedAndJobId)

  # get the feed
  feedManager = FeedManager()
  feed = feedManager.get(feedId)
  logger.info("Got feed from database. %s.", feedAndJobId)

  if feed.tags[FEEDTAG_TYPE] == FEEDTYPE_RSS:
    processRssFeed(jobId, feed)
  elif feed.tags[FEEDTAG_TYPE] == FEEDTYPE_WEBPAGE:
    processWebFeed(jobId, feed)
