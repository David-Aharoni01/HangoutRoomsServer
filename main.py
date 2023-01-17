import pathlib
import uvicorn
from fastapi import FastAPI
import base64
from pydantic import BaseModel
import time
import hashlib
from fastapi.responses import Response
from pydantic.annotated_types import Any

import HelperDB

ip = "david.lan"
port = 8080
app = FastAPI()


class File(BaseModel):
    type: str
    base_64: str


class User(BaseModel):
    phone_number: str
    name: str
    profile_picture: File
    password_hash: str

    def __init__(self, **data: Any):
        super().__init__(**data)
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


''' adding a user:
user = ('0538319302', 'David', None, hashlib.sha1('david2005'.encode()).hexdigest())
add_user(conn, user)
'''


@app.post("/users/check_availability")
async def check_availability(phone_number: str):
    conn = HelperDB.create_connection("files/users.db")
    HelperDB.create_users_table(conn)
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
    HelperDB.create_users_table(conn)
    HelperDB.add_user(conn, tuple(user))
    conn.close()
    print(tuple(user))
    return {'message': f'Created new user:\n{user}',
            'code': 1,
            'tuple': tuple(user)}


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
    uvicorn.run(app, host=ip, port=port)
