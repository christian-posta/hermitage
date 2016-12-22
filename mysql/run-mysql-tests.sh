#!/bin/sh
. $(dirname ${BASH_SOURCE})/../util.sh

MYSQL_VERSION=5.7.17

# Run the database
echo "starting the database"
docker run -d  --name hermitage-mysql -e MYSQL_ROOT_PASSWORD=admin mysql:$MYSQL_VERSION

# Run the test
python $(dirname ${BASH_SOURCE})/../parser.py $(relative mysql.md) $(relative mysql) $1