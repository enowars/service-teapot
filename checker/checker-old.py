#!/usr/bin/env python
from enolib import BaseChecker, BrokenServiceException, OfflineException, assert_equals, assert_in
import random
import sys


class CoffeepotChecker(BaseChecker):
    def gen_amount(self):
        return random.randrange(0, 10 ** 6)

    def gen_pot(self):
        return random.randrange(10 ** 31, 10 ** 32)

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

    def store_flag(self):  # type: () -> None
        """
            This method stores a flag in the service.
            In case multiple flags are provided, self.call_idx gives the appropriate index.
            The flag itself can be retrieved from self.flag.
            On error, raise an Eno Exception.
            :raises EnoException on error
            :return this function can return a result if it wants
                    if nothing is returned, the service status is considered okay.
                    the preferred way to report errors in the service is by raising an appropriate enoexception
        """
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

    def retrieve_flag(self):  # type: () -> Noneassert_equals
        """
        This method retrieves a flag from the service.
        Use self.flag to get the flag that needs to be recovered and self.roudn to get the round the flag was placed in.
        On error, raise an EnoException.
        :raises EnoException on error
        :return this function can return a result if it wants
                if nothing is returned, the service status is considered okay.
                the preferred way to report errors in the service is by raising an appropriate enoexception
        """
        pot = self.team_db[self.flag]
        resp = self.http("PROPFIND", "/pot-%s" % (pot))
        assert_equals(200, resp.status_code)
        assert_in(self.flag, resp.text)

    def store_noise(self):  # type: () -> None
        """
        This method stores noise in the service. The noise should later be recoverable.
        The difference between noise and flag is, tht noise does not have to remain secret for other teams.
        This method can be called many times per round. Check how often using self.call_idx.
        On error, raise an EnoException.
        :raises EnoException on error
        :return this function can return a result if it wants
                if nothing is returned, the service status is considered okay.
                the preferred way to report errors in the service is by raising an appropriate enoexception
        """
        self.team_db["noise"] = self.noise

    def retrieve_noise(self):  # type: () -> None
        """
        This method retrieves noise in the service.
        The noise to be retrieved is inside self.flag
        The difference between noise and flag is, tht noise does not have to remain secret for other teams.
        This method can be called many times per round. Check how often using call_idx.
        On error, raise an EnoException.
        :raises EnoException on error
        :return this function can return a result if it wants
                if nothing is returned, the service status is considered okay.
                the preferred way to report errors in the service is by raising an appropriate enoexception
        """
        try:
            assert_equals(self.team_db["noise"], self.noise)
        except KeyError:
            raise BrokenServiceException("Noise not found!")

    def havoc(self):  # type: () -> None
        """
        This method unleashes havoc on the app -> Do whatever you must to prove the service still works. Or not.
        On error, raise an EnoException.
        :raises EnoException on Error
        :return This function can return a result if it wants
                If nothing is returned, the service status is considered okay.
                The preferred way to report Errors in the service is by raising an appropriate EnoException
        """
        self.info("I wanted to inform you: I'm  running <3")
        self.http_get("/")  # This will probably fail fail, depending on what params you give the script. :)


if __name__ == "__main__":
    # Example params could be: [StoreFlag localhost ENOFLAG 1 ENOFLAG 50 3]
    exit(CoffeepotChecker(port=3255).run())
