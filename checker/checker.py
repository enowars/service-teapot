import time
import logging
import sys
import aiohttp
import random
import string
import json

from enochecker_async import BaseChecker, BrokenServiceException, create_app, OfflineException, ELKFormatter, CheckerTaskMessage
from logging import LoggerAdapter
from motor import MotorCollection

class TeapotChecker(BaseChecker):
    port = 8004

    def __init__(self):
        super(TeapotChecker, self).__init__("Teapot", 8080, 2, 0, 0)

    def gen_amount(self):
        return random.randrange(0, 10 ** 6)

    def gen_pot(self):
        return random.randrange(10 ** 31, 10 ** 32)

    async def putflag(self, logger: LoggerAdapter, task: CheckerTaskMessage, collection: MotorCollection) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            pot = str(self.gen_pot())
            await collection.insert_one({ 'flag' : task.flag, 'pot': pot })

            milk, almond, whisky, rum = [self.gen_amount() for i in range(4)]
            additions = "Whole-milk;%s,Almond;%s,Whisky;%s,Rum;%s,Flag;%s" % (
                milk, almond, whisky, rum, task.flag)
            headers = {"Accept-Additions": additions}

            try:
                resp = await session.request("BREW", f"http://{task.address}:{TeapotChecker.port}/pot-{pot}", headers=headers)
                text = await resp.text()
            except:
                raise BrokenServiceException(f"http request failed ({sys.exc_info()[0]})")
            if "BREWING" not in text:
                raise BrokenServiceException("Doesn't brew")

    async def getflag(self, logger: LoggerAdapter, task: CheckerTaskMessage, collection: MotorCollection) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            pot = await collection.find_one({ 'flag': task.flag })
            if pot is None:
                raise BrokenServiceException("Could not find pot in db")
            pot = pot["pot"]
            try:
                logger.debug(f"PROPFIND http://{task.address}:{TeapotChecker.port}/pot-{pot}")
                resp = await session.request("PROPFIND", f"http://{task.address}:{TeapotChecker.port}/pot-{pot}")
                text = await resp.text()
            except:
                raise BrokenServiceException(f"http request failed ({sys.exc_info()[0]})")
            if task.flag not in text:
                raise BrokenServiceException(f"Flag not found ({text})")

    async def putnoise(self, logger: LoggerAdapter, task: CheckerTaskMessage, collection: MotorCollection) -> None:
        pass

    async def getnoise(self, logger: LoggerAdapter, task: CheckerTaskMessage, collection: MotorCollection) -> None:
        pass

    async def havoc(self, logger: LoggerAdapter, task: CheckerTaskMessage, collection: MotorCollection) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                resp = await session.get(f"http://{task.address}:{TeapotChecker.port}")
                text = await resp.text()
            except:
                raise BrokenServiceException(f"Http request failed ({sys.exc_info()[0]})")
            
            if "tea" not in text:
                raise BrokenServiceException(f"No tea in /")

            pot = str(self.gen_pot())
            milk, almond, whisky, rum, flag = [self.gen_amount() for i in range(5)]
            additions = "Whole-milk;%s,Almond;%s,Whisky;%s,Rum;%s,Flag;%s" % (
                milk, almond, whisky, rum, flag)
            headers = {"Accept-Additions": additions}

            try:
                resp = await session.request("BREW", f"http://{task.address}:{TeapotChecker.port}/pot-{pot}", headers=headers)
                text = await resp.text()
            except:
                raise BrokenServiceException(f"http request failed ({sys.exc_info()[0]})")
            if "BREWING" not in text:
                raise BrokenServiceException("Doesn't brew")

            addition = random.choice(["Whole-milk", "Almond", "Whisky", "Rum"])
            headers = {"Addition": addition}
            try:
                resp = await session.request("PUT", f"http://{task.address}:{TeapotChecker.port}/pot-{pot}", headers=headers)
                text = await resp.text()
            except:
                raise BrokenServiceException(f"http request failed ({sys.exc_info()[0]})")
            if "ADDED" not in text:
                raise BrokenServiceException("Failed to add ingredient")

            try:
                logger.debug(f"PROPFIND http://{task.address}:{TeapotChecker.port}/pot-{pot}")
                resp = await session.request("PROPFIND", f"http://{task.address}:{TeapotChecker.port}/pot-{pot}")
                text = await resp.text()
            except:
                raise BrokenServiceException(f"http request failed ({sys.exc_info()[0]})")
            for num in (milk+1, almond+1, whisky+1, rum+1):
                if str(num) in text:
                    break
            else:
                raise BrokenServiceException("Failed to add ingredient (propfind)")

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
#handler.setFormatter(ELKFormatter("%(message)s")) #ELK-ready output
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

app = create_app(TeapotChecker()) # mongodb://mongodb:27017