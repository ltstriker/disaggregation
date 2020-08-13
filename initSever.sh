
cd ~
#install numpy
sudo apt-get update
sudo apt install python-pip
sudo python -m pip install --upgrade pip
sudo pip install numpy

#install java
sudo apt-get install openjdk-8-jdk
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"


#init hadoop
cd ~
wget https://archive.apache.org/dist/hadoop/common/hadoop-2.5.1/hadoop-2.5.1.tar.gz
tar -xzvf hadoop-2.5.1.tar.gz
export PATH=$PWD/hadoop-2.5.1/bin:$PATH
hadoop version

cd /root
mkdir spark-ec2
echo 10.10.1.1 > /root/spark-ec2/masters
echo 10.10.1.2 > /root/spark-ec2/slaves

mkdir /root/hadoop-2.5.1/conf
cp /root/hadoop-2.5.1/etc/hadoop/mapred-site.xml.template /root/hadoop-2.5.1/conf/mapred-site.xml
cp /root/hadoop-2.5.1/etc/hadoop/core-site.xml /root/hadoop-2.5.1/conf/
cp /root/hadoop-2.5.1/etc/hadoop/hdfs-site.xml /root/hadoop-2.5.1/conf/
ln -s /root/hadoop-2.5.1 /root/ephemeral-hdfs