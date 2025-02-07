from sqlalchemy import Column, Integer, Enum, ForeignKey,String,DateTime, func
from ..database import Base
from app.enums import TokenStatus



class ResetPassword(Base):
    __tablename__ = "reset_password"


    id=Column(Integer,primary_key=True,nullable=False)
    employee_id=Column(Integer,ForeignKey("employees.id"),nullable=False)
    email=Column(String,nullable=False)
    token=Column(String,nullable=False)
    status=Column(Enum(TokenStatus),nullable=False)
    created_on=Column(DateTime,nullable=False, server_default= func.now())


    

