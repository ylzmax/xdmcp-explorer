import socket,fcntl
import struct
import time
import gtk,gobject
import threading,Queue
import pygtk
import subprocess as sub
from update import *
import os

Q=Queue.Queue()
def xdmcpbroadcast():
	host=''
	port=6688
	s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
	try:
		s.bind((host,port))
		version=struct.pack('>H',1)
		qureycode=struct.pack('>H',1)
		length=struct.pack('>H',1)
		authcode=struct.pack('b',0)
		sendmess='from max!'
		messlen=struct.pack('>H',len(sendmess))
		packet=version+qureycode+length+authcode+messlen+sendmess
		braddr=getaddress('eth0')
		s.sendto(packet,(braddr,177))
		s.settimeout(2)
		hostdic={}
		while 1:
			try:
				mes,add=s.recvfrom(8192)
				hostname,detail=formathost(mes)
				Q.put((hostname,detail,add[0]))
			except:
				break
		return Q
	except:
		#print 'Socket bind error!'
		messagedialog('Socket bind error !')
	finally:
		s.close()

def getaddress(ifname):
	s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	ip=socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s',ifname[:15]))[20:24])
	mip=ip.split('.')
	mip.pop()
	mip.append('255')
	braddr='.'.join(mip)
	return braddr

def formathost(mes):
	hostlen,=struct.unpack('>H',mes[8:10])	
	hostname=mes[10:10+int(hostlen)]

	detailstart=12+int(hostlen)
	detaillen,=struct.unpack('>H',mes[detailstart:detailstart+2])
	detail=mes[detailstart:detailstart+detaillen]

	return hostname,detail

def checkcmd(cmd):
	path=os.getenv("PATH").split(":")
	for i in path:
		if os.path.isfile(os.path.join(i,cmd)):
			return 1
	return 0

def messagedialog(message,button=gtk.BUTTONS_OK):
	message=gtk.MessageDialog(buttons=button,message_format=message)
	message.run()
	message.destroy()
	
class sprdlogin(gtk.Window):
	def __init__(self):
		super(sprdlogin,self).__init__()
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_size_request(800,500)
		self.set_title('Spreadtrum Unix Login')
		self.connect('destroy',self.quit)

		self.vb=gtk.VBox()

		self.popupmenu_init()

		self.mklist()
		scroll=gtk.ScrolledWindow()
		scroll.add(self.listview)

		self.rebt=gtk.Button('Refresh')
		self.rebt.connect('clicked',self.rebt_clicked)
		self.quitbt=gtk.Button('Quit')
		self.quitbt.connect('clicked',self.quit)
		self.aboutbt=gtk.Button('About')
		self.aboutbt.connect('clicked',self.aboutbt_clicked)

		btbox=gtk.HButtonBox()
		btbox.pack_start(self.aboutbt,False)
		btbox.pack_start(self.rebt,False)
		btbox.pack_start(self.quitbt,False)

		self.toolbar=self.mk_toolbar()

		self.screennum=5
		
		self.updatethread()

		self.vb.pack_start(self.toolbar,False)
		self.vb.pack_start(scroll)
		self.vb.pack_end(btbox,0)
		
		self.add(self.vb)
		self.ftbar=floatbar()
		#self.ftbar.showdesk()
		self.show_all()

		self.bool=1
		self.run_xdmcp()

	def aboutbt_clicked(self,widget):
		aw=gtk.AboutDialog()
		aw.set_version('V1.0')
		aw.set_name('Sprdlogin')
		aw.set_authors(['Lizhuang.Yang@spreadtrum.com'])
		aw.run()
		aw.destroy()


	def run(self):
		gtk.main()

	def quit(self,widget):
		gtk.main_quit()

	def mk_toolbar(self):
		toolbar=gtk.Toolbar()
		
		self.set_size_entry=gtk.Entry(9)
		#self.set_size_entry.set_has_frame(1)
		self.set_size_entry.set_width_chars(10)
		self.set_size_entry.set_text('1680x1050')
		self.set_size_entry.set_sensitive(0)
		#self.set_size_entry.set_overwrite_mode(1)
		
		Tlabel=gtk.Label("ie. 1680x1050")
		self.togglebutton=toolbar.insert_element(gtk.TOOLBAR_CHILD_TOGGLEBUTTON,None,"Fullscreen","Enable/Disable fullscreen","demo",None,None,None,1)
		self.togglebutton.set_active(1)
		self.togglebutton.connect('toggled',self.togglebutton_press)
		toolbar.append_space()
		toolbar.append_widget(self.set_size_entry,"Set screen size","Set screen size")
	#	self.toollabel=toolbar.insert_element(gtk.TOOLBAR_CHILD_WIDGET,Tlabel,"Fullscreen enable","Enable/Disable fullscreen","1680x1050",None,None,None,3)
		toolbar.append_space()
		self.vnc_bt=toolbar.insert_element(gtk.TOOLBAR_CHILD_BUTTON,None,"VNC View","VNC","VNC",None,self.vnc_bt,None,4)
		toolbar.append_space()
		self.rdp_bt=toolbar.insert_element(gtk.TOOLBAR_CHILD_BUTTON,None,"RDP View","RDP","RDP",None,self.RDP_bt,None,6)
		self.fullscreen=True
		return toolbar

	def vnc_bt(self,widget):
		vnc=sub.call(['./3rdtools/vncview'])
	def RDP_bt(self,widget):
		if not checkcmd('remmina'):
			messagedialog('Can`t find remmina ! Please install it first !')	
		rdp=sub.call(['remmina'])
		
			
	
	def togglebutton_press(self,tg):
		if not tg.get_active():
			self.set_size_entry.set_sensitive(1)
			self.fullscreen=False
		else:
			self.set_size_entry.set_sensitive(0)
			self.fullscreen=True
			

	def mklist(self):
		self.listview=gtk.TreeView()

		cell=gtk.CellRendererText()

		hostcol=gtk.TreeViewColumn('ServerName',cell,text=0)
		ipcol=gtk.TreeViewColumn('IP',cell,text=1)
		detailcol=gtk.TreeViewColumn('Detail',cell,text=2)
		statuscol=gtk.TreeViewColumn('Status',cell,text=3)

		hostcol.set_property('clickable',True)
		ipcol.set_property('clickable',True)
		detailcol.set_property('clickable',True)
		hostcol.connect('clicked',self.sortcol)
		ipcol.connect('clicked',self.sortcol)
		detailcol.connect('clicked',self.sortcol)

		self.listview.append_column(hostcol)
		self.listview.append_column(ipcol)
		self.listview.append_column(detailcol)
		self.listview.append_column(statuscol)

		self.liststore=gtk.ListStore(str,str,str,str)

		self.listview.connect('row-activated',self.listview_row_activated)
		self.listview.connect('button_press_event',self.listview_button_press_event)

		self.listview.set_model(self.liststore)
		self.listview.columns_autosize()

	def rebt_clicked(self,widget):
		self.run_xdmcp()
	
	def run_xdmcp(self):
		txdmcp=threading.Thread(target=xdmcpbroadcast)
		txdmcp.start()
		td=threading.Thread(target=self.godis)
		td.start()
		ttime=threading.Thread(target=self.timethread)
		ttime.start()

	def timethread(self):
		time.sleep(2)
		self.bool=0

	def godis(self):
		self.liststore.clear()
		self.bool=1
		while self.bool:
			self.rebt.set_sensitive(0)
			if not Q.empty():
				hostname,detail,ip=Q.get()
				status=''
				self.liststore.append([hostname,ip,detail,status])
		self.rebt.set_sensitive(1)

	def updatethread(self):
		ut=threading.Thread(target=self.updaterun)
		ut.start()

	def updaterun(self):
		if getinfo():
			update(getupdatefile(infodic))
		else:
			print 'No update!'

	def listview_row_activated(self,treeview,path,col):
		model=treeview.get_model()
		ip=model[path][1]
		self.prun(ip)

	def Xnestmenurun(self,menuitem):
		self.prun(self.ip)

	def vncmenurun(self,menuitem):
		self.prun(self.ip)

	def prun(self,ip):
		t=threading.Thread(target=self.cmdinfo,args=(ip,))
		t.setDaemon(True)
		t.start()

	def cmdinfo(self,ip):
		if ip:
			num=self.check(self.screennum)
			if self.fullscreen:
				#xw=xwin()
				#xw.set_size_request(1680,1050)
				#xw.show()
				#xw.fullscreen()
				#xid=xw.xid
				#xw.set_title(ip)
				self.ftbar.w.show_all()
				self.ftbar.initposition()
				cmd=['/usr/bin/Xephyr','-fullscreen','-title',ip,'-once','-query',ip,num]
				xp=sub.Popen(cmd)
			else:
				size=self.set_size_entry.get_text()	
				if  not size:
					size="1680x1050"
				cmd=['/usr/bin/Xephyr','-title',ip,'-once','-query',ip,'-screen',size,num]
				xp=sub.Popen(cmd)


	def check(self,num):
		if os.path.isfile('/tmp/.X%s-lock'%num):
			return self.check(num+1)
		return "".join((":",str(num)))

	def listview_button_press_event(self,treeview,event):
		if event.button == 3:
			pathinfo=treeview.get_path_at_pos(int(event.x),int(event.y))
			if pathinfo:
				path,col,cellx,celly=pathinfo
				model=treeview.get_model()
				self.ip=model[path][1]
				self.status=(model,path)
				self.popupmenu.popup(None,None,None,event.button,event.time)

	def popupmenu_init(self):
		self.popupmenu=gtk.Menu()
		self.vncmenu=gtk.MenuItem('VNC')
		self.vncitmenu=gtk.Menu()
		self.vnccreatemenu=gtk.MenuItem('VNC Create')
		self.vncitmenu.append(self.vnccreatemenu)
		self.vncmenu.set_submenu(self.vncitmenu)
		self.xdmcpmenu=gtk.MenuItem('XDMCP')

		self.popupmenu.append(self.vncmenu)
		self.popupmenu.append(self.xdmcpmenu)
		#self.vncmenu.show()
		#self.vnccreatemenu.show()
		self.xdmcpmenu.show()
		self.xdmcpmenu.connect('activate',self.Xnestmenurun)
		self.vnccreatemenu.connect('activate',self.vncmenurun)

	def sortcol(self,treecol):
		treecol.set_sort_indicator(True)
		treecol.set_sort_column_id(0)
		treecol.set_sort_order(gtk.SORT_ASCENDING)

class floatbar():
	def __init__(self):
		self.w=gtk.Window(gtk.WINDOW_POPUP)
		
		self.w.set_keep_above(1)
		self.w.set_skip_taskbar_hint(False)

		self.w.connect("enter-notify-event",self.w_enter)
		self.w.connect("leave-notify-event",self.w_leave)

		self.ftbar=gtk.Toolbar()
		self.ftbar.set_style(gtk.TOOLBAR_ICONS)
		self.ftbar.insert_space(1)
		self.ft_label=gtk.Label('Conect INfo')	
		self.ftbar.insert_widget(self.ft_label,"Connect Info","Connect Info",2)
		self.ftbar.insert_space(3)
		bt=self.ftbar.insert_stock(gtk.STOCK_LEAVE_FULLSCREEN,"ShowDesktop","ShowDesktop",None,None,4)
		bt.connect('clicked',self.bt_clicked)

		self.w.add(self.ftbar)
		
	def initposition(self,hide=True):
		screen=self.w.get_screen()
		screen_width=screen.get_width()
		screen_height=screen.get_height()

		w_x,w_y=self.w.get_size()

		if hide:
			self.w.move(screen_width/2-w_x/2,5-w_y)
		else:
			self.w.move(screen_width/2-w_x/2,0)

	def w_enter(self,widget,event):
		self.initposition(hide=False)			

	def w_leave(self,widget,event):
		self.initposition(hide=True)

	def showdesk(self):
		import gtk.gdk
		root=gtk.gdk.get_default_root_window()
		for id in root.property_get('_NET_CLIENT_LIST')[2]:
			w=gtk.gdk.window_foreign_new(id)
			if w:
				if '192' in w.property_get("WM_NAME")[2]:
					#print dir(w)
					#w.set_events()
					w.iconify()
	
	def state(self,widget,event):
		print event.new_window_state.value_names
				
	def bt_clicked(self,widget):
		self.showdesk()

class xwin(gtk.Window):
	def __init__(self):
		super(xwin,self).__init__()
		
		self.realize()
		self.xid=self.window.xid
	
		self.connect("window-state-event",self.state_event)

	def state_event(self,widget,event):
		print event.new_window_state.value_names

	def quit(self,widget,subp):
		if subp.wait():
			subp.kill()
		self.destroy()
		
	


if __name__ == '__main__':

	if not checkcmd("Xephyr"):
		messagedialog('Can`t find Xephyr ! Please install it first !')	
		sys.exit()
	gobject.threads_init()
	gtk.gdk.threads_init()
	win=sprdlogin()
	gtk.gdk.threads_enter()
	win.run()
	gtk.gdk.threads_leave()
