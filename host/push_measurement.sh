#!/bin/bash

#
# USB Geiger counter
# 2013 Michał Słomkowski
# This code is distributed under the terms of GNU General Public License version 3.0.

# The script takes CPM (counts per minute) value from the device and sends them to cosm.com

# you should declare the full path to geiger-controller binary when running from cron
CPM=`/path/to/geiger-controller/binary/geiger-controller -cpm`
JSON="{ \"version\":\"1.0.0\", \"datastreams\":[ {\"id\":\"CPM\", \"current_value\":\"$CPM\"} ] }"

# feed ID should be visible in your cosm.com feed's page. In order to use it you have to create it first.
FEED_ID=feed_id_goes_here
# key for authenticating transaction. You have to obtain it from your cosm.com profile page.
API_KEY=your_api_key_goes_here

curl --request PUT \
     --data-binary "$JSON" \
     --header "X-ApiKey: $API_KEY" \
     --verbose \
     http://api.cosm.com/v2/feeds/$FEED_ID
