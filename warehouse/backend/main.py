from fastapi import FastAPI, HTTPException
import functions

app = FastAPI()

@app.post("/packages")
def add_package(name:str, destination:str, weight:int):
    if name == "":
        raise HTTPException(status_code=422, detail = "Package name can not be empty ")
    if destination == "":
        raise HTTPException(status_code = 422 , detail = "Destination can not be empty")
    if weight<=0:
        raise HTTPException(status_code = 422 ,detail = "Weight should be greater than 0")
    return functions.add_package(name=name,destination=destination,weight=weight)
@app.get("/packages/{package_id}")
def get_package(package_id: int):
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Package ID should be greater than 0")
    package = functions.get_package(package_id)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@app.patch("/packages/{package_id}")
def update_package(package_id: int, name: str = None, destination: str = None, weight: int = None):
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Package ID should be greater than 0")
    if name == "":
        raise HTTPException(status_code=422, detail="Package name cannot be empty")
    if destination == "":
        raise HTTPException(status_code=422, detail="Destination cannot be empty")
    if weight is not None and weight <= 0:
        raise HTTPException(status_code=422, detail="Weight should be greater than 0")
    if name is None and destination is None and weight is None:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")
    package = functions.update_package(package_id=package_id,name=name,destination=destination,weight=weight)
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@app.delete("/packages/{package_id}")
def delete_package(package_id: int):
    if package_id <= 0:
        raise HTTPException(status_code=422, detail="Package ID should be greater than 0")
    result = functions.delete_package(package_id)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if result == "dispatched":
        raise HTTPException(status_code=400, detail="Dispatched packages cannot be deleted")
    return {"message": "Package deleted successfully"}

