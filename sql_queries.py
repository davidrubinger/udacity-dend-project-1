# DROP TABLES

songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

songplay_table_create = ("""
    CREATE TABLE IF NOT EXISTS songplays (
        start_time timestamp NOT NULL,
        user_id int NOT NULL,
        level varchar,
        song_id char (18) NOT NULL,
        artist_id char (18) NOT NULL,
        session_id int,
        location varchar,
        user_agent varchar,
        songplay_id SERIAL PRIMARY KEY
    )
""")

user_table_create = ("""
    CREATE TABLE IF NOT EXISTS users (
        user_id int PRIMARY KEY,
        first_name varchar,
        last_name varchar,
        gender char (1),
        level varchar
    )
""")

song_table_create = ("""
    CREATE TABLE IF NOT EXISTS songs (
        song_id char (18) PRIMARY KEY,
        title varchar,
        artist_id char (18),
        year int,
        duration numeric
    )
""")

artist_table_create = ("""
    CREATE TABLE IF NOT EXISTS artists (
        artist_id char (18) PRIMARY KEY,
        artist_name varchar,
        artist_location varchar,
        artist_latitude decimal,
        artist_longitude decimal
    )
""")

time_table_create = ("""
    CREATE TABLE IF NOT EXISTS time (
        start_time timestamp PRIMARY KEY,
        hour int,
        day int,
        week int,
        month int,
        year int,
        weekday int
    )
""")

# INSERT RECORDS

songplay_table_insert = ("""
    INSERT INTO songplays VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DEFAULT)
""")

user_table_insert = ("""
    INSERT INTO users VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (user_id) DO UPDATE
        SET level = EXCLUDED.level;
""")

song_table_insert = ("""
    INSERT INTO songs VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (song_id) DO NOTHING
""")

artist_table_insert = ("""
    INSERT INTO artists VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (artist_id) DO NOTHING
""")

time_table_insert = ("""
    INSERT INTO time VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (start_time) DO NOTHING
""")

# FIND SONGS

song_select = ("""
    SELECT
        s.song_id,
        s.artist_id
    FROM
        songs s
    LEFT JOIN
        artists a on s.artist_id = a.artist_id
    WHERE
        s.title = %s
        AND a.artist_name = %s
        AND s.duration = %s;
""")

# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]