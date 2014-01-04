#!/bin/bash

if [ "$(hostname -s)" == "amandine" ]; then
    cd $(dirname $0)
    git reset --hard HEAD
    pkill -f irc3
else
    git push amandine master
    ssh amandine ~/apps/irc3/update.sh
fi

