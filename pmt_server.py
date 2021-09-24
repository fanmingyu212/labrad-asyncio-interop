from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
from random import randrange


ON_NEW_COUNT = 397193


class PMTServer(LabradServer):
    name = "pmt_server"
    on_new_count = Signal(ON_NEW_COUNT, "signal: on_new_count", "w")

    def initServer(self):
        self._count = 0
        self._listeners = set()
        self._lc = LoopingCall(self.new_count)
        self._timer = 1.
        self._lc.start(self._timer)

    def initContext(self, c):
        self._listeners.add(c.ID)

    def expireContext(self, c):
        self._listeners.remove(c.ID)

    def get_other_listeners(self, c):
        notified = self._listeners.copy()
        if hasattr(c, "ID") and c.ID in notified:
            notified.remove(c.ID)
        return notified

    def new_count(self, c=None):
        self._count = randrange(100)
        other_listeners = self.get_other_listeners(c)
        self.on_new_count(self._count, other_listeners)

    @setting(0)
    def get_count(self, c):
        return self._count

    @setting(1, timer="v[]")
    def set_timer(self, c, timer=1.):
        self._timer = timer
        self._lc.stop()
        self._lc.start(timer)

    @setting(2, returns="v[]")
    def get_timer(self, c):
        return self._timer


if __name__ == "__main__":
    from labrad import util
    util.runServer(PMTServer())
