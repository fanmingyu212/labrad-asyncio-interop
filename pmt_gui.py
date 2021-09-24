import sys
import asyncio
from twisted.internet import asyncioreactor
from PyQt5 import QtCore, QtGui, QtWidgets
from qasync import QEventLoop, asyncSlot

app = QtWidgets.QApplication(sys.argv)
loop = QEventLoop()  # necessary for PyQt applications
asyncio.set_event_loop(loop)
asyncioreactor.install(loop)  # necessary for asyncio / twisted interop.

import os
from wrappers import connectAsync  # this is modified labrad.wrappers


class PMTGUI(QtWidgets.QWidget):
    """GUI to demonstrate PyQt, asyncio, and labrad interop."""
    def __init__(self, parent=None):
        super().__init__()
        self.init_gui()
        self.init_cxn()

    def init_gui(self):
        grid = QtWidgets.QGridLayout()
        self.setLayout(grid)

        self.lcd = QtWidgets.QLCDNumber()
        grid.addWidget(self.lcd, 0, 0)

        self.timer = QtWidgets.QDoubleSpinBox()
        self.timer.setValue(1.0)
        self.timer.setDecimals(1)
        self.timer.setSingleStep(0.1)
        self.timer.setMaximum(10.0)
        self.timer.setMinimum(0.1)
        self.timer.setKeyboardTracking(False)
        grid.addWidget(self.timer, 1, 0)

    @asyncSlot()
    async def init_cxn(self):
        self.cxn = await connectAsync("127.0.0.1", password=os.environ["LABRADPASSWORD"])
        self.pmt = self.cxn.pmt_server

        await self.setup_cxn_listeners()
        await self.set_gui_initial_values()
        self.setup_gui_listeners()

    @asyncSlot()
    async def set_gui_initial_values(self):
        timer = await self.pmt.get_timer()
        self.timer.setValue(timer)

    @asyncSlot()
    async def setup_cxn_listeners(self):
        NEW_COUNT = 128937
        await self.pmt.signal__on_new_count(NEW_COUNT)
        self.pmt.addListener(listener=self.update_lcd, source=None, ID=NEW_COUNT)

        await self.cxn.manager.subscribe_to_named_message('Server Connect', 9898989, True)
        await self.cxn.manager.subscribe_to_named_message('Server Disconnect', 9898989+1, True)
        self.cxn.manager.addListener(listener=self.server_connect, source=None, ID=9898989)
        self.cxn.manager.addListener(listener=self.server_disconnect, source=None, ID=9898989+1)

    def server_connect(self, cxn, server_name):
        """Sync wrapper. For some reason manager listeners do not work with asyncSlot."""
        async def _server_connect(self, cxn, server_name):
            if server_name[1] == "pmt_server":
                self.setDisabled(False)
                NEW_COUNT = 128937
                await self.pmt.signal__on_new_count(NEW_COUNT)
                self.pmt.addListener(listener=self.update_lcd, source=None, ID=NEW_COUNT)

        asyncio.ensure_future(_server_connect(self, cxn, server_name),
                              loop=asyncio.get_event_loop())

    def server_disconnect(self, cxn, server_name):
        if server_name[1] == "pmt_server":
            self.setDisabled(True)

    def setup_gui_listeners(self):
        self.timer.valueChanged.connect(self.timer_changed)

    @asyncSlot()
    async def timer_changed(self):
        await self.pmt.set_timer(self.timer.value())

    def update_lcd(self, signal, value):
        self.lcd.display(value)


if __name__ == '__main__':
    pmt = PMTGUI()
    pmt.show()
    with loop:
        loop.run_forever()
