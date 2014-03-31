#!/bin/bash
################################################################################
#
# usage:
################################################################################

RENAVLIST=$1
BASEDIR="/media/data/CATAMI_SITE/media/"
SCRIPTDIR=`dirname "$(readlink -f "$0")"` # location of this script
RENAV2WEB=$SCRIPTDIR"/renav2web.py"
#RENAV2WEB="/home/auv/Code/catami/scripts/renav2web.py"

####################################################
# Read list of dives and link/prepare for web
####################################################
while read renav; do
  divedir=`dirname $renav`
  dive=`basename $divedir`
  imgs=`ls -d $divedir/i*_cv`
  #imgs=`ls -d $divedir/i*_gw`

  # make directory, import data
  echo "    Preparing $dive..."
  mkdir $dive
  cd $dive
  $RENAV2WEB --link-images $renav $imgs
  cd ../
done < $RENAVLIST

echo "Done!"

