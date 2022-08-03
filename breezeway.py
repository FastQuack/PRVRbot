from typing import Optional, List
import json
import logging
import aiohttp


class AsyncApp:

    def __init__(self, client_id: str, client_secret: str, url: Optional[str] = "api.breezeway.io",
                 company_id: Optional[int] = None):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__url = url
        self.__access_token = None
        self.__refresh_token = None
        self.authenticate()
        self.company_id = company_id or self.get_companies()[0]["id"]

    def get_url(self):
        return self.__url

    async def authenticate(self) -> bool:
        logging.info("Authenticating")
        url = f"https://{self.__url}/public/auth/v1/"

        payload = json.dumps({
            "client_id": self.__client_id,
            "client_secret": self.__client_secret
        })
        headers = {
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                body = await response.json()

        if self.company_id is None:
            self.company_id = await self.get_companies()[0]["id"]

        if response.status == 200:
            logging.debug(f"Authentication successful, received data:\n {body}")
            self.__access_token = body["access_token"]
            self.__refresh_token = body["refresh_token"]
        else:
            logging.error(f"Authentication failed, received data:\n {body}")

            return response.status == 200

    async def get_companies(self):
        logging.info("Getting companies")
        url = f"https://{self.__url}/public/inventory/v1/companies"

        headers = {
            "Authorization": f"JWT {self.__access_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                body = await response.json()

        if response.status == 200:
            logging.debug(f"Successfully got companies. received data:\n {body}")
            return body
        else:
            logging.error(f"Failed to get companies, received data:\n {body}")

    async def get_units(self):
        logging.info("Getting properties")
        url = f"https://{self.__url}/public/inventory/v1/property/external-id?reference_company_id={self.company_id}"

        headers = {
            'Authorization': f'JWT {self.__access_token}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                body = await response.json()

        if response.status == 200:
            logging.debug(f"Successfully got properties. received data:\n {body}")
            return body
        else:
            logging.error(f"Failed to get properties, received data:\n {body}")

    async def get_people(self):
        logging.info("Getting people")
        url = f"https://{self.__url}/public/inventory/v1/people?status=active"

        headers = {
            'Authorization': f'JWT {self.__access_token}',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                body = await response.json()

        if response.status == 200:
            logging.debug(f"Successfully got people. received data:\n {body}")
            return body
        else:
            logging.error(f"Failed to get people, received data:\n {body}")

    async def create_project(
            self, unit_id: int | str, department: str, priority: str = "normal", title: str = None,
            description: Optional[str] = None, template_id: Optional[int] = None, due_date: Optional[str] = None,
            due_time: Optional[str] = None, assignees: Optional[List[int]] = [],
            tag_ids: Optional[List[int]] = []):
        """department: (housekeeping, inspection, or maintenance)
        priority: (urgent, high, normal, low, or watch)"""
        logging.info("Creating project")
        url = f"https://{self.__url}/public/inventory/v1/task/"

        payload = json.dumps({
            "home_id": f"{unit_id}",
            "type_department": department,
            "type_priority": priority,
            "name": title,
            "description": description,
            "scheduled_date": due_date,
            "scheduled_time": due_time,
            "assignments": assignees,
            "template_id": template_id,
            "tags": tag_ids
        })
        headers = {
            'Authorization': f"JWT {self.__access_token}",
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                body = await response.json()

        if response.status == 201:
            logging.info(f"Successfully created task. received data:\n {body}")
        else:
            logging.error(f"Failed to create task, received data:\n {body}")

        return body
