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
from pyspark.sql.functions import col, from_utc_timestamp, lit, year, month, datediff, current_date, sum as sql_sum, count as sql_count
 
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
 
# Definindo a configuração de sobrescrita de partição
spark.conf.set('spark.sql.sources.partitionOverwriteMode', 'dynamic')
spark.conf.set('hive.exec.dynamic.partition.mode', 'nonstrict')
 
# Lendo a tabela como DynamicFrame e convertendo para DataFrame
df_produto_credito = glueContext.create_dynamic_frame.from_catalog(
    database="db_sot_banco_xis",
    table_name="produto_credito_sot_jaqueline"
).toDF()
 
# Calculando a idade do cliente em anos
df_filtrado = df_produto_credito.withColumn('idade_cliente', year(current_date()) - year(col('dob')))

# Agrupando pelos dados do cliente e por ano
df_agrupado = df_filtrado.groupBy(
    col("cc_num").alias("numero_cartao_credito_cliente"),
    col("first_name").alias("nome_cliente"),
    col("last_name").alias("sobrenome_cliente"),
    col("gender").alias("genero_pessoa"),
    "idade_cliente",
    "dt_carga",
    col("anomes").alias("ano_mes_transacoes"),
).agg(
    sql_sum("amt").alias("soma_valor_transacoes"),
    sql_count("cc_num").alias("qtd_transacoes")
)

# Selecionando as colunas desejadas
df_final = df_agrupado.select(
    "numero_cartao_credito_cliente",
    "nome_cliente",
    "sobrenome_cliente",
    "genero_pessoa",
    "idade_cliente",
    "soma_valor_transacoes",
    "qtd_transacoes",
    "dt_carga",
    "ano_mes_transacoes"
)
 
# Criando a coluna dt_carga
df_final = df_final.withColumn('dt_carga', from_utc_timestamp(lit(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'America/Sao_Paulo').cast(TimestampType()))
 
# Salvando a tabela final
df_final.write.insertInto("db_sot_banco_xis.produto_credito_spec_jaqueline", overwrite=True)

#df_final.write.option("compression","snappy").partitionBy("ano_mes_transacoes").saveAsTable(
   # "db_spec_banco_xis.produto_credito_spec_jaqueline",
   # format = "parquet",
   # mode = "overwrite",
   # path = "s3://corp-spec-sa-east-1-850202893763/produto_credito_spec_jaqueline")