import sys
from logging import DEBUG, Formatter, StreamHandler, getLogger
import weakref

from . import portfolio, security


class TinyLogging:
    """tiny logger for context class 
    
    Attributes:
        level: int, choose from (debug=10, info=20, warn=30, error=40, critical=50)
    """

    def __init__(self, level=DEBUG):
        """TynyLogging constructor 
        
        Attributes:
            level: int, choose from (debug=10, info=20, warn=30, error=40, critical=50)
        """
        formatter = Formatter("%(asctime)s : %(levelname)s : %(message)s")
        logger = getLogger(__name__)
        sh = StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        logger.setLevel(level)
        self.logger = logger

    def setLevel(self, *args, **kwargs):
        """Set loglevel"""
        self.logger.setLevel(*args, **kwargs)

    def debug(self, string):
        """Debug logging message"""
        self.logger.debug(string)

    def info(self, string):
        """Info logging message"""
        self.logger.info(string)

    def warn(self, string):
        """Wanrn logging message"""
        self.logger.warn(string)

    def error(self, string):
        """Error logging message"""
        self.logger.error(string)

    def critical(self, string):
        """Critical logging message"""
        self.logger.critical(string)


class Context:
    """Context of quantx trades

    Attributes:
        securities:
        logger:
    """

    def __init__(self):
        self.portfolio = weakref.ref(portfolio.Portfolio())
        self.logger = TinyLogging().logger,
        self.cache = weakref.WeakKeyDictionary()
        self.securities = weakref.WeakKeyDictionary()
        self.signals = weakref.WeakKeyDictionary()
        self.localStorage = weakref.WeakKeyDictionary()

    def getSecurity(self, sym):
        """Access to security.

        Args:
            sym: str, symbol of stock.
        """
        return self.securities[sym]

    def configure(self, target="", channels=dict()):
        """Configure context.
        Args:
            target: str, 
            channels: dict, 
        """
        for market_info in channels.values():
            for sym in market_info["symbols"]:
                self.securities[sym] = security.Security(self, sym)

    def regist_signal(self, name, signal):
        """Register signals.

        Args:
            name: str, Name of signal.
            signal: func, Signal function.
        """
        self.signals[name] = signal
