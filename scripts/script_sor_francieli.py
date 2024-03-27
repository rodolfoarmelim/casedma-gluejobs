import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
from pyspark.sql.functions import trim, col, from_utc_timestamp, lit, date_format
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, TimestampType, StringType, DecimalType, LongType, DateType
 
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
 
# Sobrescreve as partições necessárias
spark.conf.set('spark.sql.sources.partitionOverwriteMode', 'dynamic')
spark.conf.set('hive.exec.dynamic.partition.mode', 'nonstrict')
 
# Define o schema do dataframe
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("trans_date_trans_time", TimestampType(), True),
    StructField("cc_num", StringType(), True),
    StructField("merchant", StringType(), True),
    StructField("category", StringType(), True),
    StructField("amt", DecimalType(18, 2), True),
    StructField("first", StringType(), True),
    StructField("last", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("street", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("zip", StringType(), True),
    StructField("lat", DecimalType(18, 3), True),
    StructField("long", DecimalType(18, 3), True),
    StructField("city_pop", LongType(), True),
    StructField("job", StringType(), True),
    StructField("dob", DateType(), True),
    StructField("trans_num", StringType(), True),
    StructField("unix_time", StringType(), True),
    StructField("merch_lat", DecimalType(18, 3), True),
    StructField("merch_long", DecimalType(18, 3), True),
    StructField("is_fraud", IntegerType(), True)
])
 
# Lê o arquivo CSV com o schema definido
df_sor = spark.read.csv("s3://landing-zone-850202893763-prod/credit_card_transactions_data.csv", schema=schema, header=True)
 
# Aplica a função trim para todas as colunas do tipo string
df_sor = df_sor.select([trim(c).alias(c) if df_sor.schema[c].dataType == StringType() else c for c in df_sor.columns])
 
# Criando as colunas dt_carga e a coluna de partição anomes
df_sor = df_sor.withColumn('dt_carga', from_utc_timestamp(lit(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'America/Sao_Paulo').cast(TimestampType()))\
               .withColumn('anomes', date_format(col("trans_date_trans_time"), "yyyyMM").cast(IntegerType()))
 
# Escreve os dados na tabela db_sor_banco_xis.produto_credito_sor via insertInto
df_sor.write.insertInto("db_sor_banco_xis.produto_credito_sor_francieli", overwrite=True)
 