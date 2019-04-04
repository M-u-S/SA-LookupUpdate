**`SA-LookupUpdate`**

This TA provides an REST API endpoint that can be used to add or remove
(your Load Balancer must support something like this!) SHC member from the
load balancer group.

The REST endpoint is:

https://<hostname>:8089/services/loadbalancer

The endpoint handler is configured to report either `IN` if the SH should be
used or `OUT` if the load balancer should NOT use it.

The endpoint does not need authentication.

**Install:**

Install as usual in the Splunk web or copy into $SPLUNK_HOME/etc/apps

**Configure:**

The TA provides a saved search to populate the lookup with the names of the SH's.
This saved search is disabled by default.

**Debug**

Debug option can be enabled in the script handler `LoadBalancerStatus.py` by
changing  `myDebug = no` to `myDebug = yes`.

**Support**

This is an open source project, no support provided, but you can ask questions
on answers.splunk.com and I will most likely answer it.
Github repository: https://github.com/M-u-S/SA-LoadBalancerStatus

I validate all my apps with appinspect and the log can be found in the README
folder of each app.

Running Splunk on Windows? Good Luck, not my problem.


**Version**

`13. February 2019 : 0.0.1 / Initial`  
`14. February 2019 : 0.0.2 / Clean up`  
