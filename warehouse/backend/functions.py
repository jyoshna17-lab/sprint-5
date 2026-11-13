from sqlalchemy import Integer, String, Column,create_engine, DateTime,ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

USERNAME = "jyoshna"
PASSWORD = "123"

ACCESS_TOKEN_EXPIRY = 5 #mins
REFRESH_TOKEN_EXPIRY = 7*24*60
SECRET_kEY = "SECRET123"
ALGORITHM = "HS256"

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


class User(Base):
    __tablename__="Users"

    user_id =  Column(Integer, primary_key = True)
    user_name = Column(String)
    password = Column(String)
    



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

def get_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    packages = session.query(Package)
    if destination:
        packages = packages.filter(Package.destination == destination)
    if status:
        packages = packages.filter(Package.status == status)
    if arrival_date:
        packages = packages.filter(Package.arrival_date == arrival_date)
    packages = packages.all()
    response = []
    for package in packages:
        temp_package = {
            "id": package.id,
            "name": package.name,
            "destination": package.destination,
            "weight": package.weight,
            "arrival_date": package.arrival_date,
            "status": package.status
        }
        response.append(temp_package)
    session.close()
    return response

def verify_login(username, password):
    session = Session(engine)
    user = session.query(User).filter_by(user_name = username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    session.close()
    access_token=create_token(username = username, token_type="access")
    refresh_token=create_token(username = username, token_type="refresh")
    return {"access_token":access_token, "refresh_token ": refresh_token}


def create_token(username, token_type):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) +timedelta(minutes = time)
    }
    token = jwt.encode(payload = payload ,key = SECRET_kEY, algorithm=ALGORITHM)
    return token



def verify_token(token, token_type):
    try: 
        payload = jwt.decode(jwt=token,key=SECRET_kEY,algorithms=[ALGORITHM])
    
    except:
        return False
    if payload["token_type"] == token_type:
        return payload["username"]
    return False


def get_dispatch_batches(destination=None, vehicle=None, dispatch_status=None):
    session = Session(engine)
    batches = session.query(DispatchBatch)
    if destination:
        batches = batches.filter(DispatchBatch.destination == destination)
    if vehicle:
        batches = batches.filter(DispatchBatch.vehicle == vehicle)
    if dispatch_status:
        batches = batches.filter(DispatchBatch.dispatch_status == dispatch_status)
    batches = batches.all()
    response = []
    for batch in batches:
        temp_batch = {
            "id": batch.id,
            "destination": batch.destination,
            "vehicle": batch.vehicle,
            "dispatch_status": batch.dispatch_status,
            "dispatch_date": batch.dispatch_date
        }
        response.append(temp_batch)
    session.close()
    return response

def get_warehouse_statistics():
    session = Session(engine)
    packages = session.query(Package).all()
    total_packages = len(packages)
    pending_packages = 0
    dispatched_packages = 0
    destination_count = {}
    for package in packages:
        if package.status == "Pending":
            pending_packages += 1
        if package.status == "Dispatched":
            dispatched_packages += 1
        if package.destination in destination_count:
            destination_count[package.destination] += 1
        else:
            destination_count[package.destination] = 1
    session.close()
    response = {
        "total_packages_received": total_packages,
        "pending_packages": pending_packages,
        "dispatched_packages": dispatched_packages,
        "destination_wise_package_count": destination_count
    }
    return response

def add_dispatch_batch(destination, vehicle, package_id):
    session = Session(engine)
    package = session.query(Package).filter(Package.id == package_id).first()
    if package is None:
        session.close()
        return "Package not found"
    if package.destination != destination or package.status != "Pending":
        session.close()
        return "Invalid package"
    batch = DispatchBatch(destination=destination, vehicle=vehicle)
    session.add(batch)
    session.commit()
    package.dispatch_batch_id = batch.id
    session.commit()
    result = {
        "batch_id": batch.id,
        "destination": batch.destination,
        "vehicle": batch.vehicle,
        "package_id": package.id
    }
    session.close()
    return result

#user
def register_user(user_name:str, password:str):
    session = Session(engine)
    user_exists = session.query(User).filter_by(user_name=user_name).first()
    if user_exists is  not None :
        session.close()
        return False
    session.add(User(user_name=user_name,password=ph.hash(password)))
    session.commit()
    session.close()
    return True
