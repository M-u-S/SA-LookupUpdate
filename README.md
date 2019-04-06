**`SA-LookupUpdate`**

This SA provides a custom search command which updates lookup file from the
staging directory `$SPLUNK_HOME/var/run/splunk/lookup_tmp`. The new lookup file
MUST follow this naming convention:

**`<appname>_<lookupfilename.csv>`**

**Install:**

Install as usual in the Splunk web or copy into $SPLUNK_HOME/etc/apps

**Configure:**

Nothing to see here, move along.

**Debug**

Debug option can be enabled in the script handler `LoookupUpdate.py` by
changing  `myDebug = no` to `myDebug = yes`.

**Support**

This is an open source project, no support provided, but you can ask questions
on answers.splunk.com and I will most likely answer it.
Github repository: https://github.com/M-u-S/SA-LookupUpdate

I validate all my apps with appinspect and the log can be found in the README
folder of each app.

Running Splunk on Windows? Good Luck, not my problem.


**Version**

`5. April 2019 : 0.0.1 / Initial`  
