#!/usr/bin/env bash


if [[ $# -eq 0 ]]
then
    cmd="/bin/bash"
else
    cmd="${@}"
fi

if [[ -z ${LOCAL_UID} || -z ${LOCAL_GID} ]]
then
    echo """-----------------------------------------------------------
===> WARNING: USING 'docker run --user' WILL BREAK THINGS!
-----------------------------------------------------------

If you want to map your user and group ids into the container you **must** use:
'docker run ... -e LOCAL_UID=<your_user_id> -e LOCAL_GID=<your_group_id> ... '

I'm going to assume you are running tests (or just fiddling) and use the base image UID and GID.
"""
    echo "Using UID=${USER_ID} GID=${GROUP_ID}."
else
    echo "Using UID=${LOCAL_UID} GID=${LOCAL_GID}"
    echo "Propagate changes will take a few minutes..."

    if [[ -z $(getent group ${LOCAL_GID}) ]]
    then
        groupadd -g ${LOCAL_GID} local
    fi
    
    usermod -u ${LOCAL_UID} -g ${LOCAL_GID} cleverspeech
    chown -R ${LOCAL_UID}:${LOCAL_GID} /home/cleverspeech/
    echo "Modified. Entering container."
fi

export PYTHONPATH="${PYTHONPATH}:/home/cleverspeech/cleverSpeech"

exec sudo -E -H -u cleverspeech PYTHONPATH=${PYTHONPATH} ${cmd}

