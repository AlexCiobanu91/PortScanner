#!/bin/bash
MySQLAddress=$1
MySqlDatabaseName=$2
MySQLUser=$3
MySQLPassword=$4
DockerHostIp=$5
DeployMySql=$6

if [ -n "$DeployMySql" ]; then
	echo "Creating new MySql Docker container"
	docker pull mysql
	MySQLAddress="$DockerHostIp"
	docker run --name PortScannerMySql \
		-e MYSQL_ROOT_PASSWORD=MyAw3som3Password \
		-e MYSQL_DATABASE=$MySqlDatabaseName \
		-e MYSQL_USER=$MySQLUser \
		-e MYSQL_PASSWORD=$MySQLPassword \
		-d -p 3306:3306 mysql:latest
	sleep 30
fi

sed "s/replace_user/$MySQLUser/g" -i PortScanner/portscanner.cfg
sed "s/replace_password/$MySQLPassword/g" -i PortScanner/portscanner.cfg
sed "s/replace_address/$MySQLAddress/g" -i PortScanner/portscanner.cfg
sed "s/replace_database_name/$MySqlDatabaseName/g" -i PortScanner/portscanner.cfg
sed "s/replace_backend_address/$DockerHostIp:5000/g" -i UI/index.html

docker build -f Dockerfile_backend -t portscanner/backend .
docker build -f Dockerfile_ui -t portscanner/ui .

docker run -d -p 5000:5000 portscanner/backend
docker run -d -p 8080:80   portscanner/ui


