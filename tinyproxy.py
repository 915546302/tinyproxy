#-*- coding: UTF-8 -*-
import socket,select
import sys
import thread
from multiprocessing import Process

class Proxy:
	def __init__(self,soc):
		self.client,_=soc.accept()
		self.target=None
		self.request_url=None
		self.BUFSIZE=4096
		self.method=None
		self.targetHost=None
	def getClientRequest(self):
		request=self.client.recv(self.BUFSIZE)	
		if not request:
			return 
		cn=request.find('\n')
		firstLine=request[:cn]
		print firstLine[:len(firstLine)-9]
		line=firstLine.split()
		self.method=line[0]
		self.targetHost=line[1]
		return request
	def commonMethod(self,request):
		tmp=self.targetHost.split('/')
		net=tmp[0]+'//'+tmp[2]
		request=request.replace(net,'')
		self.getTargetInfo(tmp[2])
		self.target.send(request)
		self.nonblocking()
	def connectMethod(self,request):
		con='HTTP/1.1 200 Connection established\r\nProxy-agent: tinyproxy0.1\r\n\r\n'
		self.client.send(con)
		self.getTargetInfo(self.targetHost)
		self.nonblocking()
	def run(self):
		request=self.getClientRequest()
		if request:
			if self.method in ['GET','POST','PUT',"DELETE",'HAVE']:
				self.commonMethod(request)
			elif self.method=='CONNECT':
				self.connectMethod(request)
	def nonblocking(self,timeout=3):
		inputs=[self.client,self.target]
		while True:
			readable,_,errs=select.select(inputs,[],inputs,timeout)
			if errs:
				break
			for soc in readable:
				data=soc.recv(self.BUFSIZE)
				if data:
					if soc is self.client:
						self.target.send(data)
					elif soc is self.target:
						self.client.send(data)
				else:
					break
		self.client.close()
		self.target.close()
	def getTargetInfo(self,host):
		port=0
		site=None
		if ':' in host:
			tmp=host.split(':')
			site=tmp[0]
			port=int(tmp[1])
		else:
			site=host
			port=80
		try:
			(fam,_,_,_,addr)=socket.getaddrinfo(site,port)[0]
		except Exception as e:
			print e
			return
		self.target=socket.socket(fam)
		self.target.connect(addr)

if __name__=='__main__':
	from multiprocessing import Process
	host = '127.0.0.1' 
	port = 8083
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR , 1)
	server.bind((host,port)) 
	server.listen(5) 
	try:
		while True:
			thread.start_new_thread(Proxy(server).run,())
			# 	p=Process(target=Proxy(server).run,args=())
			# 	p.start()
			#	p.join()
	except KeyboardInterrupt:
		server.close()
		sys.exit(0)
	
		
   
