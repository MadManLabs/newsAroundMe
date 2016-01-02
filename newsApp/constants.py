# define some constants used across modules.

LANG_ENGLISH = 'en'

# common tag names
TAG_PUBLISHER = 'publisher'
TAG_PUBLISHER_DETAILS = 'publisherDetails'
TAG_IMAGES = 'images'

#doc tags
DOCTAG_URL = 'url'
DOCTAG_TRANSLATED_TITLE = 'translatedTitle'
DOCTAG_TRANSLATED_SUMMARYTEXT = 'translatedSummaryText'
DOCTAG_TRANSLATED_CONTENT = 'translatedContent'

# feed tags
FEEDTAG_TYPE = 'type'
FEEDTAG_NEXTPOLLTIME = 'nextPollTime'
FEEDTAG_POLLFREQUENCY = 'pollFrequency'
FEEDTAG_LASTPOLLTIME = 'lastPollTime'
FEEDTAG_URL = 'feedUrl'
FEEDTAG_LASTPUBDATE = 'lastPubDate'
FEEDTAG_CATEGORY = 'category'
FEEDTAG_COUNTRY = 'country'
FEEDTAG_LANG = 'lang'
FEEDTAG_LOCALE = 'locale'

# link tags
LINKTAG_ISPROCESSED = 'isProcessed'
LINKTAG_DOCKEY = 'docKey'
LINKTAG_SUMMARY = 'summary'
LINKTAG_SUMMARYTEXT = 'summaryText'
LINKTAG_SUMMARYIMAGES = 'summaryImages'
LINKTAG_PUBTIME = 'pubtime'
LINKTAG_TITLE = 'title'

# publisher tags
PUBLISHERTAG_TEXTSELECTOR = 'textSelector'
PUBLISHERTAG_IMAGESELECTORS = 'imageSelectors'
PUBLISHERTAG_HOMEPAGE = 'homepage'
PUBLISHERTAG_NAME = 'name'
PUBLISHERTAG_FRIENDLYID = 'friendlyId'

#job names
JOB_PROCESSFEED = 'processFeed'
JOBARG_PROCESSFEED_FEEDID = 'feedId'
JOB_PROCESSLINK = 'processLink'
JOBARG_PROCESSLINK_LINKID = 'linkId'
JOB_PARSEDOC = 'parseDoc'
JOBARG_PARSEDOC_DOCID = 'docId'
JOB_GETCANDIDATEDOCS = 'getCandidateDocs'
JOBARG_GETCANDIDATEDOCS_DOCID = 'docId'
JOB_COMPAREDOCS = 'compareDocs'
JOBARG_COMPAREDOCS_DOC1ID = 'doc1'
JOBARG_COMPAREDOCS_DOC2ID ='doc2'
JOB_CLUSTERDOCS = 'clusterDocs'
JOB_UPDATEDBTHROUGHPUT = 'updateDbThroughput'
JOB_UPDATEDBTHROUGHPUT_CONNECTIONSTRING = 'connectionString'
JOB_UPDATEDBTHROUGHPUT_READTHOUGHPUT = 'readThroughput'
JOB_UPDATEDBTHROUGHPUT_WRITETHOUGHPUT = 'writeThroughput'
JOB_UPDATEDBTHROUGHPUT_INDEXNAME = 'indexName'
JOB_CLEANUPDOCSHINGLES = 'cleanupDocShingles'
JOBARG_CLEANUPDOCSHINGLES_DOCID = 'docId'
JOB_CLEANUPDOCDISTANCES = 'cleanupDocDistances'
JOBARG_CLEANUPDOCDISTANCES_DOCID = 'docId'
JOB_PROCESSNEWCLUSTER = 'processNewCluster'
JOBARG_PROCESSNEWCLUSTER_CLUSTER = 'cluster'

#clustering job states
CLUSTER_STATE_INITIALIZED = 'initialized'
CLUSTER_STATE_NEW = 'new'
CLUSTER_STATE_STARTED = 'started'
CLUSTER_STATE_COMPLETED = 'completed'

#allowed input parameter values
ALLOWED_LOCALES = ['bangalore']
ALLOWED_CATEGORIES = ['sports', 'business', 'national', 'world']
ALLOWED_COUNTRIES = ['India']
