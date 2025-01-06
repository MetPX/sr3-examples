

PRIMARY_DIR=/tmp/source
COPY_DIR=/tmp/destination

echo "Comparing contents of ${PRIMARY_DIR} and ${COPY_DIR}"

echo "running audit..."
find $PRIMARY_DIR -type f -print | sort | awk ' { print "\""$0"\""; }' | xargs md5sum | sed "s+${PRIMARY_DIR}++" >source_files_md5.txt &

find $COPY_DIR -type f -print | sort | awk ' { print "\""$0"\""; }' | xargs md5sum | sed "s+${COPY_DIR}++"  >copy_files_md5.txt &

find $PRIMARY_DIR -type l -print | sort | awk ' { print "\""$0"\""; }' | xargs ls -d |  sed "s+${PRIMARY_DIR}++" >source_link_content.txt &

find $COPY_DIR -type l -print | sort | awk ' { print "\""$0"\""; }' | xargs ls -d | sed "s+${COPY_DIR}++"  >copy_link_content.txt &


wait
echo "audit complete."

file_diff_count="`diff source_files_md5.txt copy_files_md5.txt | wc -l`"
echo "${file_diff_count} Differences between files in source and desination"

if [ "${file_diff_count}" -gt 0 ]; then
	diff source_files_md5.txt copy_files_md5.txt
fi
rm source_files_md5.txt copy_files_md5.txt

link_diff_count="`diff source_link_content.txt copy_link_content.txt | wc -l`"
echo "${link_diff_count} Differences between links in source and desination"

if [ "${link_diff_count}" -gt 0 ]; then
	diff source_link_content.txt copy_link_content.txt
fi
rm source_link_content.txt copy_link_content.txt
