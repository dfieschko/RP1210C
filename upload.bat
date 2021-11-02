@ECHO OFF
ECHO Verifying twine installation...
py -m pip install twine
ECHO Creating source distribution...
python setup.py sdist
ECHO Executing upload...
twine upload dist/*
PAUSE
