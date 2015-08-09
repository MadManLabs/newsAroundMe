#background worker to do jobs

import time

from constants import *
from loggingHelper import *
from jobManager import JobManager
from workerJob import WorkerJob
from rssProcessor import *
from linkProcessor import *
import clusteringJobs as cj

def RunJob(job):
    "Run a job taking care of error handling."

    try:
        if job.jobName == JOB_PROCESSFEED:
            processFeed(job.jobId, job.jobParams[JOBARG_PROCESSFEED_FEEDID])
        if job.jobName == JOB_PROCESSLINK:
            processLink(job.jobId, job.jobParams[JOBARG_PROCESSLINK_LINKID])
        if job.jobName == JOB_PARSEDOC:
            cj.parseDoc(job.jobId, job.jobParams[JOBARG_PARSEDOC_DOCID])
    except:
        logging.exception('')

def DequeueAndExecuteJob():
    """
    Dequeue a job from the queue and start executing it.
    """

    logging.info("Dequeing a job.");
    jobManager = JobManager()
    job = jobManager.dequeueJob()

    if job is None:
        logging.info("No job found. Sleeping for 30 seconds")
        time.sleep(30)
        return

    logging.info(
        "Job found. Starting it now." + \
        "Job id: %s. Job Name: %s. Job Params: %s.",
        job.jobId,
        job.jobName,
        str(job.jobParams))
    RunJob(job)

# keep looping over jobs and executing them
if __name__ == '__main__':
    InitLogging()
    while (True):
        DequeueAndExecuteJob()
