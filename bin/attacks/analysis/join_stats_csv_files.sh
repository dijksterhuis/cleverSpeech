#!/usr/bin/env bash


EXPERIMENTS_BASE_DIR=${1}

function get_all_stats_files () {
    find ${1} -type f -name "stats.csv"
}

head -n 1  $(get_all_stats_files ${EXPERIMENTS_BASE_DIR} | head -n 1) > compiled_stats.csv
find ${EXPERIMENTS_BASE_DIR} -type f -name "stats.csv" -exec tail -n+2 {} \; >> compiled_stats.csv