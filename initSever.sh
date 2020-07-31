
cd ~
#install numpy
apt-get update
apt install python-pip
python -m pip install --upgrade pip -y
pip install numpy -y

#install java
sudo apt-get install openjdk-8-jdk -y
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"


#init hadoop
cd ~
wget https://archive.apache.org/dist/hadoop/common/hadoop-2.5.1/hadoop-2.5.1.tar.gz
tar -xzvf hadoop-2.5.1.tar.gz
export PATH=$PWD/hadoop-2.5.1/bin:$PATH
hadoop version