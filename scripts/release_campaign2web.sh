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
BASEDIR="/media/data/CATAMI_SITE/media/"
SCRIPTDIR="$(readlink -f "$0")" # location of this script
RENAV2WEB=$SCRIPTDIR"/renav2web.py"


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
while read renav; do
  divedir=`dirname $renav`
  dive=`basename $divedir`
  imgs=`ls -d $divedir/i*_cv`

  # make directory, import data
  echo "    Preparing $dive..."
  mkdir $dive
  cd $dive
  $RENAV2WEB --link-images $renav $imgs
  cd ../
done < $RENAVLIST

echo "Done!"
