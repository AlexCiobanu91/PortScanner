import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from subprocess import Popen, PIPE, TimeoutExpired
from bs4 import BeautifulSoup
from datetime import datetime, date
import db as db_manager
import json

def parse_ports_file(host_ports_file):
    with open(host_ports_file) as fd:
        try:
            soup = BeautifulSoup(fd, "xml")
    
            ports = {}
            for port_soup in soup.find_all("port"):
                ports[port_soup["portid"]] = {
                    "state": port_soup.state["state"],
                    "service": port_soup.service["name"],
                    "timestamp": soup.find_all("finished")[0]["time"],
                    "status_change": "-"
                }
            return {
                "data": ports,
                "status": True
            }
        except Exception as e:
            return {
                "data": f"Error when parsing_response_file: {e}",
                "status": False
            }


def update_database(host, port_list, database_url, logger):
    try:
        # logger.info(f"Host {host} updating database")
        print("here")
        session = db_manager.create_session(database_url)
        host_id = db_manager.query_host(host, session=session)
        if not host_id:
            # logger.info(f"Host {host} is not present in the database. Adding new host")
            db_manager.insert_host(host, session=session)
            host_id = db_manager.query_host(host, session=session)

        # logger.info(f"Host {host} updating history")
        db_manager.update_history(port_list, host_id, session=session)
        print("here2")
        return {
            "data": db_manager.get_host_history(host, session),
            "status": True
        }
    except Exception as e:
        print(f"Exception {e}")
        # logger.exception(f"Host {host} Exception when updating db {e}")
        return {
            "data": port_list,
            "status": False
        }


def retrieve_history(host, history_size=0):
    return


def run_nmap(host, host_ports_file, logger):
    with Popen(['nmap', "--open", "-oX", f"{host_ports_file}", host], stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:
        try:
            stdout, stderr = process.communicate()

            #logger.info(f"Host {host} stdout {stdout} stderr {stderr}")
            #logger.info(f"Host {host} generated nmap output file {host_ports_file}")
            if len(stderr.decode("ascii")) > 0:
                if f"Failed to resolve \"{host}\"" in stderr.decode("ascii")\
                    or f"illegal option" in stderr.decode("ascii"):
                    # logger.error(f"Host {host}: invalid host")
                    return {
                        "data" : {
                            "error": f"Invalid host \"{host}\". Please provide a vaild hostname/IP"
                        },
                        "status": False
                    }
            else:
                port_list = parse_ports_file(host_ports_file)
            
                return {
                    "data": port_list["data"],
                    "status": True
                }

        except TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            #logger.error(f"Host {host} stdout {stdout} stderr {stderr}")
            
            return {
                "data": "Internal server error",
                "status": False
            }

def scan_host(host, history_size, database_url, logger):
    #logger.info(f"Running scanning for host {host}")
    host_ports_file = f"{datetime.now().timestamp()}.xml"
    
    result = run_nmap(host, host_ports_file, logger)
    if result["status"]:
        # logger.info(f"Host {host} updating database")
        result = update_database(host, result["data"], database_url, logger)

    return {
        "host": host,
        "ports": result["data"],
        "status": result["status"]
    }


def scan_hosts(request_data, database_url, number_of_threads, logger):
    try:
        logger.info(f"received request_data {request_data}")
        data_dict = json.loads(request_data)
        logger.info(f"succesfully parsed request data {data_dict}")

        history_size = 0
        if not "hosts" in data_dict:
            return {
                "data": "You must provide a list of hosts/ip's separated by a comma",
                "status_code":400
            }

        if not data_dict["hosts"].strip():
            return {
                "data": "You must provide a list of hosts/ip's separated by a comma",
                "status_code": 400
            }

        if "history_size" in data_dict:
            history_size = data_dict["history_size"]
        
        logger.info(f"Running nmap process for each host")
        with multiprocessing.Pool(processes=number_of_threads) as ThreadPool:
            results = ThreadPool.starmap(scan_host, [(host, history_size, database_url, None) for host in data_dict["hosts"].strip().split(', ')])

        logger.info(f"Results from eac process {results}")
        response = {}
        for result in results:
            response[result["host"]] = result["ports"]
            
        return {
            "data": json.dumps(response),
            "status_code": 200
        }

    except Exception as e:
        return {
            "data": f"Bad request {e}",
            "status_code": 400
        }
