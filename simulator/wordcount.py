from pyspark import SparkContext

if __name__ == "__main__":
    # create Spark context with necessary configuration
    sc = SparkContext()

    # read data from text file and split each line into words
    words = sc.textFile("s3://cc-project-simulation-app/requirements.txt"
                        ).flatMap(lambda line: line.split(" "))

    # count the occurrence of each word
    wordCounts = words.map(lambda word: (word, 1)).reduceByKey(
        lambda a, b: a + b)

    # save the counts to output
    print(f"Word counts are: {wordCounts.count()}")
