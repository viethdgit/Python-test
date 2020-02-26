import _winreg

def startup_app():
	_KEY =_winreg.HKEY_CURRENT_USER
	_SUBKEY = 'Software\Microsoft\Windows\CurrentVersion\Run'
	_NAMEKEY = 'Unikey'
	_KEYVALUE = 'C:\Program Files\UniKey\UniKeyNT.exe'
	#_KEYTYPE : REG_SZ ; REG_BINARY
	_KEYTYPE = _winreg.REG_SZ
	#-
	try:
		key = _winreg.OpenKey(_KEY,_SUBKEY,0,_winreg.KEY_SET_VALUE)
		_winreg.SetValueEx(key,_NAMEKEY,0,_KEYTYPE,_KEYVALUE) 
		key.Close()
	except:
		print 'Error add regedit key!'
	
if __name__ == "__main__":
	startup_app()
	print 'Done!'
