# Download and extract dataset load into sqlite from csv files create
# index on important columns this will take quite awhile dataset is 20
# GB compressed (80 GB uncompressed) and database with indexes is
# about 100 GB. This is actually quite fast when compared with other
# non-parallel methods

wget https://zenodo.org/record/2536573/files/Libraries.io-open-data-1.4.0.tar.gz
tar -xf Libraries.io-open-data-1.4.0.tar.gz

sqlite3 librariesio.sqlite <<EOF
  .mode csv
  .delimiter ','
  .import libraries-1.4.0-2018-12-22/dependencies-1.4.0-2018-12-22.csv dependencies
  .import libraries-1.4.0-2018-12-22/projects-1.4.0-2018-12-22.csv projects
  .import libraries-1.4.0-2018-12-22/projects_with_repository_fields-1.4.0-2018-12-22.csv projects_with_repositories
  .import libraries-1.4.0-2018-12-22/repositories-1.4.0-2018-12-22.csv repositories
  .import libraries-1.4.0-2018-12-22/repository_dependencies-1.4.0-2018-12-22.csv repository_dependencies
  .import libraries-1.4.0-2018-12-22/tags-1.4.0-2018-12-22.csv tags
  .import libraries-1.4.0-2018-12-22/versions-1.4.0-2018-12-22.csv versions

  CREATE UNIQUE INDEX INDEX_DEPENDENCIES ON dependencies (ID);
  CREATE INDEX INDEX_DEPENDENCIES_PROJECT ON dependencies ("Dependency Project ID");
  CREATE UNIQUE INDEX INDEX_REPOSITORY_DEPENDENCIES ON repository_dependencies ("Repository ID");
  CREATE INDEX INDEX_REPOSITORY_DEPENDENCIES_PROJECT ON repository_dependencies ("Dependency Project ID");
  CREATE UNIQUE INDEX INDEX_PROJECTS ON projects (ID);
  CREATE INDEX INDEX_PROJECTS_NAME ON projects (Name);
  CREATE UNIQUE INDEX INDEX_TAGS ON tags (ID);
  CREATE UNIQUE INDEX INDEX_PROJECTS_WITH_REPOSITORY_FIELDS ON projects_with_repository_fields (ID);
  CREATE UNIQUE INDEX INDEX_VERSIONS ON versions (ID);
  CREATE UNIQUE INDEX INDEX_REPOSITORIES ON repositories (ID);
EOF
