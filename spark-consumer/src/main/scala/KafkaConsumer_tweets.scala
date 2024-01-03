import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.types._
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.SaveMode

object KafkaConsumerTweets {

  def main(args: Array[String]): Unit = {
    //  SparkSession
    val spark = SparkSession.builder
      .appName("TweetsConsumer")
      .master("local[8]")
      .getOrCreate()

    import spark.implicits._  //  Spark implicits for DataFrame operations
    //  the schema for tweets
    val tweetSchema = new StructType()
      .add("id", StringType)
      .add("date", StringType)
      .add("user", StringType)
      .add("text", StringType)
      .add("retweets", IntegerType)

    // Read stream data from Kafka
    val df = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "localhost:9092")  // Kafka broker address
      .option("subscribe", "tweets-topic")  //subscribe to Kafka topic
      .load()

    // Select and parse JSON data from Kafka into a structured DataFrame
    val tweets = df.selectExpr("CAST(value AS STRING) as json")
      .select(from_json($"json", tweetSchema).as("data"))
      .select("data.*")

    //  write data to MongoDB

    // Function to write each batch of data to MongoDB
    def writeToMongoDB(batchDF: DataFrame, batchId: Long): Unit = {
      batchDF.write
        .format("mongo")
        .mode(SaveMode.Append)
        .option("uri", "mongodb://localhost:27017/BigData_tweets.tweets")
        .save()
    }

    val query = tweets.writeStream
      .outputMode("append")  // Output mode append
      .(writeToMongoDB _)  // Apply writeToMongoDB function to each batch
      .option("checkpointLocforeachBatchation", "D:\\STREAMING")  // Checkpoint location for logs
      .trigger(Trigger.ProcessingTime("5 seconds"))
      .start()

    query.awaitTermination()  // Await the termination of the streaming query
  }
}
