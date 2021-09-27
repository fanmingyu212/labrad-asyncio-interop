#!/usr/bin/env python3
import asyncio
import threading
from artiq.applets.simple import SimpleApplet
from PyQt5 import QtWidgets


class PMT(QtWidgets.QLCDNumber):
    def __init__(self, args):
        QtWidgets.QLCDNumber.__init__(self)
        self.setDigitCount(3)
        t = threading.Thread(target=self.worker)
        t.start()

    def worker(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        from twisted.internet import asyncioreactor
        asyncioreactor.install(self.loop)

        self.loop.create_task(self.init_cxn())
        self.loop.run_forever()

    def data_changed(self, data, mods):
        pass

    async def init_cxn(self):
        from pydux.lib.control.clients.connection_asyncio import ConnectionAsyncio
        self.cxn = ConnectionAsyncio()
        await self.cxn.connect()
        self.pmt = self.cxn.get_server("pmt_server")

        await self.set_gui_initial_values()
        await self.setup_cxn_listeners()

    async def set_gui_initial_values(self):
        count = await self.pmt.get_count()
        self.display(count)

    async def setup_cxn_listeners(self):
        NEW_COUNT = 128937
        await self.pmt.signal__on_new_count(NEW_COUNT)
        self.pmt.addListener(listener=self.update_lcd, source=None, ID=NEW_COUNT)

        self.cxn.add_on_connect("pmt_server", self.server_connect)
        self.cxn.add_on_disconnect("pmt_server", self.server_disconnect)

    def server_connect(self):
        async def _server_connect(self):
            self.setDisabled(False)
            NEW_COUNT = 128937
            await self.pmt.signal__on_new_count(NEW_COUNT)
            self.pmt.addListener(listener=self.update_lcd, source=None, ID=NEW_COUNT)

        asyncio.ensure_future(_server_connect(self), loop=self.loop)

    def server_disconnect(self):
        self.setDisabled(True)

    def update_lcd(self, signal, value):
        self.display(value)

    def closeEvent(self, event):
        self.loop.stop()

def main():
    applet = SimpleApplet(PMT)
    applet.run()

if __name__ == "__main__":
    main()
