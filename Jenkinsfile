timestamps{
node () {
	checkout scm
	sh """
		chmod +x run.sh
		./run.sh 51.141.126.61:3306 PortScannerDB testUser 12345678 51.141.126.61 yes
	"""
}
}