#!/usr/bin/env python3
import random
from enochecker import BaseChecker, BrokenServiceException, assert_equals, assert_in, run


class TeapotChecker(BaseChecker):
    """
    Change the methods given here, then simply create the class and .run() it.
    Magic.

    A few convenient methods and helpers are provided in the BaseChecker.
    ensure_bytes ans ensure_unicode to make sure strings are always equal.

    As well as methods:
    self.connect() connects to the remote server.
    self.http_get and self.http_post request from http.
    self.team_db is a dict that stores its contents to filesystem. (call .persist() to make sure)
    self.readline_expect(): fails if it's not read correctly

    To read the whole docu and find more goodies, run python -m pydoc enolib
    (Or read the source, Luke)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = 3255  # default port to send requests to.

    def gen_amount(self):
        return random.randrange(0, 10 ** 6)

    def gen_pot(self):
        return random.randrange(10 ** 31, 10 ** 32)

    def putflag(self):
        pot = self.gen_pot()
        self.team_db[self.flag] = pot
        flag_id = pot

        milk, almond, whisky, rum = [self.gen_amount() for i in range(4)]

        additions = "Whole-milk;%s,Almond;%s,Whisky;%s,Rum;%s,Flag;%s" % (
            milk, almond, whisky, rum, self.flag)
        headers = {"Accept-Additions": additions}

        resp = self.http("BREW", "/pot-%s" % (pot), headers=headers)
        if resp.status_code != 200 or "BREWING" not in resp.text:
            raise BrokenServiceException("doesn't brew")

    def getflag(self):
        pot = self.team_db[self.flag]
        resp = self.http("PROPFIND", "/pot-%s" % (pot))
        assert_equals(200, resp.status_code)
        assert_in(self.flag, resp.text)

    def putnoise(self):
        pass

    def getnoise(self):
        # TODO: Could need a little more interaction
        pass

    def havoc(self):
        self.info("I wanted to inform you: I'm  running <3")
        self.http_get("/")  # This will probably fail fail, depending on what params you give the script. :)


app = TeapotChecker.service
if __name__ == "__main__":
    run(TeapotChecker)
