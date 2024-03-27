import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
from pyspark.sql.functions import col, current_timestamp, datediff, lit, from_utc_timestamp, sum, count
from pyspark.sql.types import TimestampType, IntegerType, DecimalType
 
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
 
# Definindo a configuração de sobrescrita de partição
spark.conf.set('spark.sql.sources.partitionOverwriteMode', 'dynamic')
spark.conf.set('hive.exec.dynamic.partition.mode', 'nonstrict')
 
# Lendo a tabela como DynamicFrame e convertendo para DataFrame
df_sot = glueContext.create_dynamic_frame.from_catalog(
    database="db_sot_banco_xis",
    table_name="produto_credito_sot_scarlet"
).toDF()
 
# Selecionar colunas necessárias
df_spec = df_sot.select(
    "cc_num", 
    "amt", 
    "first_name", 
    "last_name", 
    "gender", 
    "dob", 
    "anomes")
 
# Calcular idade do cliente
df_spec = df_spec.withColumn("idade_cliente", (datediff(current_timestamp(), col("dob")) / 365).cast(IntegerType()))
 
# Renomear colunas e agrupar
df_spec = df_spec.groupBy("cc_num", "first_name", "last_name", "gender", "idade_cliente", "anomes") \
    .agg(sum("amt").cast(DecimalType(18,2)).alias("soma_valor_transacoes"), count("*").cast(IntegerType()).alias("qtd_transacoes"))
# Criar coluna dt_carga com data e hora atual em America/Sao_Paulo
df_spec = df_spec.withColumn("dt_carga", from_utc_timestamp(lit(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'America/Sao_Paulo').cast(TimestampType()))
 
# Selecionar e renomear colunas
df_final = df_spec.select(
    col("cc_num").alias("numero_cartao_credito_cliente"),
    col("first_name").alias("nome_cliente"),
    col("last_name").alias("sobrenome_cliente"),
    col("gender").alias("genero_pessoa"),
    col("idade_cliente"),
    col("soma_valor_transacoes"),
    col("qtd_transacoes"),
    col("dt_carga"),
    col("anomes").alias("ano_mes_transacoes")
)
 
# # Salvando a tabela final
# # df_final.write.insertInto("db_spec_banco_xis.produto_credito_spec_rodolfo", overwrite=True)
# df_final.write.option("compression","snappy").partitionBy("ano_mes_transacoes").saveAsTable(
#     "db_spec_banco_xis.produto_credito_spec_scarlet",
#     format = "parquet",
#     mode = "overwrite",
#     path = "s3://corp-spec-sa-east-1-850202893763/produto_credito_spec_scarlet/"
# )

df_final.write.insertInto("db_sor_banco_xis.produto_credito_sor_scarlet", overwrite=True)