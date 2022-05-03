#!/bin/bash

/start.sh &
tail -Fq /var/log/gianturl.log