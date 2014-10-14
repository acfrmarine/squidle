#!/bin/bash
################################################################################
# Put paths to renavs in deployments contained in release 
# campaign dir "CMPDIR" and prepare each deployment for web
#
# usage:
#       ./campaign2web.sh CMPDIR
################################################################################

CMPDIRSRC=$1

RENAVLIST="renavlist.txt"
BASEDIR="/media/water/SQUIDLE_DATA/media/"
SCRIPTDIR=`dirname "$(readlink -f "$0")"` # location of this script
CAMPAIGN2WEB=$SCRIPTDIR"/campaign2web.sh"



####################################################
# Create and cd to campaign web directory
####################################################
CMPDIR=$BASEDIR/`basename $CMPDIRSRC`
echo $CMPDIR
mkdir $CMPDIR
cd $CMPDIR

ls ${CMPDIRSRC}/r*/renav*/stereo_pose_est.data | xargs -I {} dirname {} > $RENAVLIST

read -p "Would you like to prepare the dives?\nYou will be required to verify the list of renavs in vim... (y/n) " -n 1
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # open list in order to double check that it is ok before importing.
    vim $RENAVLIST

    # Read list of dives and link/prepare for web
    $CAMPAIGN2WEB $RENAVLIST
fi


