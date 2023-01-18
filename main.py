import os
import pathlib
from typing import Union

import uvicorn
from fastapi import FastAPI
import base64
from pydantic import BaseModel
import time
import hashlib
from fastapi.responses import Response
from pydantic.annotated_types import Any
import platform

import HelperDB

ip = "tamir's_server"
testing = platform.node() == "HOME"
port = 8080
app = FastAPI()


class File(BaseModel):
    type: str
    base_64: str


class User(BaseModel):
    phone_number: str
    name: str
    profile_picture: Union[File, str] = None
    password_hash: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.profile_picture:
            with open(f"files/profile_pictures/{self.phone_number}.{self.profile_picture.type}", 'xb') as f:
                f.write(base64.b64decode(self.profile_picture.base_64))
            self.profile_picture = f"http://{ip}:{port}/files/profile_pictures/{self.phone_number}.{self.profile_picture.type}"

    def __iter__(self):
        yield self.phone_number
        yield self.name
        yield self.profile_picture
        yield self.password_hash


media_types = {"images": "image", "videos": "video", "recordings": "audio"}


@app.get("/")
def read_root():
    return {"Status": "Server Online"}


@app.put("/users/check_availability")
async def check_availability(phone_number: str):
    conn = HelperDB.create_connection("files/users.db")
    users = HelperDB.get_users(conn, phone_number, 'Phone_number')
    conn.close()
    if len(users) > 0:
        return {'message': f'User with phone number {phone_number} already exists',
                'code': 0}
    return {'message': f'Phone number {phone_number} available',
            'code': 1}


@app.post("/users/signup")
async def signup(user: User):
    conn = HelperDB.create_connection("files/users.db")
    HelperDB.add_user(conn, tuple(user))
    conn.close()
    return {'message': f'Created new user: {user}',
            'code': 1,
            'user': user}


@app.put("/users/signin")
async def signin(phone_number: str, password_hash: str):
    conn = HelperDB.create_connection("files/users.db")
    existing_user = HelperDB.get_users(conn, phone_number, '*')
    conn.close()
    if len(existing_user) == 0:
        return {'message': f'User with phone number {phone_number} doesnt exist',
                'code': 0}
    if password_hash != existing_user[0][HelperDB.Users.PASSWORD_HASH]:
        return {'message': f'Wrong password',
                'code': 0}
    return {'message': f'Phone number and password match',
            'code': 1,
            'user': tuple(existing_user)}


@app.post("/files/{directory}")
async def upload(directory: str, file: File):
    file_name = f"{hashlib.sha1(str(int(time.time() * 1000)).encode()).hexdigest()}.{file.type}"
    try:
        with open(f"files/{directory}/{file_name}", 'xb') as f:
            f.write(base64.b64decode(file.base_64))
    except Exception as e:
        return {"message": str(e)}
    return {"message": f"Successfully uploaded file",
            "url": f"http://{ip}:{port}/files/{directory}/{file_name}"}


@app.get("/files/{directory}/{file_name}")
def read_item(directory: str, file_name: str):
    try:
        with open(f"files/{directory}/{file_name}", 'rb') as f:
            extension = pathlib.Path(f"files/{directory}/{file_name}").suffix[1:]
            media_type = f"{media_types.get(directory)}/{extension}"
            return Response(content=f.read(), media_type=media_type)
    except Exception as e:
        return {"message": str(e)}


if __name__ == "__main__":
    if not os.path.exists("files"):
        os.mkdir("files")
    [os.mkdir(os.path.join("files/", directory)) for directory in
     ["images", "videos", "recordings", "profile_pictures"] if not os.path.exists(os.path.join("files/", directory))]
    conn = HelperDB.create_connection("files/users.db")
    HelperDB.create_users_table(conn)
    conn.close()
    if testing:
        ip = "david.lan"
    uvicorn.run(app, host=ip, port=port)
