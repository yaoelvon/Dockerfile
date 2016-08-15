#!/bin/sh -e

EP=/opt/etherpad

random_key() {
    dd if=/dev/urandom bs=64 count=1 2>/dev/null|sha256sum|cut -d' ' -f1|tr -d '\n'
}

if [ "$EP/bin/run.sh" = "$1" ]; then
    [ -r $EP/APIKEY.txt ] || random_key > $EP/APIKEY.txt
    [ -r $EP/SESSIONKEY.txt ] || random_key > $EP/SESSIONKEY.txt
    touch $EP/node_modules/ep_etherpad-lite/.ep_initialized
    chown -R etherpad:etherpad $EP/settings.json $EP/var
    exec su-exec etherpad "$@"
fi

exec "$@"
