import aiohttp
import datetime
import asyncio
import time
import aiofiles

class diary:
    def __init__(self,login,password):
        self.login = login
        self.password = password
        self.update_cookies_time = 0

    async def get_cookies(self):
        async with aiohttp.ClientSession() as session:
            url = "https://dnevnik.egov66.ru/api/auth/Auth/Login"

            headers = {
                "Content-Type":"application/json"
            }

            data = {
                "login": self.login, 
                "password": self.password
            }

            response = await session.post(url=url,
                                            json=data,    
                                            headers=headers)
            
            self.cookies = response.cookies
            url = "https://dnevnik.egov66.ru/api/students"

            response = await session.get(url=url,
                                         cookies = self.cookies)
            
            response_json = await response.json()
            self.user_id = response_json["students"][0]["id"]

    async def getDayHomework(self,delta):
        if time.time() - self.update_cookies_time >= 3600:
            await self.get_cookies()
            self.update_cookies_time = time.time()
        datenow = datetime.datetime.now()
        if delta >= 0: date = datenow + datetime.timedelta(delta)
        else:date = datenow - datetime.timedelta(-delta)
        date_str =  f"{date:%Y-%m-%d}"
        async with aiohttp.ClientSession() as session:
            url = "https://dnevnik.egov66.ru/api/homework"

            params={
                'date': date_str,
                "studentId": self.user_id
            }

            response = await session.get(url=url,
                                         params=params,
                                         cookies = self.cookies)
            
            response_json = await response.json()
        result = {
            "date": date_str, 
            "homework": [
                {
                    "name": lesson["lessonName"],
                    "text": lesson["description"],
                    "files": [file["id"] for file in lesson["homeWorkFiles"]]
                    } for lesson in response_json["homeworks"]
            ]
        }
        return result
    
    async def getDateHomework(self,date_str):
        if time.time() - self.update_cookies_time >= 3600:
            await self.get_cookies()
            self.update_cookies_time = time.time()
        async with aiohttp.ClientSession() as session:
            url = "https://dnevnik.egov66.ru/api/homework"

            params={
                'date': date_str,
                "studentId": self.user_id
            }

            response = await session.get(url=url,
                                         params=params,
                                         cookies = self.cookies)
            
            response_json = await response.json()
        result = {"date": date_str, "homework": [{"name": lesson["lessonName"],"text": lesson["description"],"files": [{"id":file["id"],"name":file["name"]} for file in lesson["homeWorkFiles"]]} for lesson in response_json["homeworks"]]}
        return result
    
    async def getFile(self,fileId):
        async with aiohttp.ClientSession() as session:
            url = f"https://dnevnik.egov66.ru/api/lesson/homework/files/{fileId}"
            async with session.get(url,
                                   cookies = self.cookies) as resp:
                if resp.status == 200:
                        return await resp.read()