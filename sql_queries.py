import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

AWS_REGION = config.get('CLUSTER','AWS_REGION')
ARN = config.get('IAM_ROLE','ARN')

LOG_DATA = config.get('S3','LOG_DATA')
LOG_JSONPATH = config.get('S3','LOG_JSONPATH')
SONG_DATA = config.get('S3','SONG_DATA')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS stageEvents"
staging_songs_table_drop = "DROP TABLE IF EXISTS stageSongs"
songplay_table_drop = "DROP TABLE IF EXISTS factSongplays"
user_table_drop = "DROP TABLE IF EXISTS dimUsers"
song_table_drop = "DROP TABLE IF EXISTS dimSongs"
artist_table_drop = "DROP TABLE IF EXISTS dimArtists"
time_table_drop = "DROP TABLE IF EXISTS dimTime"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS stageEvents
(
   artist        TEXT NULL
  ,auth          VARCHAR(50) NULL
  ,firstName     VARCHAR(25) NULL
  ,gender        VARCHAR(10) NULL
  ,itemInSession SMALLINT NULL
  ,lastName      VARCHAR(25) NULL
  ,length        FLOAT NULL DEFAULT 0
  ,level         VARCHAR(20) NULL
  ,location      VARCHAR(50) NULL
  ,method        VARCHAR(10) NULL
  ,page          VARCHAR(20)  NULL
  ,registration  VARCHAR(50)  NULL
  ,sessionId     INTEGER  NULL
  ,song          VARCHAR(200)  NULL
  ,status        SMALLINT NULL
  ,ts            TIMESTAMP NULL
  ,userAgent     VARCHAR(200) NULL
  ,userId        INTEGER  NULL
)
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS stageSongs
(
   num_songs        SMALLINT
  ,artist_id        VARCHAR(50) NULL
  ,artist_latitude  FLOAT NULL
  ,artist_longitude FLOAT NULL
  ,artist_location  TEXT NULL
  ,artist_name      TEXT NULL
  ,song_id          VARCHAR(50) NULL
  ,title            VARCHAR(200) NULL
  ,duration         FLOAT NULL
  ,year             SMALLINT NULL
)
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS factSongplays
(
    songplay_id INTEGER PRIMARY KEY IDENTITY(0,1),
    start_time TIMESTAMP NOT NULL REFERENCES dimTime(start_time) sortkey,
    user_id INTEGER NOT NULL REFERENCES dimUsers(user_id),
    level VARCHAR(50) NULL,
    song_id VARCHAR NOT NULL REFERENCES dimSongs(song_id),
    artist_id VARCHAR REFERENCES dimArtists(artist_id) distkey,
    session_id INTEGER NOT NULL,
    location VARCHAR(200) NULL,
    user_agent TEXT NULL
)
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS dimUsers
(
    user_id INTEGER PRIMARY KEY sortkey,
    first_name VARCHAR(50) NULL,
    last_name VARCHAR(50) NULL,
    gender VARCHAR(50) NULL,
    level VARCHAR(50) NULL
) diststyle ALL;
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS dimSongs
(
    song_id VARCHAR PRIMARY KEY sortkey,
    title VARCHAR(200) NULL,
    artist_id VARCHAR(100) NULL,
    year SMALLINT,
    duration NUMERIC
)
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS dimArtists
(
    artist_id VARCHAR PRIMARY KEY distkey,
    name VARCHAR(100) NULL,
    location VARCHAR(150) NULL,
    lattitude NUMERIC(9,5) NULL,
    longitude NUMERIC(9,5) NULL
)
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS dimTime
(
    start_time TIMESTAMP NOT NULL PRIMARY KEY sortkey,
    hour SMALLINT,
    day SMALLINT,
    week SMALLINT,
    month SMALLINT,
    year SMALLINT,
    weekday SMALLINT
)
""")

# STAGING TABLES

staging_events_copy = ("""
COPY stageEvents 
FROM {}
iam_role {} 
REGION {}
FORMAT AS JSON {}
""").format(LOG_DATA,ARN,AWS_REGION,LOG_JSONPATH)

staging_songs_copy = ("""
COPY stageSongs 
FROM {}
iam_role {} 
region {} 
FORMAT AS JSON 'auto' 
""").format(SONG_DATA,ARN,AWS_REGION)

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO factSongplays(
    start_time,
    user_id,
    level,
    song_id,
    artist_id,
    session_id,
    location,
    user_agent
)
SELECT 
    e.ts,
    e.userId,
    e.level,
    s.song_id,
    s.artist_id,
    e.sessionId,
    e.location,
    e.userAgent 
FROM stageEvents AS e
LEFT JOIN stageSongs AS s 
ON e.song = s.title AND e.artist = s.artist_name 
WHERE e.page = 'NextSong'
""")

user_table_insert = ("""
INSERT INTO dimUsers(
    user_id,
    first_name,
    last_name,
    gender,
    level
) 
SELECT DISTINCT 
    e.userId,
    e.firstName,
    e.lastName,
    e.gender,
    e.level
FROM stageEvents AS e 
WHERE e.userId IS NOT NULL 
AND e.page = 'NextSong'
""")

song_table_insert = ("""
INSERT INTO dimSongs(
    song_id,
    title,
    artist_id,
    year,
    duration
) 
SELECT DISTINCT 
    s.song_id,
    s.title,
    s.artist_id,
    s.year,
    s.duration 
FROM stageSongs AS s 
""")

artist_table_insert = ("""
INSERT INTO dimArtists(
    artist_id,
    name,
    location,
    lattitude,
    longitude    
) 
SELECT DISTINCT 
    s.artist_id,
    s.artist_name,
    s.artist_location,
    s.artist_latitude,
    s.artist_longitude
FROM stageSongs AS s 
""")

time_table_insert = ("""
INSERT INTO dimTime(
    start_time BIGINT NOT NULL PRIMARY KEY sortkey,
    hour SMALLINT,
    day SMALLINT,
    week SMALLINT,
    month SMALLINT,
    year SMALLINT,
    weekday SMALLINT   
) 
SELECT DISTINCT 
    fs.start_time,
    CAST(DATE_PART('hour', fs.start_time) as Integer),
    CAST(DATE_PART('day', fs.start_time) as Integer), 
    CAST(DATE_PART('week', fs.start_time) as Integer),
    CAST(DATE_PART('month', fs.start_time) as Integer),
    CAST(DATE_PART('year', fs.start_time) as Integer),
    CAST(DATE_PART('dow', fs.start_time) as Integer)
FROM factSongplays AS fs 
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, song_table_create, artist_table_create, time_table_create,songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
