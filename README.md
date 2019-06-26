# Data Warehouse with Amazon Web Services

## Introduction
A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. The app data resides in Amazon S3 storage service, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The startup wants a data engineer to build an ETL pipeline that extracts data from JSON files on Amazon S3 storage, copy the data to staging tables on Redshift database, then transforms data from staging tables into a set of dimensional and fact tables for the analytics team to quickly and easy query for insights in what songs the app users are listening to. 

## Staging Database
A staging database will be created on Amazon Redshift, a  cloud data warehouse service, with two tables "stageEvents" and "stageSongs" to store raw data that are extracted from JSON files that resides on Amazon S3 storage service. These JSON files contains user's song play activies/events and song meta data. These tables have simplistic schema without any primary keys or references as they are mainly serve as temporary holding storage for further processing.

**stageEvents** - store user's song play activies

|COLUMN  	    |TYPE  	        | NOTE   	                             |
|-------------- |---------------| ---------------------------------------|
|artist         |TEXT           | full name of artist                    |
|auth           |VARCHAR        | user authentication status             |
|firstName      |VARCHAR        | user's first name                      |
|gender         |VARCHAR        | gender of user                         |
|itemInSession  |SMALLINT       | total songs count during user's session|
|lasName        |VARCHAR        | user's last name                       |
|length         |FLOAT          | song play time                         |
|level          |VARCHAR        | user's membership level                |
|method         |VARCHAR        | type of http request                   |
|page           |VARCHAR        | the web page user was on               |
|registration   |VARCHAR        | registration ID                        |
|sessionId      |INTEGER        | user's session ID                      |
|song           |VARCHAR        | full song name/title                   |
|status         |SMALLINT       | http request response status           |
|ts             |BIGINT         | timestamp of when the song is played   |
|userAgent      |VARCHAR        | user's browser info                    |
|userId         |INTEGER        | unique record ID of the user           |

**stageSongs** - store song and artist info

|COLUMN  	     |TYPE  	     | NOTE   	                      |
|----------------|---------------|--------------------------------|
|num_songs       |SMALLINT       | total songs count              |
|artist_id       |VARCHAR        | unique record ID of the artist |
|artist_latitude |FLOAT          | artist's location latitude     |
|artist_longitude|FLOAT          | artist's location longitude    |
|artist_location |TEXT           | artist's geo location name     |
|artist_name     |TEXT           | full name of artist            |
|song_id         |VARCHAR        | unique record ID of the song   |
|title           |VARCHAR        | title of the song              |
|duration        |FLOAT          | duration of song               |
|year            |INTEGER        | song release year              |


## Data Warehouse Database Design
The database is designed base on Star schema with one fact table and five dimension tables to achieve song play analysis goal.

### Fact Table
**factSongplays** - store user's song play activities

|COLUMN  	    |TYPE  	        | NOTE   	                             |
|-------------- |---------------| ---------------------------------------|
|songplay_id    |SERIAL         | Primary Key                            |
|start_time     |BIGINT         | foreign key of dimTime table, sortkey  |
|user_id        |INTEGER        | foreign key of dimUsers table          |
|level          |VARCHAR        |                                        |
|song_id        |VARCHAR        | foreign key of dimSongs table          |
|artist_id      |VARCHAR        | foreign key of dimArtist table, distkey|
|session_id     |INTEGER        |                                        |
|location       |VARCHAR        |                                        |
|user_agent     |TEXT           |                                        |

### Dimension Tables
**dimUsers** - store app's users info

|COLUMN  	    |TYPE  	        | NOTE   	    |
|-------------- |---------------| --------------|
|user_id        |INTEGER        | Primary Key   |
|first_name     |VARCHAR(50)    | allow null    |
|last_name      |VARCHAR(50)    | allow null    |
|gender         |VARCHAR(50)    | allow null    |
|level          |VARCHAR(50)    | allow null    |

**dimSongs** - store song data

|COLUMN  	    |TYPE  	        | NOTE   	           |
|-------------- |---------------| ---------------------|
|song_id        |VARCHAR(100)   | Primary Key          |
|title          |VARCHAR(200)   | not null             |
|artist_id      |VARCHAR(100)   | foreign key          |
|year           |SMALLINT       | not null             |
|duration       |NUMERIC        | not null             |

**dimArtists** - store artist data

|COLUMN  	    |TYPE  	        | NOTE   	           |
|-------------- |---------------| ---------------------|
|artist_id      |VARCHAR(100)   | Primary Key, distkey |
|name           |VARCHAR(150)   | allow null           |
|location       |VARCHAR(150)   | allow null           |
|lattitude      |NUMERIC(9,5)   | allow null           |
|longitude      |NUMERIC(9,5)   | allow null           |

**dimTime** - store timestamps in songplay activities broken down into specific time units

|COLUMN  	    |TYPE  	        | NOTE   	           |
|-------------- |---------------|----------------------|
|start_time     |BIGINT         | Primary Key, sortkey |
|hour           |SMALLINT       | allow null           |
|day            |SMALLINT       | allow null           |
|week           |SMALLINT       | allow null           |
|month          |SMALLINT       | allow null           |
|year           |SMALLINT       | allow null           |
|weekday        |SMALLINT       | allow null           |

## Extract-Transform-Load (ETL) Pipeline
ETL pipeline is written in Python, which extract data from static text files, transform data to a clean/proper data format, then load the data into related tables in the database.

The text files are in JSON format and contain data about songs, users, song play sessions/activities. The files are located on two Amazon S3 directories at **"s3://udacity-dend/log_data"** and **"s3://udacity-dend/song_data"**.

## Main Files

**dwh.cfg** - configuration file that store info about Amazon Redshift, Role, and file locations to JSON files on Amazon S3. 

**IMPORTANT:** this config file "**dwh.cfg**" must be properly and completely fill out prior to running ETL python scripts.

**sql_queries.py** - contains all SQL statements that being referenced by other Python scripts.

**create_tables.py** - contains functions to establish connection to Amazon Redshift and rebuild database schema using drops & creates SQL statements. 

**etl.py** - contains functions to read and process files from "song_data" and "log_data" and loads data into Amazon Redshift database. 

## How To Run

The following must be setup on Amazon Web Services before running the scripts/files in this project:

* Create Amazon role with have "read" access privilege to Amazon S3.
* Create a Redshift cluster with at least 8 nodes to get a faster data copying and processing and assigned this cluster with Amazon role with S3 read access privilege.
* Once the Redshift cluster is created, copy the cluster info and related Amazon role into the config file "dwh.cfg"

Run the following commands in local terminal:
1. Run the "create_tables.py" script to setup the database and related tables
>python create_tables.py

2. Run the "etl.py" script to extract data from text files and copy to staging tables, then clean data and insert the data into fact and dimension tables.
>python etl.py