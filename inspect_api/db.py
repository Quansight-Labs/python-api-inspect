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

CREATE TABLE IF NOT EXISTS AttributeStats (
   id TEXT,
   namespace TEXT,
   stats BLOB,

   PRIMARY KEY (id, namespace)
);

CREATE TABLE IF NOT EXISTS DefFunctionStats (
   id TEXT,
   stats BLOB,

   PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS DefClassStats (
   id TEXT,
   stats BLOB,

   PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS index_file_project ON File(project);
CREATE INDEX IF NOT EXISTS index_file_filename ON File(filename);
CREATE INDEX IF NOT EXISTS index_file_filename_hash ON File(filename_hash);
CREATE INDEX IF NOT EXISTS index_function_stats_namespace ON FunctionStats(namespace);
CREATE INDEX IF NOT EXISTS index_attribute_stats_namespace ON AttributeStats(namespace);
'''

def create_connection(filename):
    connection = sqlite3.connect(filename, )

    with connection:
        connection.execute('PRAGMA journal_mode=WAL')
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
    def_function_stats = []
    def_class_stats = []
    function_stats = []
    attribute_stats = []

    for (project, filename, filename_hash), stats in batch_stats.items():
        file_uuid = str(uuid.uuid4()).upper()

        connection.execute('''
        INSERT INTO File (id, project, filename, filename_hash)
        VALUES (?, ?, ?, ?)
        ''', (file_uuid, project, filename, filename_hash))

        if stats['def_function']['count'] != 0:
            content_stats.append((file_uuid, json.dumps(stats['contents'])))
            def_function_stats.append((file_uuid, json.dumps(stats['def_function'])))

        if stats['def_class']['count'] != 0:
            stats['def_class']['inherit'] = {'.'.join(key): value for key, value in stats['def_class']['inherit'].items()}
            def_class_stats.append((file_uuid, json.dumps(stats['def_class'])))

        for namespace in stats['function']:
            _stats = {'.'.join(key): value for key, value in stats['function'][namespace].items()}
            function_stats.append((file_uuid, namespace, json.dumps(_stats)))

        for namespace in stats['attribute']:
            _stats = {'.'.join(key): value for key, value in stats['attribute'][namespace].items()}
            attribute_stats.append((file_uuid, namespace, json.dumps(_stats)))

    with connection:
        result = connection.executemany('''
          INSERT INTO ContentStats (id, stats)
          VALUES (?, ?)
        ''', content_stats)

        if def_function_stats:
            result = connection.executemany('''
              INSERT INTO DefFunctionStats (id, stats)
              VALUES (?, ?)
            ''', def_function_stats)

        if def_class_stats:
            result = connection.executemany('''
              INSERT INTO DefClassStats (id, stats)
              VALUES (?, ?)
            ''', def_class_stats)

        if function_stats:
            result = connection.executemany('''
              INSERT INTO FunctionStats (id, namespace, stats)
              VALUES (?, ?, ?)
            ''', function_stats)

        if attribute_stats:
            result = connection.executemany('''
              INSERT INTO AttributeStats (id, namespace, stats)
              VALUES (?, ?, ?)
            ''', attribute_stats)
