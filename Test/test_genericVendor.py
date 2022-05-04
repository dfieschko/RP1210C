from ctypes import cdll, create_string_buffer
import pytest
import RP1210, os, configparser
from utilities import RP1210ConfigTestUtility

API_NAMES = ["PEAKRP32", "DLAUSB32", "DGDPA5MA", "NULN2R32", "CMNSI632", "CIL7R32"]
INVALID_API_NAMES = ["empty_api", "invalid_api", "extra_empty_api", "invalid_pd_api"]

# These tests are meant to be run with cwd @ repository's highest-level directory
CWD = os.getcwd()
TEST_FILES_DIRECTORY = CWD + ".\\Test\\test-files"
INI_DIRECTORY = TEST_FILES_DIRECTORY + "\\ini-files"
DLL_DIRECTORY = TEST_FILES_DIRECTORY + "\\dlls"
RP121032_PATH = TEST_FILES_DIRECTORY + "\\RP121032.ini"

# try to get Windows Server to load DLLs w/ GitHub Actions
os.add_dll_directory(DLL_DIRECTORY)
os.add_dll_directory(os.getcwd())
os.environ['PATH'] += os.pathsep + DLL_DIRECTORY
for d in os.environ['path'].split(';'): # overboard
    if os.path.isdir(d):
        os.add_dll_directory(d)

invalid_apis = [] + INVALID_API_NAMES

# Check which APIs are missing dependencies so they can be skipped
for api_name in API_NAMES:
    valid = True
    try:
        ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
        dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
        rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
        if api_name not in invalid_apis:
            valid = rp1210.getAPI().isValid()
    except Exception:
        valid = False
    if not valid:
        invalid_apis.append(api_name)

def test_cwd():
    """Make sure cwd isn't in Test folder."""
    cwd = os.getcwd()
    assert "RP1210" in cwd
    assert "Test" not in cwd

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_api_files_exist(api_name : str):
    """Makes sure all the relevant API files are in test-files directory."""
    assert os.path.exists(TEST_FILES_DIRECTORY)
    assert os.path.exists(INI_DIRECTORY)
    assert os.path.exists(DLL_DIRECTORY)
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    assert os.path.isfile(ini_path)
    assert os.path.isfile(RP121032_PATH)
    if not api_name in invalid_apis:
        assert os.path.isfile(dll_path)
        assert cdll.LoadLibrary(dll_path) != None

def test_getAPINames():
    """
    Test the getAPINames() function with a custom directory.
    
    Also calls getAPINames() with no argument to make sure there isn't an exception.
    """
    RP1210.getAPINames()
    for name in RP1210.getAPINames(RP121032_PATH):
        assert name in API_NAMES

@pytest.mark.parametrize("rp121032_path", ["bork", "bork.ini", 1234, "RP121032", RP121032_PATH + "x"])
def test_getAPINames_invalid(rp121032_path):
    """
    Makes sure we get an exception if we provide an invalid path for getAPINames().
    """
    with pytest.raises(FileNotFoundError):
        RP1210.getAPINames(rp121032_path)

@pytest.mark.parametrize("api_name", argvalues=API_NAMES + INVALID_API_NAMES)
def test_RP1210Config(api_name : str):
    """
    Tests RP1210Config class with all sample files provided in test-files folder.
    """
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    assert rp1210.isValid() == True or api_name in INVALID_API_NAMES
    assert rp1210.getAPIName() == api_name
    utility.verifydata(rp1210.getName, "VendorInformation", "Name", fallback="(Vendor Name Missing)")
    utility.verifydata(rp1210.getAddress1, "VendorInformation", "Address1")
    utility.verifydata(rp1210.getAddress2, "VendorInformation", "Address2")
    utility.verifydata(rp1210.getCity, "VendorInformation", "City")
    utility.verifydata(rp1210.getState, "VendorInformation", "State")
    utility.verifydata(rp1210.getCountry, "VendorInformation", "Country")
    utility.verifydata(rp1210.getPostal, "VendorInformation", "Postal")
    utility.verifydata(rp1210.getTelephone, "VendorInformation", "Telephone")
    utility.verifydata(rp1210.getFax, "VendorInformation", "Fax")
    utility.verifydata(rp1210.getVendorURL, "VendorInformation", "VendorURL")
    utility.verifydata(rp1210.getVersion, "VendorInformation", "Version")
    utility.verifydata(rp1210.autoDetectCapable, "VendorInformation", "AutoDetectCapable", fallback=False)
    utility.verifydata(rp1210.getAutoDetectCapable, "VendorInformation", "AutoDetectCapable", fallback=False)
    utility.verifydata(rp1210.getTimeStampWeight, "VendorInformation", "TimeStampWeight", fallback=1.0)
    utility.verifydata(rp1210.getMessageString, "VendorInformation", "MessageString")
    utility.verifydata(rp1210.getErrorString, "VendorInformation", "ErrorString")
    utility.verifydata(rp1210.getRP1210Version, "VendorInformation", "RP1210")
    utility.verifydata(rp1210.getDebugLevel, "VendorInformation", "DebugLevel", fallback=-1)
    utility.verifydata(rp1210.getDebugFile, "VendorInformation", "DebugFile")
    utility.verifydata(rp1210.getDebugMode, "VendorInformation", "DebugMode", fallback=-1)
    utility.verifydata(rp1210.getDebugFileSize, "VendorInformation", "DebugFileSize", fallback=1024)
    utility.verifydata(rp1210.getNumberOfSessions, "VendorInformation", "NumberOfRTSCTSSessions", fallback=1)
    utility.verifydata(rp1210.getCANAutoBaud, "VendorInformation", "CANAutoBaud", fallback=False)
    utility.verifydata(rp1210.getCANFormatsSupported, "VendorInformation", "CANFormatsSupported")
    utility.verifydata(rp1210.getJ1939FormatsSupported, "VendorInformation", "J1939FormatsSupported")
    utility.verifydata(rp1210.getDeviceIDs, "VendorInformation", "Devices")
    utility.verifydata(rp1210.getProtocolIDs, "VendorInformation", "Protocols")
    assert rp1210.getName() == rp1210.getDescription()
    assert rp1210.getName() in str(rp1210)
    assert rp1210.getCANAutoBaud() == rp1210.autoBaudEnabled()
    assert rp1210.getProtocol() == rp1210.getProtocol("J1939")
    
@pytest.mark.parametrize("api_name", argvalues=API_NAMES + INVALID_API_NAMES)
def test_Devices(api_name : str):
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    deviceIDs = rp1210.getDeviceIDs()
    for id in deviceIDs:
        device = rp1210.getDevice(id)
        utility.verifydevicedata(device.getID, id, "DeviceID", fallback=-1)
        utility.verifydevicedata(device.getDescription, id, "DeviceDescription")
        utility.verifydevicedata(device.getName, id, "DeviceName")
        utility.verifydevicedata(device.getParams, id, "DeviceParams")
        utility.verifydevicedata(device.getMultiJ1939Channels, id, "MultiJ1939Channels", fallback=0)
        utility.verifydevicedata(device.getMultiCANChannels, id, "MultiCANChannels", fallback=0)
        if device.getID() == -1:
            assert "(Invalid Device)" in str(device)
        else:
            assert str(device) == str(device.getID()) + " - " + device.getDescription()
        assert device in rp1210.getDevices()
        with pytest.raises(TypeError):
            assert device != "dingus"

@pytest.mark.parametrize("api_name", argvalues=API_NAMES + INVALID_API_NAMES)
def test_Protocols(api_name : str):
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    protocolIDs = rp1210.getProtocolIDs()
    assert rp1210.getProtocol("test protocol name") is None
    if not api_name in INVALID_API_NAMES:
        assert protocolIDs
    for id in protocolIDs:
        protocol = rp1210.getProtocol(id)
        name = protocol.getString()
        protocolFromString = rp1210.getProtocol(name)
        assert protocolFromString.getString() == name
        assert name in rp1210.getProtocolNames()
        assert rp1210.getProtocol(name).getString() == name
        utility.verifyprotocoldata(protocol.getDescription, id, "ProtocolDescription")
        utility.verifyprotocoldata(protocol.getString, id, "ProtocolString")
        utility.verifyprotocoldata(protocol.getParams, id, "ProtocolParams")
        utility.verifyprotocoldata(protocol.getDevices, id, "Devices")
        utility.verifyprotocoldata(protocol.getSpeed, id, "ProtocolSpeed")
        assert protocol in rp1210.getProtocols()
        with pytest.raises(TypeError):
            assert protocol != "dingus"

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_load_DLL(api_name : str):
    """Loads an API's DLL and checks for validity."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    # try to load it twice, to make sure they don't collide or something
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert rp1210.getAPI().isValid()
    assert rp1210.api.getDLL() != None
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert rp1210.api.loadDLL() != None

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ClientConnect(api_name : str):
    """Tests whether ClientConnect follows expected behavior when disconnected from device."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    deviceID = rp1210.getProtocol("J1939").getDevices()[0]
    clientID = rp1210.api.ClientConnect(deviceID, b"J1939:Baud=Auto")
    assert RP1210.translateErrorCode(clientID) in RP1210.RP1210_ERRORS.values()

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ClientDisconnect(api_name : str):
    """Tests whether ClientDisconnect follows expected behavior when disconnected from device."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    code = rp1210.api.ClientDisconnect(0)
    if code < 0:
        code += 65536
    if api_name == "NULN2R32": # Nexiq drivers can trick computer into thinking it's connected
        assert code == 0 or code >= 128
        return
    assert code >= 128

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ReadVersion(api_name : str):
    """Test RP1210_ReadVersion while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping ReadVersion test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    buff1 = create_string_buffer(16)
    buff2 = create_string_buffer(16)
    buff3 = create_string_buffer(16)
    buff4 = create_string_buffer(16)
    rp1210.api.ReadVersion(buff1, buff2, buff3, buff4)
    assert str(buff1) + str(buff2) + str(buff3) + str(buff4) != ""

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ReadVersionDirect(api_name : str):
    """Test ReadVersionDirect while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping ReadVersionDirect test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    for ver in rp1210.api.ReadVersionDirect():
        assert ver != ""

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ReadDetailedVersion(api_name : str):
    """Test ReadDetailedVersion while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping ReadDetailedVersion test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    buff1 = create_string_buffer(17)
    buff2 = create_string_buffer(17)
    buff3 = create_string_buffer(17)
    ret_val = rp1210.api.ReadDetailedVersion(0, buff1, buff2, buff3)
    assert RP1210.translateErrorCode(ret_val) in ["ERR_DLL_NOT_INITIALIZED", "ERR_HARDWARE_NOT_RESPONDING", "ERR_INVALID_CLIENT_ID"]

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_GetErrorMsg(api_name : str):
    """Test GetErrorMsg while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping GetErrorMsg test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    for code in RP1210.RP1210_ERRORS.keys():
        msg = rp1210.api.GetErrorMsg(code)
        assert msg != ""

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_SendCommand(api_name : str):
    """Test SendCommand while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping SendCommand test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    for command in RP1210.RP1210_COMMANDS:
        assert RP1210.translateErrorCode(rp1210.api.SendCommand(command, 0)) in RP1210.RP1210_ERRORS.values()

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_GetHardwareStatus(api_name : str):
    """Test GetHardwareStatus while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping GetHardwareStatus test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    buffer = create_string_buffer(64)
    ret_val = rp1210.api.GetHardwareStatus(0, buffer, 64)
    if ret_val < 0:
        ret_val += 65536
    assert not buffer.value
    assert ret_val in RP1210.RP1210_ERRORS

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_GetHardwareStatusDirect(api_name : str):
    """Test GetHardwareStatusDirect while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping GetHardwareStatusDirect test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert not rp1210.api.GetHardwareStatusDirect(0).value

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_RemainingFunctions(api_name : str):
    """Tests whether API functions follow expected behavior when disconnected from device."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping 'Remaining Functions' test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    ret_val = rp1210.api.SendMessage(0, b"", 0)
    assert RP1210.translateErrorCode(ret_val) in RP1210.RP1210_ERRORS.values()
    ret_val = rp1210.api.SendMessage(0, b"12345678", 8)
    assert RP1210.translateErrorCode(ret_val) in RP1210.RP1210_ERRORS.values()
    read_array_in = create_string_buffer(256)
    assert rp1210.api.ReadMessage(128, read_array_in, len(read_array_in)) <= 0
    assert not read_array_in.value
    read_array_in = create_string_buffer(64)
    assert rp1210.api.ReadMessage(0, read_array_in) <= 0
    assert not read_array_in.value
    assert not rp1210.api.ReadDirect(0)
    assert rp1210.api.ReadDetailedVersionDirect(0)

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_rp1210client_commands(api_name):
    """Tests RP1210Client command functions when adapter is disconnected."""
    pytest.skip("Tests for RP1210Client are invalid until modular API loading is implemented.")
    # TODO: this is copied from old tests & will need to be updated before use!
    client = RP1210.RP1210Client()
    client.setVendor(api_name)
    assert client.getClientID() == 128
    clientID = client.connect()
    assert clientID in RP1210.RP1210_ERRORS.keys()
    assert clientID == client.getClientID()
    # sampling of simpler commands
    assert client.resetDevice() in RP1210.RP1210_ERRORS.keys()
    assert client.setAllFiltersToPass() in RP1210.RP1210_ERRORS.keys()
    assert client.setAllFiltersToDiscard() in RP1210.RP1210_ERRORS.keys()
    assert client.setEcho(True) in RP1210.RP1210_ERRORS.keys()
    assert client.setMessageReceive(True) in RP1210.RP1210_ERRORS.keys()
    assert client.releaseJ1939Address(0xEE) in RP1210.RP1210_ERRORS.keys()
    assert client.setJ1939FilterType(0) in RP1210.RP1210_ERRORS.keys()
    assert client.setCANFilterType(0) in RP1210.RP1210_ERRORS.keys()
    assert client.setJ1939InterpacketTime(100) in RP1210.RP1210_ERRORS.keys()
    assert client.setMaxErrorMsgSize(100) in RP1210.RP1210_ERRORS.keys()
    assert client.disallowConnections() in RP1210.RP1210_ERRORS.keys()
    assert client.setJ1939Baud(5) in RP1210.RP1210_ERRORS.keys()
    assert client.setBlockingTimeout(20, 30) in RP1210.RP1210_ERRORS.keys()
    assert client.flushBuffers() in RP1210.RP1210_ERRORS.keys()
    assert client.setCANBaud(5) in RP1210.RP1210_ERRORS.keys()
