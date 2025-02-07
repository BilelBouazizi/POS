
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import emailUtil
from .. import models,schemas,enums
import uuid



def get(db:Session, id:int):
    return db.query(models.Employee).filter(models.Employee.id == id).first()


def get_confirmation_code(db:Session, code:str):
    return db.query(models.AccountActivation).filter(models.AccountActivation.token==code).first()

#def get_by_email(db:Session, email:str):
#    return db.query(models.Employee).filter(models.Employee.email== email).first()


def getAll(db:Session,skip:int=0, limit:int=100):
    return db.query(models.Employee).offset(skip).limit(limit).all()
error_keys={
    "employees_roles_employee_id_fkey":"No Employee with this id",
    "employees_roles_pkey":"No employee role with this id",
    "ck_employees_cnss_number":"It should be {8 digits}.{2 digits} and it is mandatory",
    "employees_email_key":"Email already exist",
    "employees_pkey":"No employee <ith this id"
}
def get_error_message(error_message):
    for error_key in error_keys:
        if error_key in error_message:
            return error_keys[error_key]
    return "Something went wrong"

def add_error(text,db):
    try:
        db.add(models.Error(
              text=text,
             
        ))
        db.commit()
    except Exception as e:
        #alternative solution bech ken db tahet najem nal9a mochkla
        raise HTTPException(status_code=500,detail="Something went wrong")



async def add(db:Session, employee:schemas.EmployeeCreate):
    try:
        not_hashed_pwd=employee.password
        employee.password = employee.password + "notreallyhashed"
        #fil moment hetha db_model 3indha id=null
        employee_data= employee.model_dump()
        employee_data.pop('confirm_password')
        roles=employee_data.pop('roles')
        db_employee= models.Employee(**employee_data)
        db.add(db_employee)# it is pending nothing in db
        #autoflush=true par default, yaani yzid fi session w toul yflushi fi db 
        db.flush()   #tsajel change fi db commit vs flush (returned an id) employee tsab fi db
        db.refresh(db_employee) #ba3ed refrech db 3tat id lil employee , kif na3mlou refrech we get the id 

    #add employee role
        #for role in roles:
         #   db_role= models.EmployeeRole(role=role, employee_id=db_employee.id)
          #  db.add(db_role)
           # db.commit() # 3la kol role 3malna transaction
           # db.refresh(db_role)
        db.add_all([models.EmployeeRole(role=role, employee_id=db_employee.id) for role in roles])

    #add confirmation code



        activation_code= models.AccountActivation(employee_id=db_employee.id,email=db_employee.email,status=enums.TokenStatus.PENDING,token=uuid.uuid1())
        db.add(activation_code)
        db.commit() # itha ma yhemekech fil mailteb3ath wela le w tzid btn f web bech yeb3ith mail itha ma jahouch
        #db.refresh(activation_code)

    #send confirmation email (fixme later, duplicated code)
        await emailUtil.simple_send([db_employee.email],{
            'name': employee_data["first_name"],
            'code': activation_code.token,
            'psw' : not_hashed_pwd
        }) 

        db.commit() #itha tchouf wala PO ychouf enou mail lazem yousel  

    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text,db)
    

        raise HTTPException(status_code=500,detail=get_error_message(text))
        # Ex1:
    # tkhayel 3andek customers, jek client f telifone (3andek service support) 9alek rani 7awelet nzid user w jetni l error hethi
    # w choufli 7al chta3mel houni
    # Ex2:
    """
    psycopg2.error.CkeckViolation "ck_employees_cnss_number"

    3lech traje3lou sth went wrong w enti ta3ref howa enou regex cnss number ghalet?

    hint sghayer:
    ta3ref esm l constraint ck_employees_cnss_number
    """ 
    return schemas.EmployeeOut(**db_employee.__dict__)
    

