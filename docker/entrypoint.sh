#!/usr/bin/env bash


if [[ $# -eq 0 ]]
then
    cmd="/bin/bash"
else
    cmd="${@}"
fi

if [[ -z ${LOCAL_UID} || -z ${LOCAL_GID} ]]
then
    echo "You *must* provide the LOCAL_UID and LOCAL_GID environment variables."
    echo "Quitting."
    exit
else
    echo "Modifying container to match UID=${LOCAL_UID} GID=${LOCAL_GID}"
    echo "This will take a moment."

    if [[ -z $(getent group ${LOCAL_GID}) ]]
    then
        groupadd -g ${LOCAL_GID} local
    fi
    
    usermod -u ${LOCAL_UID} -g ${LOCAL_GID} cleverspeech
    chown -R ${LOCAL_UID}:${LOCAL_GID} /home/cleverspeech
    chown -R ${LOCAL_UID}:${LOCAL_GID} /data/
    echo "Modified. Entering container."

    exec sudo -E -H -u cleverspeech PYTHONPATH=${PYTHONPATH}:${BASE_DIR}/cleverSpeech ${cmd}
fi
