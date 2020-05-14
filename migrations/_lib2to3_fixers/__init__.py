import lib2to3.pgen2.driver
import logging


class Lib2to3LoggingModuleShim(object):
    def getLogger(self):
        return logging.getLogger("lib2to3")


lib2to3.pgen2.driver.logging = Lib2to3LoggingModuleShim()
logging.getLogger("lib2to3").setLevel(logging.WARNING)

from lib2to3.refactor import RefactoringTool  # noqa
