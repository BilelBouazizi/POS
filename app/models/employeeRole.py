from sqlalchemy import Column, Integer, Enum, ForeignKey
from ..database import Base
from app.enums import RoleType


class EmployeeRole(Base):
    __tablename__ = "employees_roles"


    id=Column(Integer,primary_key=True,nullable=False)
    employee_id=Column(Integer,ForeignKey("employees.id"),nullable=False)
    role=Column(Enum(RoleType),nullable=False)
    

