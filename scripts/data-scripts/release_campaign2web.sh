#!/bin/bash
################################################################################
# Put paths to renavs in deployments contained in release 
# campaign dir "CMPRELEASEDIR" and prepare each deployment for web
#
# usage:
#       ./campaign2web.sh CMPRELEASEDIR
################################################################################

CMPRELEASEDIR=$1

RENAVLIST="renavlist.txt"
BASEDIR="/media/water/SQUIDLE_DATA/media/"
SCRIPTDIR=`dirname "$(readlink -f "$0")"` # location of this script
CAMPAIGN2WEB=$SCRIPTDIR"/campaign2web.sh"



####################################################
# Create and cd to campaign web directory
####################################################
CMPDIR=$BASEDIR/`basename $CMPRELEASEDIR`
echo $CMPDIR
mkdir $CMPDIR
cd $CMPDIR

echo "Saving list of deployment renavs to: $CMPDIR/$RENAVLIST"
for f in `ls -d $CMPRELEASEDIR/r2*`; do
  l=`readlink "$f/track_files"` # figure out renav location
  echo $(readlink -m "$f/`dirname $l`") >> $RENAVLIST
done

####################################################
# Read list of dives and link/prepare for web
####################################################
$CAMPAIGN2WEB $RENAVLIST
