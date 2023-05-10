# Trade-o-mat
Automated trading system

## Installation

### On Windows

1. Install CPython 3.10
2. Create a virtual environment named `venv`
3. Install TA-Lib from source
   - Download TA-Lib source from their [website](http://ta-lib.org/hdr_dw.html)
   - Unzip into `C:\ta-lib`
   - Install Visual Studio 2015+ with `Visual C++`
   - Run `VS2015 x64 Native Tools Command Prompt`
   - Navigate to `C:\ta-lib\c\make\cdr\win32\msvc`
   - Run `nmake`
4. Install TA-Lib-Python
   - Clone `https://github.com/TA-Lib/ta-lib-python`
   - Run `./venv/Scripts/python.exe ta-lib-python/setup.py install`
5. `./venv/Scripts/python.exe -m pip install -r ./trading/requirements.txt`
