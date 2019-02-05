import os
from flask import Flask, abort, request, jsonify
from flask_cors import CORS, cross_origin
from db import init_database
from scan import scan_hosts
database_url = None

def create_app():
    """ create and configure the app"""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_envvar("PORT_SCANNER_CFG")
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    print(app.config)
    
    init_database(app.config["SQLALCHEMY_DATABASE_URI"])
    
    @app.route('/scan', methods=['GET', 'POST'])
    @cross_origin(allow_headers=['Content-Type'])
    def scan_hosts_ports():
        app.logger.info(f"Received request data {request.data}")
        resp = scan_hosts(request.data, app.config["SQLALCHEMY_DATABASE_URI"], app.config["THREADS_NUMBER"], app.logger)
        response = jsonify(resp["data"])
        return response, resp["status_code"]

    #@app.after_request
    #def after_request(response):
    #    response.headers.add('Access-Control-Allow-Origin', '*')
    #    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    #    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    #    return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True,host='0.0.0.0')




