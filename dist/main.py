import argparse

parser=argparse.ArgumentParser(
    description='A lightweight tool based on sweetviz that generates high-density visualizations to kickstart Exploratory Data Analysis within Snowflake using Snowflake Connector for Python with just one line of code.',
    epilog='github.com/malexandersalazar/tools-python-snowflake-statistics-descriptor')
parser.add_argument('user', type=str, help='my.user@company.com')
parser.add_argument('account', type=str, help='xyz01234.us-east-1')
parser.add_argument('warehouse', type=str, help='mywh')
parser.add_argument('database', type=str, help='mydb')
parser.add_argument('schema', type=str, help='myschema')
parser.add_argument('-r','--rows', default=500000, type=int, help='specifies the number of rows (up to 1,000,000) to sample from the table (default: 500000)')
parser.add_argument('-l','--level', choices=['s','t'], default='s', type=str, help='specifies the snowflake object level in which the analysis should be executed, "s" for schema and "t" for table (default: "s")')
parser.add_argument('-t','--table', type=str, help='specifies the snowflake table name')
parser.add_argument('--associations', dest='associations', action='store_true', help='indicates that a correlation graph should be generated')
parser.set_defaults(associations=False)
parser.add_argument('--open-browser', dest='open_browser', action='store_true', help='indicates that a web browser tab should be opened while datasets are analyzed')
parser.set_defaults(open_browser=False)
args=parser.parse_args()

USER = args.user
ACCOUNT = args.account
WAREHOUSE = args.warehouse
DATABASE = args.database
SCHEMA = args.schema
ROWS = args.rows
LEVEL = args.level
TABLE = args.table
ASSOCIATIONS = args.associations
OPEN_BROWSER = args.open_browser

import os
import snowflake.connector
import pandas as pd
import sweetviz as sv
import gc

ctx = snowflake.connector.connect(
    user=USER,
    account=ACCOUNT,
    authenticator='externalbrowser'
)

ctx.execute_string(f"USE WAREHOUSE {WAREHOUSE}", return_cursors=False)

cur = ctx.cursor().execute(f"SHOW TABLES IN {DATABASE}.{SCHEMA}")

tables = []
if(LEVEL=='s'):
    schema_cur = ctx.cursor().execute(f"SHOW TABLES IN {DATABASE}.{SCHEMA}")
    for (created_on,name,database_name,schema_name,kind,comment,cluster_by,rows,bytes,owner,retention_time,automatic_clustering,change_tracking,search_optimization,search_optimization_progress,search_optimization_bytes,is_external) in schema_cur:
        tables.append((f'{database_name}.{schema_name}.{name}',comment,rows,bytes))
else:
    ctx.execute_string(f"USE DATABASE {DATABASE}", return_cursors=False)

    table_query = f"SELECT ROW_COUNT, BYTES, COMMENT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA='{SCHEMA}' AND TABLE_NAME='{TABLE}'"
    table_cur = ctx.cursor().execute(table_query)
    for (rows,bytes,comment) in table_cur:
        tables.append((f'{DATABASE}.{SCHEMA}.{TABLE}',comment,rows,bytes))

if not os.path.exists('obj'):
    os.mkdir('obj')

info_arr = []

# Generate high-density visualizations
for (table_name,comment,rows,bytes) in tables:
    print(f'Loading {table_name}...')

    sheet_name = table_name.split('.')[-1]

    sample_query = f'SELECT * FROM {table_name} SAMPLE BERNOULLI ({ROWS} ROWS)'
    sample_cur = ctx.cursor().execute(sample_query)
    sample_df = pd.DataFrame.from_records(
        iter(sample_cur), columns=[x[0] for x in sample_cur.description])

    is_clustering_eligible = 'YES' if bytes / 1024 / 1024 / 1024 / 1024 >= 1 else 'NO'
    info_arr.append([table_name, comment, rows, bytes, is_clustering_eligible, len(sample_df)])

    analysis = sv.analyze(sample_df, pairwise_analysis=("on" if ASSOCIATIONS else "off"))
    analysis.show_html(f'obj/{sheet_name}.html', open_browser=OPEN_BROWSER)

    del sample_df
    gc.collect()

# Writing summary
eda_info_df = pd.DataFrame(info_arr, columns = ['NAME','COMMENT','TABLE ROWS','TABLE BYTES','CLUSTERING ELIGIBLE','SAMPLE ROWS'])
excel_writer = pd.ExcelWriter(f'obj/{SCHEMA}_EDA_INFO.xlsx', engine='xlsxwriter')
eda_info_df.to_excel(excel_writer, sheet_name=SCHEMA, index=False)
worksheet = excel_writer.sheets[SCHEMA]
for idx, col in enumerate(eda_info_df):  # Loop through all columns
    series = eda_info_df[col]
    max_len = max((
        series.astype(str).str.len().max(),  # Len of largest item
        len(str(series.name))  # Len of column name/header
        )) + 9  # Adding a little extra space
    worksheet.set_column(idx, idx, max_len)  # Set column width
excel_writer.close()