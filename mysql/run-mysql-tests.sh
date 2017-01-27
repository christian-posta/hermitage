#!/bin/sh
. $(dirname ${BASH_SOURCE})/../util.sh

MYSQL_VERSION=5.7.17

# Run the database
echo "starting the database"
docker run -d  --name hermitage-mysql -e MYSQL_ROOT_PASSWORD=admin mysql:$MYSQL_VERSION

# give some time for mysql to start up... 
docker logs -f hermitage-mysql &
TASK_PID=$!
sleep 15s
kill $TASK_PID

# Run the test
python $(dirname ${BASH_SOURCE})/../parser.py $(relative mysql.md) $(relative mysql) $1