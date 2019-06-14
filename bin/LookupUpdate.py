#!/usr/bin/env python2.7
# Copyright (C) 2019 MuS
# http://answers.splunk.com/users/2122/mus
#

# enable / disable logger debug output
myDebug='no'

# import only basic modules and do some stuff before we start
import splunk
import splunk.rest as rest
import sys
import os
import logging
import logging.handlers
import splunk.Intersplunk
import datetime
import getopt
from ast import literal_eval
from os import path
from sys import modules, path as sys_path, stderr
from datetime import datetime
from ConfigParser import SafeConfigParser
from optparse import OptionParser

""" get SPLUNK_HOME form OS """
SPLUNK_HOME = os.environ['SPLUNK_HOME']

""" get myScript name and path """
myScript = os.path.basename(__file__)
myPath = os.path.dirname(os.path.realpath(__file__))

# define the logger to write into log file
def setup_logging(n):
    logger = logging.getLogger(n)
    if myDebug == 'yes':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = '%s.log' % myScript
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = '%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s'
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger

# start the logger for troubleshooting
logger = setup_logging( 'Logger started ...' ) # logger

# or get user provided options in Splunk as keyword, option
try: # lets do it
    logger.info( 'getting Splunk options...' ) # logger
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions() # get key value pairs from user search
    app = options.get('app','foo') # get user option or use a default value
    filename = options.get('filename','baz') # get user option or use a default value
    if 'foo' in app:
        logger.info( 'no options provided ...' ) # logger
        splunk.Intersplunk.generateErrorResults(': no options provided, please add \'app=<appName> filename=<lookupfile.csv>\'  ...')
        sys.exit() # exit on error

    logger.info( 'got options %s %s ...' % (app, filename)) # logger

except Exception ,e:
    logger.info( 'error getting options ...' ) # logger
    splunk.Intersplunk.generateErrorResults(': error getting options ...')
    sys.exit() # exit on error

try: # lets do it
    logger.info( 'starting main ...' ) # logger
    results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    logger.info( 'getting session ...' ) # logger
    sessionKey = settings.get('sessionKey', None)
    logger.info( 'got session ...' ) # logger

except Exception ,e:
    logger.info( 'failed to get sessionKey ...' ) # logger
    splunk.Intersplunk.generateErrorResults(': failed to get sessionKey ...')
    sys.exit() # exit on error

try:
    logger.info( 'setting up post command ...' ) # logger
    post_path = '/servicesNS/nobody/%s/data/lookup-table-files' % app
    logger.info( 'setting up %s ...' % post_path) # logger
    postArgs = {}
    logger.info( 'setting up dict %s ...' % postArgs) # logger
    postApp = '%s/var/run/splunk/lookup_tmp/%s_%s' % (SPLUNK_HOME, app, filename)
    logger.info( 'setting up postApp %s ...' % postApp ) # logger
    postFile = '%s' % filename
    logger.info( 'setting up postFile %s ...' % postFile) # logger
    postArgs = {'eai:data': postApp , 'name': postFile}
    logger.info( 'adding to dict %s ...' % postArgs) # logger

except Exception ,e:
    logger.info( 'error in setting up post command ...' ) # logger
    splunk.Intersplunk.generateErrorResults(': error in setting up post command ...')
    sys.exit() # exit on error

logger.info( 'check if the lookup file is in the staging directory ...' ) # logger
exists = os.path.isfile(postApp)
if exists:
    logger.info( 'lookup file is in the staging directory ...' ) # logger
    try:
        logger.info( 'first we have to remove the old lookup file ...' ) # logger
        oldFile = '%s/etc/apps/%s/lookups/%s' % (SPLUNK_HOME, app, filename)
        old_f = os.path.isfile(oldFile)
        if old_f:
            logger.info( 'will delete old file %s ...' % oldFile) # logger
            os.remove(oldFile)
            logger.info( 'file deleted ...') # logger

    except Exception, e:
        logger.info( 'error deleting old file ...' ) # logger
        splunk.Intersplunk.generateErrorResults(': error deleting old file ...')
        sys.exit() # exit on error

else:
    logger.info( 'lookup file is NOT the staging directory ...' ) # logger
    splunk.Intersplunk.generateErrorResults(': lookup file is NOT the staging directory')
    sys.exit() # exit on error

try:
    logger.info( 'starting post ...' ) # logger
    response, content = rest.simpleRequest(post_path, sessionKey=sessionKey, postargs=postArgs, method='POST', raiseAllErrors=True)
    logger.info( 'post done ...' ) # logger
    t1 = datetime.now();
    logger.info( 'got time ...' ) # logger
    log_result = 'time=\"%s\", app=\"%s\", filename=\"%s\", message=\"Updated lookup file\"' % (t1, app, postFile)
    logger.setLevel(logging.DEBUG)
    logger.info(log_result)
    logger.setLevel(logging.ERROR)
    results = []
    result = {}
    logger.info( 'setup results & result...' ) # logger
    result['_time'] = t1
    result['app'] = '%s' % (app)
    result['filename'] = '%s' % (postFile)
    result['message'] = 'Updated lookup file'
    results.append(result)
    splunk.Intersplunk.outputResults(results)

except Exception, e:
    #logger.info( 'error during update ...' ) # logger
    t1 = datetime.now();
    log_error = 'time=\"%s\", app=\"%s\", filename=\"%s\", message=\"Error during update\"' % (t1, app, postFile)
    logger.error(log_error)
    splunk.Intersplunk.generateErrorResults(': error during update ...')
