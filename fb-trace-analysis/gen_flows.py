from cluster import *
from lib import *
import random
import math
import sys




class Flow_record:
  count = 0
  write_records_to_file = True
  def __init__(self, time, from_id, to_id, size, rec_type):
    self.id = Flow_record.count
    Flow_record.count += 1
    self.time = time
    self.from_id = from_id
    self.to_id = to_id
    self.size = size
    self.rec_type = rec_type

  def __str__(self):
    return str(self.time) + "," + self.from_id + "," + self.to_id + "," + str(self.size) + "," + self.rec_type

  def to_ns2_str(self):
    return " ".join([str(self.id), str(self.time), "0", str(self.size), "0", "0", self.from_id, self.to_id])

  @classmethod
  def from_str(cls, record):
    entires = record.split(",")
    time = int(entires[0])
    from_id = entires[1]
    to_id = entires[2]
    size=int(entires[3])
    rec_type=entires[4]
    return Flow_record(time, from_id, to_id, size, rec_type)


class FlowContainer:
  def __init__(self):
    self.flows = []
    self.flow_size_count = {}
    self.name_dict = {"file_read":0,
               "file_written":1,
               "Map_file_write":2,
               "Reduce_file_read":3,
               "Map_CPU_Mem_read":4,
               "Map_CPU_Mem_write":5,
               "Reduce_CPU_Mem_read":4,
               "Reduce_CPU_Mem_write":5,
               "hdfs_read_local": 6,
               "hdfs_read_remote":7,
               "hdfs_written_local": 8,
               "hdfs_written_remote1":9,
               "hdfs_written_remote2":9
               }

def gen_flows(u):
  print "gen_flows Version:", 19

  hdfs_block_size_mb = 1
  hdfs_block_size = int(1024*1024*hdfs_block_size_mb)
  mem_page_size = 4096
  percent_local_read = 0.9

  map_read_ratio = (391 * 1024 * 1024) / (4.5 * 1024 * 1024 * 1024)
  map_write_ratio = (430 * 1024 * 1024) / (4.5 * 1024 * 1024 * 1024)

  reduce_read_ratio = (100 * 1024 * 1024) / (2.8 * 1024 * 1024 * 1024)
  reduce_write_ratio = (110 * 1024 * 1024) / (2.8 * 1024 * 1024 * 1024)


  next_percent = 0.01
  count = 0
  container = FlowContainer()
  for job in u.jobs.itervalues():
    for task in job.tasks.itervalues():
      count += 1
      if float(count)/u.total_tasks > next_percent:
        print "Finished", next_percent, "(", count, "/", u.total_tasks, ") Flows added:", len(container.flows)
        next_percent += 0.01

      if len(job.map_tasks) == 0 or len(job.reduce_tasks) == 0:
        if task.file_bytes_read > 0:
          num_of_blocks = task.file_bytes_read/hdfs_block_size + 1
          for i in range(0, num_of_blocks):
	    if i == num_of_blocks -1:
              read_size = task.file_bytes_read%hdfs_block_size
            else:
              read_size = hdfs_block_size   
            record = Flow_record(task.start_time, task.self_id + "_disk", task.self_id + "_mem", read_size, "file_read")
            add_flow(record, container)

        if task.file_bytes_written > 0:
          num_of_blocks = task.file_bytes_written/hdfs_block_size + 1
          for i in range(0, num_of_blocks):
            if i == num_of_blocks-1:
               write_size = task.file_bytes_written%hdfs_block_size
            else:
               write_size = hdfs_block_size    
            record = Flow_record(task.start_time + task.cpu_ms, task.self_id + "_mem", task.self_id + "_disk", hdfs_block_size, "file_written")
            add_flow(record, container)

      else:
        if task.rec_type == "ReduceAttempt" and task.reduce_shuffle_bytes > 0:
          reduce_flow_size = task.reduce_shuffle_bytes / len(job.map_tasks)
          for mapper in job.map_tasks.itervalues():
            storage_node = u.get_rand_server()
            write_record = Flow_record(mapper.start_time + mapper.cpu_ms, mapper.self_id + "_cpu", storage_node + "_mem", reduce_flow_size, "Map_file_write")
            read_record = Flow_record(task.start_time, storage_node + "_mem", task.self_id + "_cpu", reduce_flow_size, "Reduce_file_read")
            add_flow(write_record, container)
            add_flow(read_record, container)


      if task.map_input_bytes > 0:
        cpu_ram_read_blocks = int(task.map_input_bytes * map_read_ratio / mem_page_size)
        cpu_ram_write_blocks = int(task.map_input_bytes * map_write_ratio / mem_page_size)
        for i in range(0, cpu_ram_read_blocks):
          read_record = Flow_record(int(task.start_time + (task.finish_time - task.start_time) * float(i) / cpu_ram_read_blocks),
                                    task.self_id + "_mem",
                                    u.get_rand_server() + "_cpu",
                                    mem_page_size,
                                    "Map_CPU_Mem_read"
                                    )
          add_flow(read_record, container)

        for i in range(0, cpu_ram_write_blocks):
          write_record = Flow_record(int(task.start_time + (task.finish_time - task.start_time) * float(i) / cpu_ram_write_blocks),
                                    u.get_rand_server() + "_cpu",
                                    task.self_id + "_mem",
                                    mem_page_size,
                                    "Map_CPU_Mem_write"
                                    )
          add_flow(write_record, container)


      if task.reduce_shuffle_bytes > 0:
        cpu_ram_read_blocks = int(task.reduce_shuffle_bytes * reduce_read_ratio / mem_page_size)
        cpu_ram_write_blocks = int(task.reduce_shuffle_bytes * reduce_write_ratio / mem_page_size)
        for i in range(0, cpu_ram_read_blocks):
          read_record = Flow_record(int(task.start_time + (task.finish_time - task.start_time) * float(i) / cpu_ram_read_blocks),
                                    task.self_id + "_mem",
                                    u.get_rand_server() + "_cpu",
                                    mem_page_size,
                                    "Reduce_CPU_Mem_read"
                                    )
          add_flow(read_record, container)

        for i in range(0, cpu_ram_write_blocks):
          write_record = Flow_record(int(task.start_time + (task.finish_time - task.start_time) * float(i) / cpu_ram_write_blocks),
                                    u.get_rand_server() + "_cpu",
                                    task.self_id + "_mem",
                                    mem_page_size,
                                    "Reduce_CPU_Mem_write"
                                    )
          add_flow(write_record, container)








      if task.hdfs_bytes_read > 0:
        num_blocks = task.hdfs_bytes_read/hdfs_block_size+1
        for i in range(0, num_blocks):
          if i == num_blocks - 1:
            read_size = task.hdfs_bytes_read%hdfs_block_size
          else:
            read_size = hdfs_block_size
          if random.random() < percent_local_read:
            source = task.self_id
            rec_type = "hdfs_read_local"
          else:
            rec_type = "hdfs_read_remote"
            if len(task.other_ids) > 0: 
              source = task.other_ids[i%len(task.other_ids)]
            else:
              source = u.get_rand_server()
          record = Flow_record(task.start_time, source + "_disk", task.self_id + "_mem", read_size, rec_type)
          add_flow(record, container)


      if task.hdfs_bytes_written > 0:
        num_blocks = task.hdfs_bytes_written/hdfs_block_size + 1
        for i in range(0, num_blocks):
          if i == num_blocks - 1:
            write_size = task.hdfs_bytes_written%hdfs_block_size
          else:
            write_size = hdfs_block_size
          if write_size > 0:
            record1 = Flow_record(task.start_time + task.cpu_ms, task.self_id + "_mem", task.self_id + "_disk", write_size, "hdfs_written_local")
            record2 = Flow_record(task.start_time + task.cpu_ms, task.self_id + "_mem", u.get_rand_server() + "_disk", write_size, "hdfs_written_remote1")
            record3 = Flow_record(task.start_time + task.cpu_ms, task.self_id + "_mem", u.get_rand_server() + "_disk", write_size, "hdfs_written_remote2")
            add_flow(record1, container)
            add_flow(record2, container)
            add_flow(record3, container)

  print "Start sorting. Total flows added:", len(container.flows)
  container.flows.sort(key=lambda r : r.time)

  print "Finished sorting"

  flow_dist_file = open(u.name + "_dist.txt", "w")
  for fsize in sorted(container.flow_size_count):
    line_to_write = str(fsize) + " " + " ".join(map(str, container.flow_size_count[fsize]))
    print line_to_write
    flow_dist_file.write(line_to_write + "\n")
  flow_dist_file.close()

  flow_file = open("../../ramdisk/" + u.name + "_" + str(hdfs_block_size_mb) +"_sortedflows.txt","w")
  for r in container.flows:
    flow_file.write(r.to_ns2_str() + "\n")
  flow_file.close()





def add_flow(flow, container):
  if Flow_record.write_records_to_file:
    container.flows.append(flow)

  flowSizeKey = int(round(pow(10,round(math.log10(flow.size),1)),0))

  if flowSizeKey not in container.flow_size_count:
    container.flow_size_count[flowSizeKey] = [0,0,0,0,0,0,0,0,0,0]
  container.flow_size_count[flowSizeKey][container.name_dict[flow.rec_type]] += 1








def main(argv):
  if len(argv) > 0 and argv[0] == "-s":
    Flow_record.write_records_to_file = False
  u = Cluster("../../ramdisk/1h.txt")
  gen_flows(u)

if __name__ == "__main__" :
  main(sys.argv[1:])


