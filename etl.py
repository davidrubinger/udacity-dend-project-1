import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *

pd.options.mode.chained_assignment = None  # default='warn'

def process_song_file(cur, filepath):
    """
    Read song file and insert info into songs and artists tables.
    
    Reads in a file in data/song_data/, extracts song and artist info, and inserts
    info into songs and artists dim tables.
    
    Arguments:
        cur: the cursor object. 
        filepath: log data file path. 

    Returns:
        None
    """
    
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = (
        df[["song_id", "title", "artist_id", "year", "duration"]].
        values.
        tolist()[0]
    )
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = (
        df[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]].
        values.
        tolist()[0]
    )
    cur.execute(artist_table_insert, artist_data)

def process_log_file(cur, filepath):
    """
    Read log file and insert info into song play, user and time tables.
    
    Reads in a file in data/log_data/, extracts user and time info, and inserts
    info into user and time dim tables. Also combines that data with data in
    songs table to populate the songplays fact table.
    
    Arguments:
        cur: the cursor object. 
        filepath: log data file path. 

    Returns:
        None
    """
    
    # open log file
    df = pd.read_json(filepath, lines=True)
    
    # filter by NextSong action
    df = df.query("page == 'NextSong'")
    
    # convert stamp column to datetime and extract time-related features
    df.loc[:, "ts"] = pd.to_datetime(df["ts"], unit='ms')
    df.loc[:, "hour"] = df["ts"].apply(lambda x: x.hour)
    df.loc[:, "day"] = df["ts"].apply(lambda x: x.day)
    df.loc[:, "week"] = df["ts"].apply(lambda x: x.week)
    df.loc[:, "month"] = df["ts"].apply(lambda x: x.month)
    df.loc[:, "year"] = df["ts"].apply(lambda x: x.year)
    df.loc[:, "weekday"] = df["ts"].apply(lambda x: x.dayofweek)
    
    time_df = (
        df.loc[:, ["ts", "hour", "day", "week", "month", "year", "weekday"]].drop_duplicates()
    )
    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = (
        df.
        loc[:,["userId", "firstName", "lastName", "gender", "level"]].
        rename({"userId": "user_id",
                "firstName": "first_name",
                "lastName": "last_name"},
               axis="columns").
        drop_duplicates()
    )

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)
    
    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (
            row.ts, row.userId, row.level,
            songid, artistid, row.sessionId, row.location,
            row.userAgent
        )
        cur.execute(songplay_table_insert, songplay_data)

def process_data(cur, conn, filepath, func):
    """
    Apply song and log processing functions to all data files.
    
    Applies process_song_file() and process_log_file() to every file in
    data/song_data/ and data/log_data/, respectively.
    
    Arguments:
        cur: the cursor object.
        conn: database connection object.
        filepath: data/song_data/ or data/log_data/ file path.
        func: process_song_file or process_log_file function.

    Returns:
        None
    """
    
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))
    all_files = [file for file in all_files if ".ipynb_checkpoints" not in file]

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))

def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()