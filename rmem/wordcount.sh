free > /dev/null && sync && echo 3 > /proc/sys/vm/drop_caches && free > /dev/null
rm -rf /root/hadoop-2.5.1/output
/root/hadoop-2.5.1/bin/hadoop jar /root/hadoop-2.5.1/test/wc.jar WordCount /root/data/wordcount/f$1.txt /root/hadoop-2.5.1/output/
#bin/hdfs dfs -rm -r /user/root/output
#bin/hadoop jar test/wc.jar WordCount 24h.txt output
