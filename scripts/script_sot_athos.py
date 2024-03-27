import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
from pyspark.sql.functions import col, from_utc_timestamp, lit
from pyspark.sql import SparkSession
from pyspark.sql.types import TimestampType, IntegerType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Definindo a configuração de sobrescrita de partição
spark.conf.set('spark.sql.sources.partitionOverwriteMode', 'dynamic')
spark.conf.set('hive.exec.dynamic.partition.mode', 'nonstrict')

# Lendo a tabela como DynamicFrame e convertendo para DataFrame
df_produto_credito = glueContext.create_dynamic_frame.from_catalog(
    database="db_sor_banco_xis",
    table_name="produto_credito_sor_athos"
).toDF()

# Selecionando as colunas desejadas
df_selecionado = df_produto_credito.select(
    "id",
    "trans_date_trans_time",
    "cc_num",
    "category",
    "amt",
    col('first').alias('first_name'),
    col('last').alias('last_name'),
    "gender",
    "dob",
    "anomes"
)

# Filtrando os dados
df_filtrado = df_selecionado.where(
    (col('amt') > 0) | (~col('cc_num').isNull())
)

# Criando a coluna dt_carga
df_filtrado = df_filtrado.withColumn('dt_carga', from_utc_timestamp(lit(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'America/Sao_Paulo').cast(TimestampType()))

# Selecionando as colunas finais
df_filtrado = df_filtrado.select(
    "id",
    "trans_date_trans_time",
    "cc_num",
    "category",
    "amt",
    "first_name",
    "last_name",
    "gender",
    "dob",
    "dt_carga",
    col("anomes").cast(IntegerType()),
)

# Salvando a tabela final
df_filtrado.write.insertInto("db_sot_banco_xis.produto_credito_sot_athos", overwrite=True)