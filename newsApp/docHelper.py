import json
import logging

from constants import *
import textHelperNltk as th

logger = logging.getLogger('docHelper')

def getDocEnglishTitle(doc):
  docLang = doc.tags[FEEDTAG_LANG]

  if docLang != LANG_ENGLISH:
    return doc.tags[DOCTAG_TRANSLATED_TITLE]
  else:
    return doc.tags[LINKTAG_TITLE]

def getDocEnglishSummaryText(doc):
  docLang = doc.tags[FEEDTAG_LANG]

  if docLang != LANG_ENGLISH:
    return doc.tags[DOCTAG_TRANSLATED_SUMMARYTEXT]
  else:
    return doc.tags[LINKTAG_SUMMARYTEXT]

def getDocEnglishContent(doc):
  docLang = doc.tags[FEEDTAG_LANG]

  if docLang != LANG_ENGLISH:
    return doc.tags[DOCTAG_TRANSLATED_CONTENT]
  else:
    return doc.content

def computeEnglishDocsSimScore(doc1, doc2):
    doc1EntityWeights = json.loads(doc1.tags.get(DOCTAG_ENTITY_WEIGHTS, "{}"))
    doc2EntityWeights = json.loads(doc2.tags.get(DOCTAG_ENTITY_WEIGHTS, "{}"))

    titleSim = th.compareTitles(
        getDocEnglishTitle(doc1),
        getDocEnglishTitle(doc2))

    titleSimEntities = th.compareTextEntities(
        getDocEnglishTitle(doc1),
        getDocEnglishTitle(doc2),
        doc1EntityWeights,
        doc2EntityWeights)

    summarySim = th.compareUsingShingles(
        getDocEnglishSummaryText(doc1),
        getDocEnglishSummaryText(doc2))

    contentSim = th.compareUsingShingles(
        getDocEnglishContent(doc1),
        getDocEnglishContent(doc2))

    return titleSim*0.1 \
           + titleSimEntities*0.15 \
           + summarySim*0.3 \
           + contentSim*0.45

def computeDocSimScoreUsingEntities(doc1, doc2):
    doc1EntityWeights = json.loads(doc1.tags.get(DOCTAG_ENTITY_WEIGHTS, "{}"))
    doc2EntityWeights = json.loads(doc2.tags.get(DOCTAG_ENTITY_WEIGHTS, "{}"))

    titleSim = th.compareTitles(
        getDocEnglishTitle(doc1),
        getDocEnglishTitle(doc2))

    titleSimEntities = th.compareTextEntities(
        getDocEnglishTitle(doc1),
        getDocEnglishTitle(doc2),
        doc1EntityWeights,
        doc2EntityWeights)

    summarySim = th.compareTextEntities(
        getDocEnglishSummaryText(doc1),
        getDocEnglishSummaryText(doc2),
        doc1EntityWeights,
        doc2EntityWeights)

    contentSim = th.compareTextEntities(
        getDocEnglishContent(doc1),
        getDocEnglishContent(doc2),
        doc1EntityWeights,
        doc2EntityWeights)

    score = titleSim*0.2 \
           + titleSimEntities*0.4 \
           + summarySim*0.2 \
           + contentSim*0.2

    if score > 0.5:
        score = min(score * 1.4, 1.0)

    return score

def getDocComparisionScore(jobInfo, doc1, doc2):
    score = 0
    if (doc1.tags[FEEDTAG_LANG] == LANG_ENGLISH) and \
        (doc2.tags[FEEDTAG_LANG] == LANG_ENGLISH):
        score = computeEnglishDocsSimScore(doc1, doc2)
        logger.info("Comparing using shingles. %s", jobInfo)
    else:
        score = computeDocSimScoreUsingEntities(doc1, doc2)
        logger.info("Comparing using entities. %s", jobInfo)

    if FEEDTAG_LOCALE in doc1.tags and FEEDTAG_LOCALE in doc2.tags and \
        doc1.tags[FEEDTAG_LOCALE] != doc2.tags[FEEDTAG_LOCALE]:

        logger.info(
            "The two docs are from different locations. Adding penalty. %s",
            jobInfo)
        score = score - 0.4
        if score < 0:
            score = 0
    logger.info("Comparision score: %s. %s", str(score), jobInfo)
    return score