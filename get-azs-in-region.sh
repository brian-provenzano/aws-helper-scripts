#!/bin/bash -e
#
# This script gets AZs in all regions.  
# If you specify an optional int it will return the regions with at least that number of AZs
#
# Usage:
# get-azs-in-region.sh <num-azs>
#
# Notes:
# Useful for checking for mapping/templating etc and/or adding to automation for dyn checking of AZs in region (and taking some action)
# OR just to run it because it is fun to watch...
#
# Author:
# Hosting - BJP - 1/19
if [[ $# -eq 1 ]] ; then
    echo -e "regions with at least [ $1 ] AZs:\n"
    for region in $(aws ec2 describe-regions | jq -r ".Regions[].RegionName"); do
        NUM_AZS=$(aws ec2 describe-availability-zones --region "${region}" | jq ".[] | length")
        if [[ $NUM_AZS -ge $1 ]]; then
            echo "${region} - number of AZs: ${NUM_AZS}"
        fi
    done
else
    for region in $(aws ec2 describe-regions | jq -r ".Regions[].RegionName"); do
        echo "${region} - number of AZs: "  $(aws ec2 describe-availability-zones --region "${region}" | jq ".[] | length")
    done
fi