from sqlalchemy import Integer, String, Column,create_engine, DateTime,ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

class Package(Base):
    __tablename__="packages"

    id = Column(Integer, primary_key=True)
    name=Column(String)
    destination=Column(String)
    weight=Column(Integer)
    arrival_date=Column(DateTime, default = datetime.now)
    status = Column(String , default = "Pending")
    dispatch_batch_id = Column(Integer, ForeignKey("dispatch_batches.id"), nullable = True )


class DispatchBatch(Base):
    __tablename__="dispatch_batches"

    id = Column(Integer, primary_key = True)
    destination = Column(String)
    vehicle = Column(String)
    dispatch_status=Column(String, default = "Pending")
    dispatch_date = Column(DateTime,default= datetime.now)

Base.metadata.create_all(engine)

def add_package(name, destination, weight):
    session = Session(engine)
    package=Package(name=name,destination=destination,weight= weight)
    session.add(package)
    session.commit()
    response={
        "id":package.id,
        "name":package.name,
        "destination":package.destination,
        "weight":package.weight,
        "arrival_date":package.arrival_date,
        "status":package.status
    }
    session.close()
    return response


def get_package(package_id):
    session=Session(engine)
    package = session.query(Package).filter(Package.id ==package_id).first()
    if package is None:
        session.close()
        return None
    response = {
        "id": package.id,
        "name": package.name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }
    session.close()
    return response

def update_package(package_id, name=None, destination=None, weight=None):
    session = Session(engine)
    package = session.query(Package).filter(Package.id == package_id).first()
    if package is None:
        session.close()
        return None
    if name is not None:
        package.name = name
    if destination is not None:
        package.destination = destination
    if weight is not None:
        package.weight = weight
    session.commit()
    response = {
        "id": package.id,
        "name": package.name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }
    session.close()
    return response

def delete_package(package_id):
    session = Session(engine)
    package = session.query(Package).filter(Package.id == package_id).first()
    if package is None:
        session.close()
        return "not_found"
    if package.status == "Dispatched":
        session.close()
        return "dispatched"
    session.query(Package).filter(Package.id == package_id).delete()
    session.commit()
    session.close()
    return "deleted"

  