from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse


from .config import settings

conf = ConnectionConfig(
    MAIL_USERNAME = settings.mail_username,
    MAIL_PASSWORD = settings.mail_password,
    MAIL_FROM = settings.mail_from,
    MAIL_PORT = 465,
    MAIL_SERVER = settings.mail_server,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = Path(__file__).parent
    
)



async def simple_send(emails: list[EmailStr], body: dict) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=emails,
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message,template_name="templates/account_activation.html")
    return JSONResponse(status_code=200, content={"message": "email has been sent"})     