import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql import SparkSession
from awsglue.job import Job
from pyspark.sql.types import TimestampType, IntegerType
from datetime import datetime
from pyspark.sql.functions import col, from_utc_timestamp, lit

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Sobrescreve as partições necessárias
spark.conf.set('spark.sql.sources.partitionOverwriteMode', 'dynamic')
spark.conf.set('hive.exec.dynamic.partition.mode', 'nonstrict')

df = glueContext.create_dynamic_frame.from_catalog(
    database="db_sor_banco_xis",
    table_name="produto_credito_sor_scarlet").toDF()
    
df = df.select(
    "id",
    "trans_date_trans_time",
    "cc_num",
    "category",
    "idade_cliente"
    "amt",
    "first",
    "last",
    "gender",
    "dob",
    "anomes")
    
df = df.withColumnRenamed("first", "first_name") \
       .withColumnRenamed("last", "last_name")
    
df = df.withColumn("dt_carga", from_utc_timestamp(lit(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'America/Sao_Paulo').cast(TimestampType()))

df = df.filter((col('amt') > 0) | (~col('cc_num').isNull()))

# df.write.option("compression","snappy").partitionBy("anomes").saveAsTable(
#     "db_sot_banco_xis.produto_credito_sot_scarlet",
#     format = "parquet",
#     mode = "overwrite",
#     path = "s3://corp-sot-sa-east-1-850202893763/produto_credito_sot_scarlet/"
# )

df.write.insertInto("db_sor_banco_xis.produto_credito_sor_scarlet", overwrite=True)