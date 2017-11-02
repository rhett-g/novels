import argparse
import subprocess
from pyspark import SparkContext, SparkConf


def sendCommand(filePath):
    command = ['/playpen/goroot/go/bin/disaster', filePath]
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    response = p.stdout.read()
    p.kill()
    return response[:10]


def initDatabase(partitionOfFilePaths):
    listofname = []
    for line in partitionOfFilePaths:
        listofname.append(sendCommand(line))
    return listofname


if __name__ == "__main__":

    """
        Usage: extracting info from libs
    """
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("first_chap_url", help="URL of first chapter")
    PARSER.add_argument("last_chap_url", help="URL of last chapter")
    ARGS = PARSER.parse_args()
    conf = SparkConf()
    conf.setAppName(')
    conf.set("spark.storage.memoryFraction", "0.5")
    sc = SparkContext(conf=conf)
    lines = spark.sparkContext.textFile("/playpen/test.txt", 2000)
    col = lines.mapPartitions(initDatabase)
    print col.collect()
    spark.stop()
