This sample application scans hosts for open ports and keep a history of previous scan using a MySQL database.
The application is configured to run on Docker.
The scripts present in this repo are for creating a Docker instance
The application has two main components:

1) Backend --> web server that provides the /scan endpoint on which you should 
			   POST a list of hosts to be scanned, in json format, such as:
				a) single host: { "hosts": "google.com" }
				b) multiple hosts(separated by comma): { "hosts": "google.com, facebook.com" } 

2) UI --> static Web Page behind an Nginx Proxy with an input box in which hosts can be introduced to be scanned:
				a) single host: google.com
				b) multiple hosts(separated by comma): google.com, facebook.com

How does it work:
After clicking the "scan" button inside the Web Page an ajax call is made to the /scan endpoint of the Backend server
and the response is afterwards parsed using client-side javascript.

To create an instance of this app you should run the run.sh script with the following parameters:
	./run.sh <MySQLAddress> <MySqlDatabaseName> <MySQLUser> <MySQLPassword> <DeployMySql>

if you already have a running MySQL instance you can run the command as follows:
	./run.sh <MySQLAddress> <MySqlDatabaseName> <MySQLUser> <MySQLPassword>

An example of how to run the script is present inside the Jenkinsfile.
Normally the parameters of the run.sh script should also be the parameters of the Jenkins job but here they are shown 
just for example.

Note:
If you want to run a Jenkins pipeline using the Jenkinsfile provided here make sure you have 
the Timestamps plugin the the jenkins user is part of the docker group