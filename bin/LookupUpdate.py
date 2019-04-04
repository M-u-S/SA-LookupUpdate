# enable / disable logger debug output
#myDebug='no' # debug disabled
myDebug='yes' # debug enabled

# import only basic modules and do some stuff before we start
import splunk
import splunk.rest as rest
import sys
import os
import logging
import logging.handlers
import splunk.Intersplunk
#import datetime
import getopt
#import csv
#import re
#import collections
#import base64
#import inspect
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
if myDebug == 'yes': logger = setup_logging( 'Logger started ...' ) # logger

# or get user provided options in Splunk as keyword, option
try: # lets do it
    if myDebug == 'yes': logger.info( 'getting Splunk options...' ) # logger
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions() # get key value pairs from user search
    app = options.get('app',None) # get user option or use a default value
    filename = options.get('filename',None) # get user option or use a default value
    if myDebug == 'yes': logger.info( 'got options %s %s ...' % (app, filename)) # logger

except: # get error back
    if myDebug == 'yes': logger.info( 'INFO: no option provided using [default]!' ) # logger

try:
    if myDebug == 'yes': logger.info( 'starting main ...' ) # logger
    # getting the sessionKey, owner, namespace
    results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    if myDebug == 'yes': logger.info( 'getting session ...' ) # logger
    sessionKey = settings.get('sessionKey', None)
    if myDebug == 'yes': logger.info( 'got session ...' ) # logger
    try:
        if myDebug == 'yes': logger.info( 'first we have to remove the old lookup file ...' ) # logger
        oldFile = '/opt/splunk/etc/apps/%s/lookups/%s' % (app, filename)
        if myDebug == 'yes': logger.info( 'will delete old file %s ...' % oldFile) # logger
        os.remove(oldFile)
        if myDebug == 'yes': logger.info( 'file deleted ...') # logger
        
    except Exception, e:
        if myDebug == 'yes': logger.info( 'error deleting old file ...' ) # logger
 
    try:
        if myDebug == 'yes': logger.info( 'setting up post command ...' ) # logger
        post_path = '/servicesNS/nobody/%s/data/lookup-table-files' % app
        if myDebug == 'yes': logger.info( 'setting up %s ...' % post_path) # logger
        postArgs = {}
        if myDebug == 'yes': logger.info( 'setting up dict %s ...' % postArgs) # logger
        postApp = '/opt/splunk/var/run/splunk/lookup_tmp/%s_%s' % (app, filename)
        if myDebug == 'yes': logger.info( 'setting up postApp %s ...' % postApp ) # logger
        postFile = '%s' % filename
        if myDebug == 'yes': logger.info( 'setting up postFile %s ...' % postFile) # logger
        postArgs = {'eai:data': postApp , 'name': postFile}
        #postArgs = literal_eval(postArgs)
        if myDebug == 'yes': logger.info( 'adding to dict %s ...' % postArgs) # logger

    except Exception ,e:
        if myDebug == 'yes': logger.info( 'error in setting up post command ...' ) # logger

    if myDebug == 'yes': logger.info( 'starting post ...' ) # logger
    response, content = rest.simpleRequest(post_path, sessionKey=sessionKey, postargs=postArgs, method='POST', raiseAllErrors=True)
    #response, content = rest.simpleRequest(post_path, sessionKey=sessionKey, postargs=postArgs, method='POST', raiseAllErrors=True) % (app, filename, filename)
    #response, content = rest.simpleRequest(post_path, sessionKey=sessionKey, postargs={'eai:data': postApp , 'name': postFile }, method='POST', raiseAllErrors=True) % (app, filename, filename)
    if myDebug == 'yes': logger.info( 'done update of %s ...' % postFile) # logger
    splunk.Intersplunk.generateErrorResults(': done update of %s !' % postFile) # print the error into Splunk UI
 

except: # get error back
    logger.error( 'ERROR: update failed!' ) # logger
    splunk.Intersplunk.generateErrorResults(': update failed!') # print the error into Splunk UI
    sys.exit() # exit on error
 
