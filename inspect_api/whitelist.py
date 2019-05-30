import sqlite3


PROJECT_QUERY = '''
SELECT r."Host Type", r."Name with Owner"
FROM dependencies as d
INNER JOIN projects as dp ON d."Dependency Project ID" = dp.ID
INNER JOIN projects as p ON d."Project ID" = p.ID
INNER JOIN repositories as r ON r.ID = p."Repository ID"
WHERE dp.Name = "{project}" AND dp.Platform = "Pypi" AND d."Dependency Name" = "{project}"
GROUP BY r."Host Type", r."Name with Owner"
ORDER BY CAST(r."Stars Count" AS INTEGER) DESC
'''

REPOSITORY_QUERY = '''
SELECT DISTINCT r."Host Type", r."Name with Owner"
FROM repository_dependencies as rd
INNER JOIN projects as p ON p.ID = rd."Dependency Project ID"
INNER JOIN repositories as r ON rd."Repository ID" = r.ID
WHERE p.Name = "{project}" AND p.Platform = "Pypi" AND rd."Dependency Project Name" = "{project}"
GROUP BY r."Host Type", r."Name with Owner"
ORDER BY CAST(r."Stars Count" AS INTEGER) DESC
'''

def _read_packages(cursor):
   packages = {}
   for row in cursor:
      if row[0] == 'GitHub' and row[1] not in packages:
         packages[row[1]] = f'github/{row[1]}/master\n'
   return packages


def create_whitelist(database_filename, project, filename):
   connection = sqlite3.connect(database_filename)
   with connection:
      packages = {}
      with open(filename, 'w') as f:
         f.write('[packages]\n')
         f.write('# owner/repo = site/owner/repo/ref\n')
         cursor = connection.execute(PROJECT_QUERY.format(project=project))
         project_packages =_read_packages(cursor)
         print(f'dependant projects for "{project}" got {len(project_packages)} results')
         cursor = connection.execute(REPOSITORY_QUERY.format(project=project))
         repository_packages = _read_packages(cursor)
         print(f'dependant repositories for "{project}" got {len(repository_packages)} results')
         for key, value in {**project_packages, **repository_packages}.items():
            f.write(f'{key}={value}')
