#!/bin/bash
## g.e. # ./BoM_AWAP.bash 20080101-20120101 BoM/AWAP
if test $1 = '-h'; then
  echo "**************************"
  echo "*** Script to download ***"
  echo "***    BoM AWAP data   ***"
  echo "**************************"
  echo "BoM_AWAP.bash [period]([YYYYMMDDi]-[YYYYMMDDe]) [ofold](output fold)"
else
  rootsh=`pwd`
  period=$1
  ofold=$2

  datei=`echo ${period} | tr '-' ' ' | awk '{print $1}'`
  datee=`echo ${period} | tr '-' ' ' | awk '{print $2}'`

  date=${datei}
  cd ${rootsh}/${ofold}
  while test ! ${date} == ${datee}; do
    wget http://www.bom.gov.au/web03/ncc/www/awap/rainfall/totals/daily/grid/0.05/history/nat/${date}${date}.grid.Z
    date=`date +%Y%m%d -d"${date} 1 day"`
    echo ${date}
  done # end of dates

fi
