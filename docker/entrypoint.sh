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
    echo "Modifying container for UID=${LOCAL_UID} and GID=${LOCAL_GID}"
    echo "=> chown-ing files..."
    N_CPUS=$(cat /proc/cpuinfo | grep -c processor)

    find /home/cleverspeech \
      -path "*/native_client/*" -prune -o \
      -path "*/modules/*" -prune -o  \
      -print \
    | parallel -j $((${N_CPUS} * 8)) \
      chown --changes ${LOCAL_UID}:${LOCAL_GID} ::: >> /chown.log 2>&1

    echo "==> switching user and group..."

    if [[ -z $(getent group ${LOCAL_GID}) ]]
    then
        groupadd -g ${LOCAL_GID} local
    fi
    usermod -u ${LOCAL_UID} -aG ${LOCAL_GID} cleverspeech

    echo "==> all done."


fi

exec sudo -E -H -u cleverspeech ${cmd}


