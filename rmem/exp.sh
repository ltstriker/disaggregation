#rmems=( 1500686 1762830 2024974 2287118 2549262 2614798 2680334 2745870 2811406 )
rmems=( 2549262 )
input_size=( 64 128 256 512 1024 2048 3072 4096 5120 6144 7168 8192 9216 10240 )
#input_size=( 1024 )
job="terasort"

echo ============= >> exp_log.txt
for i in {1..2}
do
  for remote_mem in "${rmems[@]}"
  do
    for size in "${input_size[@]}"
    do
      echo "==========================rmem: $remote_mem size: $size iter: $i ===================="
      ./exit_rmem.sh
      echo "exit_rmem.sh done"
      ./init_rmem.sh $remote_mem
      echo "init_rmem.sh done"
      result=$(./hadoop.sh $job $size 2>&1 | python hadoop_state.py)
      output="$(date +%y%m%d%H%M%S) $job $remote_mem $size $result"
      echo $output
      echo $output >> exp_log.txt
    done
  done
done
