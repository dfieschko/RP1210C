@ECHO OFF
ECHO ..............................................................................................
ECHO :                  Welcome to the RP1210.py automatic-ish test suite!                        :
ECHO ..............................................................................................
ECHO : Tests are run roughly in order from more basic to more complex functionality.              :
ECHO : Running these tests requires installation of several adapter drivers,                      :
ECHO : as well as physical possession of some adapters.                                           :
ECHO : A list of adapter drivers can be found in the project's documentation.                     :
ECHO : This is not a fully automated test. These are not continuous-integration tests.            :
ECHO : Some tests rely on adapters being disconnected, while others rely on them being connected. :
ECHO : You will be prompted to connect or disconnect adapters before each relevant step.          :
ECHO ..............................................................................................
ECHO Preparing...
REM ECHO Checking pytest installation...
REM py -m pip install -U -q pytest
REM py -m pip install -U -q pytest-cov
ECHO Preparing test directory...
ECHO Removing old source code from Test directory...
rmdir /s /q Test\OldTests\RP1210
ECHO Copying source code into Test directory...
xcopy /v /s /y /q RP1210 Test\OldTests\RP1210\
cd Test\OldTests
ECHO Done!
ECHO ..............................................................................................
ECHO Disconnect all RP1210 adapters before continuing.
pause
py -m pytest -l -v -ra --tb=long --cov=RP1210 --cov func --cov-branch --cov-report term-missing
pause
