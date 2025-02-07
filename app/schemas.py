from datetime import  datetime
from typing import List, Optional
from pydantic import BaseModel 
from app.enums import ContractType,Gender,RoleType
from app.enums.matchyComparer import Comparer
from app.enums.matchyConditionProperty import ConditionProperty
from app.enums.matchyFieldType import FieldType


class OurBaseModel(BaseModel):
    class Config:
        from_attributes = True

class BaseOut(OurBaseModel):
    detail: str
    status_code: int

class EmployeeBase(OurBaseModel):
    first_name: str
    last_name: str
    email: str
    number: int
    birth_date: datetime | None = None
    address: str | None = None
    cnss_number: str | None = None
    contract_type: ContractType | None = None
    gender: Gender
    roles:List[RoleType]
    phone_number: str | None = None


class EmployeeCreate(EmployeeBase):
    password: str | None = None
    confirm_password: str | None = None
    



class EmployeeOut(OurBaseModel):
    id:int
    created_on:datetime


class ConfirmationAccount(OurBaseModel):
    confirmation_code:str


class BaseOut(OurBaseModel):
    detail: str
    status_code: int



class MatchyCondition(BaseModel):
    property: ConditionProperty
    comparer: Optional[Comparer]=None
    value:int|float|str|List[str]
    custom_fail_message:Optional[str] = None


class MatchyOption(BaseModel):
    display_value:str
    value:Optional[str]=None
    mandatory:Optional[bool]= False
    type: FieldType
    conditions: Optional[List[MatchyCondition]]= []

class ImportPossibleFields(OurBaseModel):
    possible_fields: List[MatchyOption]=[]

class MatchyCell(OurBaseModel):
    value:str
    rowIndex:int 
    colIndex: int


class MatchyUploadEntry(OurBaseModel):
    lines: List[dict[str, MatchyCell]] # [ {cnss_number: {40, 1, 1}, {roles: {Admin, vendor, 1, 2}}, {emp 2}, {emp 3}] # enou emp lkol en tant que dict 3andhom nafs l keys
    forceUpload: Optional[bool] = False 


class MatchyWrongCell(OurBaseModel):
    message:str
    rowIndex:int 
    colIndex: int

class ImportResponse(BaseOut):
    errors:Optional[str]=None
    warnings:Optional[str]=None
    wrong_cells: Optional[List[MatchyWrongCell]]=[] # because in front same value written like that