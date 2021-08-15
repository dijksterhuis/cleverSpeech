#!/usr/bin/env bash


if [[ $# -eq 0 ]]
then
    cmd="/bin/bash"
else
    cmd="${@}"
fi

if [[ -z ${LOCAL_UID} && -z ${LOCAL_GID} ]]
then
    echo ""
else
    echo "Chowning files... This may take a while."
    if [[ -z $(getent group ${LOCAL_GID}) ]]
    then
        groupadd -g ${LOCAL_GID} local
    fi
    usermod -u ${LOCAL_UID} -g ${LOCAL_GID} cleverspeech
    chown -R ${LOCAL_UID}:${LOCAL_GID} /home/cleverspeech/
fi

exec sudo -E -H -u cleverspeech ${cmd}

