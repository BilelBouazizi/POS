import uuid
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from . import models,schemas,emailUtil, enums
from .routers import crud
from .database import SessionLocal,engine 
from datetime import datetime
import re
from fastapi.middleware.cors import CORSMiddleware 



app = FastAPI()

#fixme: please use specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origin=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:

        db.close()
@app.get("/")
async def read_root():
    return await emailUtil.simple_send(['y@yopmail.com'],
{
       "first_name": "Bilel",
        "last_name": "BOUAZIZI"
}
                                       )





@app.post("/employee/",response_model=schemas.EmployeeOut)

async def create_user(employee:schemas.EmployeeCreate, db:Session = Depends(get_db)):

    if employee.password != employee.confirm_password:
        raise HTTPException(status_code=400,detail="Password must match")    
    # here we use ask for forgivness because it not reccurent to add an email already exist 
   # db_employee= crud.get_by_email(db,email=employee.email)
 
    #if db_employee:
     #   raise HTTPException (status_code=400, detail="Email already registred")
    return await crud.add(db=db,employee=employee)



@app.patch("/employee")
def confirm_account(confirmationAccountInput: schemas.ConfirmationAccount, db:Session= Depends(get_db)):
    confirmation_code=crud.get_confirmation_code(db, confirmationAccountInput.confirmation_code)

    if not confirmation_code:
        raise HTTPException(status_code=400, detail='token does not exist')
    
    if confirmation_code.status==enums.TokenStatus.USED:
        raise HTTPException(status_code=400, detail='token already used')
    
    diff= (datetime.now()-confirmation_code.created_on).seconds

    if diff > 6000:
        raise HTTPException(status_code=400,detail='token expired')
    # employee become active => he can start using the app
    db.query(models.Employee).filter(models.Employee.id== confirmation_code.employee_id).\
    update({models.Employee.account_status:enums.AccountStatus.ACTIVE}, synchronize_session=False)
    db.commit()

    # token used => you cannot use it again
    db.query(models.AccountActivation).filter(models.AccountActivation.id== confirmation_code.id).\
    update({models.AccountActivation.status:enums.TokenStatus.USED}, synchronize_session=False)
    db.commit()

    return schemas.BaseOut(
        detail= "Account confirmed",
        status_code=status.HTTP_200_OK
    )

email_regex= r'^\S+@\S+\.\S+$'
cnss_regex=r'^\d{8}-\d{2}$'
phone_number_regex=r'^\+216\d{8}$'

mandatory_fields = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "number": "Number",
    "contract_type": "Contract Type",
    "gender": "Gender",
    "employee_roles": "Roles",
                    }

optional_fields={
    "birth_date": "Birth Date",
    "address":"Address",
    "phone_number":"Phone Number",
} 

mandatory_with_condition={
    "cnss_number": ("Cnss Number", lambda employee: isCdiOrCdd(employee))
}

possible_fields={
    **mandatory_fields,
    **optional_fields,
    **mandatory_with_condition,
}
unique_fields={
    "email":"Email",
    "number":"Number",

}
options =[
    schemas.MatchyOption(display_value=mandatory_fields["first_name"] ,value="first_name",mandatory=True,type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_fields["last_name"],value="last_name",mandatory=True,type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_fields["email"],value="email",mandatory=True,type=enums.FieldType.string,conditions=[
       # schemas.MatchyCondition(property=enums.ConditionProperty.regex,comparer=enums.Comparer.e,value=email_regex),
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["number"],value="number",mandatory=True,type=enums.FieldType.integer),
    schemas.MatchyOption(display_value=optional_fields["birth_date"],value="birth_date",mandatory=False,type=enums.FieldType.string),
    schemas.MatchyOption(display_value=optional_fields["address"],value="address",mandatory=False,type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_with_condition["cnss_number"][0],value="cnss_number",mandatory=False,type=enums.FieldType.string,conditions=[
        schemas.MatchyCondition( property=enums.ConditionProperty.regex,comparer=enums.Comparer.e,value=cnss_regex)
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["contract_type"],value="contract_type",mandatory=True,type=enums.FieldType.string,conditions=[
        schemas.MatchyCondition( property=enums.ConditionProperty.value,comparer=enums.Comparer._in,value=enums.ContractType.getPossibleValues())
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["gender"],value="gender",mandatory=True,type=enums.FieldType.string,conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.value,comparer=enums.Comparer._in,value=enums.Gender.getPossibleValues())
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["employee_roles"],value="employee_roles",mandatory=True,type=enums.FieldType.string),
     schemas.MatchyOption(display_value=optional_fields["phone_number"],value="phone_number",mandatory=False,type=enums.FieldType.string,conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.regex,comparer=enums.Comparer.e,value=phone_number_regex)
    ]),

]



def is_regex_matched (pattern,field):
    return field if re.match(pattern,field) else None #ncheckiw itha warming nkhalouha none , itha error mandatory -> error

def is_valid_email(field : str):
    return  is_regex_matched(email_regex,field)

def is_positive_int(field :str):
    try:
        res=int(field)
    except:
        return None #net parsable
    return res if res>=0 else None
def is_valide_date(field :str):
    try:
        #FIXME: try to give the user the possibility to configure date format 
        #or try many format(not recommented) 12/01 -> 12 jan
        # 12/01 -> mm/dd-> 1 dec
        #user we3i bil format
        obj = datetime.strptime(field, ' %Y-%m-%d')
        return obj.isoformat()
    except:
        return None # fchel enou yrodha date -> not parsable to int  
def isCdiOrCdd(employee):
    return employee["contract_type"] in [enums.ContractType.CDD,enums.ContractType.CDI]
def is_valide_cnss_number(employee,field):
   return field if is_regex_matched(cnss_regex,field) else None
  #itha mch shysh ama type contract mch cdi wella cdd => warning
  # => error  
   """  #contract_type= employee["contract_type"] # itha manech thamnin contract type fi dict , rod belek .get()
    contract_type= employee.get("contract_type")
    if not contract_type:
        return None
    if isCdiOrCdd(field): """

def is_valide_phone_number(field): 
    return field if is_regex_matched(phone_number_regex,field) else None

def are_roles_valid(field):
    #admin, venDor,  
    res=[]
    for role_name in field.split(','):
        val= enums.RoleType.is_valid_enum_value(role_name)
        if not val:
            return None
        res.append(val)
    return res # [enums.RoleType.Admin, enums.RoleType.vendor]



fields_check= {
    # fields to validate :( function to validate ,error message if not valid )

    "email": (lambda field: is_valid_email(field), "wrong Email format"),
    "gender":(lambda field: enums.Gender.is_valid_enum_value(field), f"Possible values are: {enums.Gender.getPossibleValues()} "),
    "contract_type":(lambda field: enums.ContractType.is_valid_enum_value(field), f"Possible values are: {enums.ContractType.getPossibleValues()}"),
    "number":(lambda field: is_positive_int(field),"it should be an integer >=0" ),
    "birth_date":(lambda field: is_valide_date(field),"Date format should be dd/mm/YYYY" ),
    "cnss_number": (lambda field: is_valide_cnss_number(field),"it should be{8 digits-{2 digits}} and it is mandotory for cdi and cdd"),
    "phone_number":(lambda field: is_valide_phone_number(field),"Phone number is not valid for tunisia it should start of 8 digits"),
    "roles": (lambda field: are_roles_valid(field),f"Possible values are: {enums.RoleType.getPossibleValues()}")
}

unique_fields={
    "email":models.Employee.email,
    "number" :models.Employee.number,
}

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


@app.post("/employees/import")
def importEmployees():
    pass

@app.get("/employees/possibleFields")
def getPossibleFields(db:Session= Depends(get_db)):
    return schemas.ImportPossibleFields(
        possible_fields=options,
    )

@app.post("/employees/test")
async def upload(entry: schemas.MatchyUploadEntry, backgroundTasks: BackgroundTasks, db:Session= Depends(get_db)):
    employees = entry.lines
    if not employees:   #front lazem ygeri enou fama au moins lines
        #return schemas.BaseOut(status_code=400, detail="Nothing to do, empty file.")
        raise HTTPException(status_code=400,detail="Nothing to do, empty file.")

    if not employees[0]:
        return schemas.BaseOut(status_code=400, detail="Invalid data format.")

    missing_mandatory_fields = set(mandatory_fields.keys()) - employees[0].keys() # 3tina thi9a fil matchy eli input valid 
    if missing_mandatory_fields:
        
        raise HTTPException(status_code=400,
        #return schemas.BaseOut(
                            detail=f"Missing mandatory fields: { ' ,'.join([mandatory_fields[field] for field in missing_mandatory_fields])}" )
          #  status_code=400,
         #   msg=f"Missing mandatory fields: {', '.join(missing_mandatory_fields)}"
        #)

    
    return  valid_employees_data_and_upload(employees,entry.forceUpload, backgroundTasks,db)
    

def is_field_mandatory(employee,field):
    return field in mandatory_fields or (field in mandatory_with_condition and mandatory_with_condition[field][1](employee)) 


#employee we7ed 
def valid_employees_data(employee):
    errors = []
    warnings = []
    wrong_cells = []  #bech nraj3ouha ll matchy ylawnhom bil a7mer
    employee_to_add={field: cell.value for field,cell in employee.item()  }
    for field in possible_fields:
        if field not in employee:
            if is_field_mandatory(employee,field):
                errors.append(f"{possible_fields[field]} is mandatory but missing")
            continue
        cell=employee[field]
        employee_to_add[field]=employee_to_add[field].strip()
        if employee_to_add[field]=='':
            if is_field_mandatory(employee,field):
                msg= f"{possible_fields[field][0]} is mandatory but missing"
                errors.append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg,rowIndex=cell.rowIndex,colIndex=cell.colIndex))
            else:
                employee_to_add[field]=None # fi db tetsab null

        elif field in fields_check:
            converted_val= fields_check[field][0](employee_to_add)
            if converted_val is None: # if not converted_val khater ken je 3ina type bool=> false valid value , int >=0 converted_val=0
                msg=fields_check[field][1]
                (errors if is_field_mandatory(employee,field) else warnings).append(msg) 
                wrong_cells.append(schemas.MatchyWrongCell(message=msg,rowIndex=cell.rowIndex,colIndex=cell.colIndex))
            else:
                employee_to_add[field]=converted_val
    return (errors,warnings,wrong_cells,employee_to_add)




def valid_employees_data_and_upload(employees:list,force_upload:bool,backgroundTasks: BackgroundTasks,db:Session=Depends(get_db)):
    try:
        errors = []
        warnings = []
        wrong_cells = []
        employees_to_add=[] # bech nesta3mlou fil batch add, bech nlemou data kol w nsob fard mara
        roles_per_mail={}
        for line,employee in enumerate(employees): # for i in range (len(employee)) line=i  employee=employees[i]  
            emp_errors,emp_warming,emp_wrong_cells,emp= valid_employees_data(employee)
            if emp_errors:
                msg= ('\n').join(emp_errors)
                errors.append(f"\nLine {line+1}:\n{msg}") 
            if emp_warming:
                msg= ('\n').join(emp_warming)
                warnings.append(f"\nLine {line+1}:\n{msg}") 
            if emp_wrong_cells:
                wrong_cells.extend(emp_wrong_cells)
            roles_per_mail[emp.get('email')]= emp.pop('employee_roles') # email unique 
            emp["password"]=uuid.uuid1
            employees_to_add.append(models.Employee(**emp))
            

    

        for field in unique_fields:
            for line,employee in enumerate(employees):
                values=set()
                cell= employee.get(field)
                val=cell.value.strip()
                if val=='': #if it is mandatory email and number were already checked in field check
                    continue   
                if val in values:
                    msg=f"{possible_fields[field]} should be unique but this value exists more than one in the file"
                    (errors if is_field_mandatory(employee,field) else warnings).append(msg)
                    wrong_cells.append(schemas.MatchyWrongCell(message=msg,rowIndex=cell.rowIndex,colIndex=cell.colIndex))
                else:
                    values.add(val)

            duplicated_vals= db.query(models.Employee).filter(unique_fields[field].in_(values)).all()
            duplicated_vals= {str(val[0]) for val in duplicated_vals}
            if duplicated_vals:
                msg=f"{possible_fields[field]} should be unique.{(', ').join(duplicated_vals)} already exist in database"
                (errors if is_field_mandatory(employee,field) else warnings).append(msg)

                for employee in employees:
                    cell = employee.get(field)
                    val= cell.value.strip()

                    if val in duplicated_vals:

                        wrong_cells.append(schemas.MatchyWrongCell(message=f"{possible_fields[field]} should be unique. {val} already exist in database",rowIndex=cell.rowIndex,colIndex=cell.colIndex))
        
        if errors or (warnings and not force_upload):   #omourou l force ma yet3adech itha errors w yet3ada itha warmings ama lazem force_upload=true
            return schemas.ImportResponse(
                errors=('\n').join(errors),
                warnings=('\n').join(warnings),
                wrongCells=wrong_cells,
                detail="something went wrong",
                status_code=400,
            )


    #exercice: add 
    # add_all vs nektbou l query wa7edna w laken rod belek w hawel este3mel l'orm le max                  
    #n7ebou na3rfou role kol user ba3ed maysirlou add

        db.add_all(employees_to_add) 
        db.flush()
    #case 1: imagine employees lost their order
        #list comprehension present a limit in update
        #db.add_all([[models.employeeRole(employee_id=emp.id, role=role) for role in roles_per_mail[emp.email]]for emp in employees_to_add])
        
        employee_roles_to_add=[]
        for emp in employees_to_add:
            for role in roles_per_mail[emp.email]:
               employee_roles_to_add.append(models.employeeRole(employee_id=emp.id, role=role))      
        db.add_all(employee_roles_to_add)
        db.flush()
        activation_codes_to_add=[]
        email_data=[]
        for emp in employees_to_add:
            token=uuid.uuid1()
            activation_code= models.AccountActivation(employee_id=emp.id,email=emp.email,status=enums.TokenStatus.PENDING,token=token)
            activation_codes_to_add.append(activation_code)
            email_data.append(([emp.email],{
                'name': emp.first_name,
                'code':token,
                'psw':emp.password
            }))
        db.add(activation_code)
        db.flush()
        #choice 1, wait for the sending(takes time, in case of problem, we rollback all transactions) 
        for email_datum in email_data:
             #send confirmation email
            backgroundTasks.add_task(emailUtil.simple_send,email_datum[0],email_datum[1])  
         #choice 2, do it using background task, if failed, no problem add a btn received an email? sent again
        db.commit()  

   
    except Exception as e:
        db.rollback()
        text=str(e)
        add_error(text,db)
        raise HTTPException(status_code=500, detail=get_error_message(text))
    return schemas.ImportResponse(
                detail="file uploaded",
                status_code= 201,
                
            )
 