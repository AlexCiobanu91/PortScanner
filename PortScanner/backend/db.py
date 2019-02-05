import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Host(Base):
    __tablename__ = "hosts"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)
    hostname = sqlalchemy.Column(sqlalchemy.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Hostname {self.hostname}'


class History(Base):
    __tablename__ = "history"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    port = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    open = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    service = sqlalchemy.Column(sqlalchemy.String(120), nullable=False)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    run = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    host_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(Host.id))
    
    def __repr__(self):
        return f'Port {self.port}: Open {self.open} Service {self.service} Timestamp {self.timestamp} Run {self.run} Host {self.host_id}'


def init_database(database_url):
    if not database_exists(database_url):
        create_database(database_url)
    
    db_engine = create_engine(database_url)
    if not db_engine.dialect.has_table(db_engine, "hosts"):
        Host.__table__.create(db_engine)
    
    if not db_engine.dialect.has_table(db_engine, "history"):
        History.__table__.create(db_engine)

def create_session(database_url):
    db_engine = create_engine(database_url)
    session = sessionmaker(bind=db_engine)
    return session()

def insert_host(host, session=None):
    if query_host(host, session) is None:
        new_host = Host(hostname=host)
        session.add(new_host)
        session.commit()

def get_all_hosts(session):
    hosts = session.query(Host).all()
    return hosts

def query_host(host, session):
    if session.query(Host).filter(Host.hostname.in_([host])).count() > 0:
        host_entry = session.query(Host).filter(Host.hostname.in_([host])).first()
        return host_entry.id
    else:
        return None

def update_history(port_list, host_id, session):
    last_run = session.query(History).filter(History.host_id.in_([host_id])).order_by(History.run.desc()).first()

    if not last_run:
        last_run = -1
    else:
        last_run = last_run.run + 1

    for port in port_list.keys():
        new_history_entry = History(port=int(port),
                                    open=True if port_list[port]["state"] == "open" else False,
                                    service=port_list[port]["service"],
                                    timestamp=datetime.fromtimestamp(int(port_list[port]["timestamp"])),
                                    run=last_run,
                                    host_id=host_id)
    
        session.add(new_history_entry)

    session.commit()

def get_host_history(host, session):
    host_id = query_host(host, session)
    if host_id:
        host_history = session.query(History.port, History.open, History.service, History.timestamp).filter(
            History.host_id.in_([host_id])).order_by(History.timestamp.desc()).all()

        history_list = []
        for hist in host_history:
            history_list.append({
                "timestamp": str(hist[3]),
                "port": hist[0],
                "open": hist[1],
                "service": hist[2]
            })

        return {
            "data": history_list,
            "status": True
        }
    else:
        return {
            "data": f"No host {host} found",
            "status": True
        }