from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for simplicity
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite-specific argument
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    alias = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=True)
    employee_number = Column(String, nullable=False, unique=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request and response validation
class EmployeeCreate(BaseModel):
    name: str
    last_name: str
    alias: str = None
    email: EmailStr
    phone_number: str = None
    employee_number: str

class EmployeeResponse(EmployeeCreate):
    id: int

    class Config:
        orm_mode = True

# Initialize FastAPI app
app = FastAPI()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST endpoint to create a new employee
@app.post("/employee/", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate, db=Depends(get_db)):
    new_employee = Employee(**employee.dict())
    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: " + str(e))
    return new_employee

# GET endpoint to fetch an employee by employee_number
@app.get("/employee/{employee_number}", response_model=EmployeeResponse)
def get_employee(employee_number: str, db=Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_number == employee_number).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# OpenAPI JSON endpoint (automatically provided by FastAPI, but included for clarity)
@app.get("/openapi.json")
def get_openapi():
    return app.openapi()
