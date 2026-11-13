from fastapi import FastAPI, HTTPException, Header, Body
from pydantic import BaseModel, Field
import functions
from datetime import datetime, date
app = FastAPI()


class PackageCreate(BaseModel):
    name: str
    destination: str
    weight: int = Field(gt=0)
    arrival_date: date


class PackageUpdate(BaseModel):
    name: str | None = Field(default=None)
    destination: str | None = Field(default=None)
    weight: int | None = Field(default=None, gt=0)


class UserRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    user_type: str

class DispatchBatchCreate(BaseModel):
    destination: str
    vehicle: str

USER_TYPES = ["admin", "staff"]


def authorize(token, allowed_user_types):
    payload = functions.verify_token(token=token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")
    if payload["user_type"] not in allowed_user_types:
        raise HTTPException(status_code=403, detail="You do not have permission to do this")
    return payload


@app.post("/packages")
def add_package(package: PackageCreate, token=Header(None)):
    authorize(token, ["admin", "staff"])
    return functions.add_package(name=package.name,destination=package.destination,weight=package.weight,arrival_date=package.arrival_date)

@app.get("/packages/{package_id}")
def get_package(package_id: int, token=Header(None)):
    authorize(token, ["admin", "staff"])
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Package ID should be greater than 0")
    package = functions.get_package(package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@app.patch("/packages/{package_id}")
def update_package(package_id: int, package: PackageUpdate, token=Header(None)):
    authorize(token, ["admin", "staff"])
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Package ID should be greater than 0")
    update_data = package.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")
    result = functions.update_package(package_id=package_id,name=update_data.get("name"),destination=update_data.get("destination"),weight=update_data.get("weight"))
    if result is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return result

@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token=Header(None)):
    authorize(token, ["admin"])
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Package ID should be greater than 0")
    result = functions.delete_package(package_id)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if result == "dispatched":
        raise HTTPException(status_code=400, detail="Dispatched packages cannot be deleted")
    return {"message": "Package deleted successfully"}

@app.get("/packages")
def get_packages(destination=None, status=None, arrival_date: date = None, token=Header(None)):
    authorize(token, ["admin", "staff"])
    return functions.get_packages(destination=destination,status=status,arrival_date=arrival_date)

@app.post("/login")
def login(user: UserRequest):
    token = functions.verify_login(username=user.username,password=user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return token

@app.post("/refresh")
def refresh(refresh_token=Header(None)):
    payload = functions.verify_token(token=refresh_token,token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")
    access_token = functions.create_token(username=payload["username"],user_type=payload["user_type"],token_type="access")
    return {"access_token": access_token}

@app.get("/dispatch-batches")
def get_dispatch_batches(destination=None, vehicle=None, dispatch_status=None, token=Header(None)):
    authorize(token, ["admin", "staff"])
    return functions.get_dispatch_batches(destination=destination,vehicle=vehicle,dispatch_status=dispatch_status)

@app.get("/warehouse-statistics")
def get_warehouse_statistics(token=Header(None)):
    authorize(token, ["admin"])
    return functions.get_warehouse_statistics()

@app.post("/dispatch-batches")
def add_dispatch_batch(batch: DispatchBatchCreate, token=Header(None)):
    authorize(token, ["admin"])
    return functions.add_dispatch_batch(destination=batch.destination,vehicle=batch.vehicle)

@app.post("/register")
def register_user(user: RegisterRequest):
    if user.user_type not in USER_TYPES:
        raise HTTPException(status_code=400, detail="User type must be admin or staff")
    if functions.register_user(user_name=user.username,password=user.password,user_type=user.user_type):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")

