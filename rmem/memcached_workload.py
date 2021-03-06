
def set_memcached_size(size_gb):
  record = int(size_gb * 1024 * 1024 * 1024 / 10240)
  workload = '''
db=com.yahoo.ycsb.db.SpymemcachedClient
memcached.address=/root/spark-ec2/slaves
memcached.port=11211


histogram.buckets=20
exportfile=results.txt
recordcount=%d
operationcount=%d
workload=com.yahoo.ycsb.workloads.MemcachedCoreWorkload

readallfields=true

insertproportion=0
readproportion=0.95
updateproportion=0
scanproportion=0

memgetproportion=0.100
memupdateproportion=0.0
valuelength=10240

workingset=%d
churndelta=%d

printstatsinterval=5

requestdistribution=zipfian

threadcount=8
target=1000000
''' % (record, 5*record, int(record), int(record))
  f = open("/root/disaggregation/apps/memcached/workloads/running","w")
  f.write(workload)
  f.close()
  
