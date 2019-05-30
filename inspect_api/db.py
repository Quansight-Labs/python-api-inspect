import sqlite3
import json
import uuid


CREATE_TABLES_INDICES = '''
CREATE TABLE IF NOT EXISTS File (
   id TEXT,
   project TEXT,
   filename TEXT,
   filename_hash TEXT,

   PRIMARY KEY (id),
   UNIQUE (project, filename, filename_hash)
);

CREATE TABLE IF NOT EXISTS ContentStats (
   id TEXT,
   stats BLOB,

   PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS FunctionStats (
   id TEXT,
   namespace TEXT,
   stats BLOB,

   PRIMARY KEY (id, namespace)
);

CREATE INDEX IF NOT EXISTS index_file_project ON File(project);
CREATE INDEX IF NOT EXISTS index_file_filename ON File(filename);
CREATE INDEX IF NOT EXISTS index_file_filename_hash ON File(filename_hash);
CREATE INDEX IF NOT EXISTS index_function_stats_namespace ON FunctionStats(namespace);
'''

def create_connection(filename):
    connection = sqlite3.connect(filename)

    with connection:
        connection.executescript(CREATE_TABLES_INDICES)

    return connection


def check_file_previously_parsed(connection, project, filename, filename_hash):
    with connection:
        result = connection.execute('''
          SELECT id
          FROM File
          WHERE project = ? AND filename = ? AND filename_hash = ?
        ''', (project, filename, filename_hash,)).fetchone()
    return result is not None


def insert_file_stats(connection, batch_stats):
    content_stats = []
    api_stats = []

    for (project, filename, filename_hash), stats in batch_stats.items():
        file_uuid = str(uuid.uuid4()).upper()

        connection.execute('''
        INSERT INTO File (id, project, filename, filename_hash)
        VALUES (?, ?, ?, ?)
        ''', (file_uuid, project, filename, filename_hash))

        content_stats.append((file_uuid, json.dumps(stats['contents'])))
        for namespace in stats['api']:
            _stats = {'.'.join(key): value for key, value in stats['api'][namespace].items()}
            api_stats.append((file_uuid, namespace, json.dumps(_stats)))

    with connection:
        result = connection.executemany('''
          INSERT INTO ContentStats (id, stats)
          VALUES (?, ?)
        ''', content_stats)

        if api_stats:
            result = connection.executemany('''
              INSERT INTO FunctionStats (id, namespace, stats)
              VALUES (?, ?, ?)
            ''', api_stats)
