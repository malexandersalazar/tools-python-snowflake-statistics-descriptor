# Snowflake Statistics Descriptor

![alt text](/img/viz.png "Snowflake Statistics Descriptor")

A lightweight tool based on sweetviz that generates high-density visualizations to kickstart Exploratory Data Analysis within Snowflake using Snowflake Connector for Python with just one line of code

## Installation

Just copy the `main.py` script and install the requirements located in the dist folder.

```
pip install -r requirements.txt
```

## Getting Started

| Positional arguments | Example / Help |
| --- | --- |
| user | alexanders@contoso.com |
| account | xyz123.us-east-1 |
| warehouse | MY_WH |
| database | MY_DB |
| schema | MY_SCHEMA |

| Options | Example / Help |
| --- | --- |
| -h, --help | show this help message and exit |
| -r, --rows | specifies the number of rows (up to 1,000,000) to sample from the table (default: 500000) |
| -l, --level | specifies the snowflake object level in which the analysis should be executed, "s" for schema and "t" for table (default: "s") |
| -t, --table | specifies the snowflake table name |
| --associations | indicates that a correlation graph should be generated |
| --open-browser | indicates that a web browser tab should be opened while datasets are analyzed |

The default behaviour of the script will load and analyze the specified number of rows of each table in the selected database schema.

```
python main.py alexanders@contoso.com xyz123.us-east-1 MY_WH SNOWFLAKE_SAMPLE_DATA TPCH_SF100 -r=100000
```

The program will build and save locally high-density HTML visualizations and generate an Excel summary with table name, comment, rows, bytes, grouping eligible flag, and parsed record count in a new folder called **obj**.

![alt text](/img/cmd.png "Snowflake Statistics Descriptor")

If we need a correlation graph to be generated for the columns of each table, we must include the `--associations` flag.

```
python main.py alexanders@contoso.com xyz123.us-east-1 MY_WH SNOWFLAKE_SAMPLE_DATA TPCH_SF100 -r=100000 --associations --open-browser
```

We must consider that correlations and other associations may take a **quadratic time (n^2)** to complete.

![alt text](/img/associations.png "Snowflake Statistics Descriptor")

If we only need the analysis for a single table we must specify "**t**" as `-l` or `--level` argument value with the corresponding **table name** in `-t` or `--table` argument.

```
python main.py alexanders@contoso.com xyz123.us-east-1 MY_WH SNOWFLAKE_SAMPLE_DATA TPCH_SF100 -r=500000 -l=t -t=LINEITEM
```

## Prerequisites

Snowflake Statistics Descriptor was tested with:

* Python: 3.7.16
* Packages:
    * snowflake-connector-python: 3.0.3
    * pandas: 1.3.5
    * sweetviz: 2.1.4
    * XlsxWriter: 3.1.0 
* Anaconda: 2.4.0

## License

This project is licenced under the [MIT License][1].

[1]: https://opensource.org/licenses/mit-license.html "The MIT License | Open Source Initiative"