# labrad-asyncio-interop
Demonstrates interoperation of pylabrad and asyncio

See https://github.com/labrad/pylabrad/issues/378. Tested on python 3.8.

It provides an wrapper that is similar to [labrad.wrappers](https://github.com/labrad/pylabrad/blob/master/labrad/wrappers.py) to convert twisted client to asyncio client.

Run `pmt_server.py` test server on a computer with LabRAD running, and then run `pmt_gui.py` to see a GUI that is based on asyncio. `pmt_async_jupyter.ipynb` tests async pylabrad code in a Jupyter notebook.
