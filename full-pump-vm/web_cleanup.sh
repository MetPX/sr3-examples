# remove all files >30 minutes old.  this is for very small systems without much online disk.
# for bigger systems, one can use retention strategy based on the daily directory
find /var/www/html -type f -mmin +30  | grep -v /var/www/html/index.html | xargs rm -f
