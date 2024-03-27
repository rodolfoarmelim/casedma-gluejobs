import sys
import logging
from datetime import datetime
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import *
from uuid import uuid4
from pyspark.sql.types import *
from pyspark.sql.types import StructType, StructField, IntegerType, TimestampType, StringType, DecimalType, LongType, DateType
from pyspark.sql.functions import trim, col, from_utc_timestamp, lit, date_format
from pyspark.sql.functions import (
    col, lower, regexp_replace, year, month, datediff, sum, to_date, countDistinct, avg, trim, current_timestamp, input_file_name, lit
)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Sobrescreve as partições necessárias
spark.conf.set('spark.sql.sources.partitionOverwriteMode', 'dynamic')
spark.conf.set('hive.exec.dynamic.partition.mode', 'nonstrict')

df = StructType([
    StructField("id", IntegerType(), True),
    StructField("trans_date_trans_time", TimestampType(), True),
    StructField("cc_num", StringType(), True),
    StructField("merchant", StringType(), True),
    StructField("category", StringType(), True),
    StructField("amt", DecimalType(18,2), True),
    StructField("first", StringType(), True),
    StructField("last", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("stree", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("zip", StringType(), True),
    StructField("lat", DecimalType(18,3), True),
    StructField("long", DecimalType(18,3), True),
    StructField("city_pop", LongType(), True),
    StructField("job", StringType(), True),
    StructField("dob", DateType(), True),
    StructField("trans_num", StringType(), True),
    StructField("unix_time", StringType(), True),
    StructField("merch_lat", DecimalType(18,3), True),
    StructField("merch_long", DecimalType(18,3), True),
    StructField("is_fraud", IntegerType(), True),
    ])
    
bronze = spark.read.csv("s3://landing-zone-850202893763-prod/credit_card_transactions_data.csv", schema=df, header=True)

bronze = bronze.select([trim(c).alias(c) if bronze.schema[c].dataType == StringType() else c for c in bronze.columns])

bronze = bronze.withColumn('dt_carga', from_utc_timestamp(lit(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'America/Sao_Paulo').cast(TimestampType()))\
               .withColumn('anomes', date_format(col("trans_date_trans_time"), "yyyyMM").cast(IntegerType()))

    
# # # Envie o arquivo para o S3
# database = "db_sor_banco_xis"
# tabela = "produto_credito_sor_scarlet"

# # Variáveis
# s3_bucket_path = "s3://corp-sor-sa-east-1-850202893763/produto_credito_sor_scarlet"
# database_table_name = f"`{database}`.`{tabela}`"

# # Salva o DataFrame como uma nova tabela no catálogo de dados do Glue, especificando o caminho no S3
# bronze.write.mode("overwrite").option("compression", "snappy").partitionBy("anomes").saveAsTable(database_table_name)   

# bronze.write.option("compression","snappy").partitionBy("anomes").saveAsTable(
#     "db_sor_banco_xis.produto_credito_sor_scarlet",
#     format = "parquet",
#     mode = "overwrite",
#     path = "s3://corp-sor-sa-east-1-850202893763/produto_credito_sor_scarlet/"
# )

bronze.write.insertInto("db_sor_banco_xis.produto_credito_sor_scarlet", overwrite=True)