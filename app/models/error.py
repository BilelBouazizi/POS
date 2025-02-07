from sqlalchemy import Column, DateTime, Integer,ForeignKey, String, func
from ..database import Base



class Error(Base):
    __tablename__ = "errors"


    id=Column(Integer,primary_key=True)
    text=Column(String,nullable=False)
    
    #employee_id=Column(Integer,ForeignKey("employees.id"),nullable=False)
    created_on=Column(DateTime,nullable=False, server_default= func.now())
   

