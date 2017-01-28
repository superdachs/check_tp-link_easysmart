# check_tp-link_easysmart
Monitoring plugin for checking semi managed tp-link switches
tested with TP-LINK TLSG108E

# usage
* -H --hostaddress - ip or hostname of the switch
* -U --username - username of admin
* -P --password - password of admin
* -M --mode - check mode (overview or errors)
  overview: displays overall count of given ports for send and receive counters, uses no thresholds
  errors: displays counts for given ports since the last check, uses thresholds
* -p --ports - comma separated list of ports or all
* -w --warning - warning threshold (number)
* -c --critical - critical threshold (number)
* --html - adds <\br> tags for web after lines in output (not in perfdata)

# example
```bash
check_tp-link_easysmart.py -H $HOSTADDRESS$ -U $ARG1$ -P $ARG2$ -M errors -p 1,3,5 -w 10 -c 15 --html
```
```bash
check_tp-link_easysmart.py -H $HOSTADDRESS$ -U $ARG1$ -P $ARG2$ -M errors -w 10 -c 15 --html
```
This checks the error counts for send and receive since last check. Returns warning for > 10 errors (tx or rx) and critical for 15 errors (tx or rx).

