import socks
import binascii
import time
import json
import os
import sys

# 115709063 // test
# 79414881 // русский шансон
# 74230986 // чисто рэп
# 58534882 // целуй и знакомься
# 107796898 // кавказ дом родной
# 108667826 // ставим все подряд

#46.182.24.155:2222 - sock сервер

banner = '''										
 _   _ _   __  _   ___     _   _______   _    _ _                 
| | | | | / / | | / | |   | | | | ___ \ | |  | (_)                
| | | | |/ /  | |/ /| |   | | | | |_/ / | |  | |_ _ __   ___ _ __ 
| | | |    \  |    \| |   | | | | ___ \ | |/\| | | '_ \ / _ | '__|
\ \_/ | |\  \ | |\  | |___| |_| | |_/ / \  /\  | | |_) |  __| |   
 \___/\_| \_/ \_| \_\_____/\___/\____/   \/  \/|_| .__/ \___|_|   
                                                 | |              
                                                 |_|             
by dzmuh                                               for 2ch.hk
Source: github.com/dzmuh97/VKClubWiper         '''

class ClubWiper():

	def __init__(self):
		print(banner, end='\n\n')
		self.accs = self.load_accs()
		self.socks = []
		self.rooms = []
		self.romm_data = []
		self.connected = False
		self.clubs = []
		self.proxylist = []
		self.currentroom = ''
		print('Включен ручной режим.\n"h" - вывод справки.', end='\n\n')
		self.loadprx()
		self.roll()

	def loadprx(self):
		file = open(sys.path[0] + '/proxyes.dat', 'r').readlines()
		for q in file:
			pr = q.split(':', 1)
			try:
				self.proxylist.append( [ pr[0], int( pr[1].strip() ) ] )
			except:
				print('Не удалось добавить прокси, array =', q)
		print('Загружено', len(self.proxylist), 'прокси.\n')
		
	def normalprint(self, text):
		return ''.join( [x for x in text if x in r' qwertyuiop[]asdfghjkl;\'zxcvbnm,./`1234567890-=\\~!@#$%^&*()_+|QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'] )
		
	def load_accs(self):
		arr = []
		ac = open(sys.path[0] + '/data.accs', 'r').readlines()
		for q in ac:
			tmp = q.split(':', 2)
			try:
				arr.append( [bytes(tmp[0], 'UTF-8'), bytes(tmp[1], 'UTF-8'), bytes(tmp[2].strip(), 'UTF-8')] )
			except:
				print('Не удалось добавить аккаунт, array =', tmp)
		return arr

	def help(self):
		hlp = '''
		h - вывод справки.
		c - подключение всех аккаунтов
		r - переподключить аккаунты и вернуться в руму
		g - перекатиться в клуб
		m MES - отправить MES в чат
		q - выход
		d - дизлайк
		l - лайк
		L - рога (без репостов и прочей хуйни)
		e - кинуть яйцо
		'''
		print(hlp)

	def flush(self, sock):
		sock.settimeout(0)
		while True:
			try:
				if not sock.recv(1024):
					break
			except Exception as e:
				break
		sock.settimeout(None)
		return 0

	def dec(self, sock):
		MSGLEN = sock.recv(2)
		MSGLEN= int(binascii.hexlify(MSGLEN), 16)
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			try:
				chunk = sock.recv(min(MSGLEN - bytes_recd, 1024))
			except Exception as e:
				break
			chunks.append(chunk)
			bytes_recd += len(chunk)
		data = b''.join(chunks)
		return data.decode()

	def egg(self):
		if not self.connected:
			print('Аккаунты не подключены.')
			return 0
		i = 0
		print('-----')
		for q in self.romm_data:
			i += 1
			print('{:<3} {:<15} {:<15}'.format(i, self.normalprint(q[0]), q[1]))
		print('-----')
		no = int(input('Номер человека >> ')) - 1
		uid = self.romm_data[no][1]
		payload = b'{"type":"send_gift","receiver_id":"'+bytes(uid, 'UTF-8')+b'","gift":"snow"}'
		ms = binascii.unhexlify(format(len(payload), '#06x')[2:]) + payload
		for chunk in self.socks:
			s = chunk[1]
			s.send(ms)

	def lik(self):
		if not self.connected:
			print('Аккаунты не подключены.')
			return 0
		l = binascii.unhexlify('001d') + b'{"vote":"like","type":"vote"}'
		for chunk in self.socks:
			s = chunk[1]
			s.send(l)

	def suplik(self):
		if not self.connected:
			print('Аккаунты не подключены.')
			return 0
		l = binascii.unhexlify('0022') + b'{"vote":"superlike","type":"vote"}'
		for chunk in self.socks:
			s = chunk[1]
			s.send(l)

	def dis(self):
		if not self.connected:
			print('Аккаунты не подключены.')
			return 0
		d = binascii.unhexlify('0020') + b'{"vote":"dislike","type":"vote"}'
		for chunk in self.socks:
			s = chunk[1]
			s.send(d)

	def msg(self, msg):
		if not self.connected:
			print('Аккаунты не подключены.')
			return 0
		payload = b'{"type":"chat","text":"'+bytes(msg, 'UTF-8')+b'"}'
		ms = binascii.unhexlify(format(len(payload), '#06x')[2:]) + payload
		for chank in self.socks:
			s = chank[1]
			s.send(ms)

	def goto(self, curr=''):
		if not self.connected:
			print('Аккаунты не подключены.')
			return 0
		if not self.clubs:
			print('Клубы не загружены.')
			return 0
		if not curr:
			i = 0
			print('-----')
			for q in self.clubs:
				i += 1
				print('{:<3} {:<35} {:<15} {:<3}'.format(i, self.normalprint(q[0]), q[1], q[2]))
			print('-----')
			no = int(input('Номер клуба >> ')) - 1
			club = self.clubs[no][1]
			self.currentroom = club
		else:
			club = curr
		self.romm_data = []
		for chank in self.socks:
			s = chank[1]
			self.flush(s.dup())
			payload = b'{"type":"goto","club_id":"'+bytes(club, 'UTF-8')+b'"}'
			to_club = binascii.unhexlify(format(len(payload), '#06x')[2:]) + payload
			s.send(to_club)
			data = self.dec(s.dup())
			if not self.romm_data:
				h = json.loads(data)
				for q in h['clubbers']:
					self.romm_data.append( [q['name'],  q['id']] )
			if '"id": "'+str(club)+'"' in data:
				print(chank[2], 'перекатился.')
				continue
			elif 'club_banned_still' in data:
				print(chank[2], 'не смог перекатиться.. (бан) | -> exit')
			else:
				print(chank[2], 'не смог перекатиться.. | -> exit', data)
			s.close()
			del self.socks[ self.socks.index(chank) ]

	def conn(self):
		if self.connected:
			print('Аккаунты уже подключены.')
			return 0
		used_prx = []
		for q in self.accs:
			for prxy in self.proxylist: 
				if len(used_prx) == len(self.proxylist):
					print('Прокси кончились..')
					return 0
				if prxy in used_prx:
					continue
				sock = socks.socksocket()
				sock.set_proxy(socks.SOCKS4, prxy[0], prxy[1])
				print('Пробуем подключиться с', prxy[0], ':', prxy[1])
				used_prx.append(prxy)
				try:
					sock.connect(('46.182.24.155', 2222))
					break
				except socks.GeneralProxyError:
					print('Прокси не валидны..')
				except socks.ProxyConnectionError:
					print('Прокси не отвечают..')
			payload = b'{"id":"'+q[0]+b'","age":'+q[1]+b',"type":"login","referrer_type":"user_apps","club_id":"0","auth":"'+q[2]+b'","referrer_id":""}'
			payload = binascii.unhexlify(format(len(payload), '#06x')[2:] ) + payload
			sock.send(payload)
			print(q[0], 'отправил запрос на авторизацию..')
			data = self.dec(sock.dup())
			if data:
				user = json.loads(data)
				uid = user['profile']['id']
				bonus = int(user['daily_bonus'])
				name = user['profile']['name']
				print('------------')
				print('| Профиль:', name)
				print('| ID:', uid)
				print('| Золото:', user['profile']['gold'])
				print('| Ежедневнй бонус:', bonus)
				if not self.clubs:
					data = self.dec(sock.dup())
					clubs = json.loads(data)
					if not 'clubs' in clubs:
						payload = binascii.unhexlify('0015') + b'{"type":"list_clubs"}'
						sock.send(payload) 
						data = self.dec(sock.dup())
						clubs = json.loads(data)
					for q in clubs['clubs']:
						self.clubs.append( [ q['title'], q['id'], q['population'] ] )
				if bonus > 0:
					payload = binascii.unhexlify('001c') + b'{"type":"claim_daily_bonus"}'
					sock.send(payload)
					self.flush(sock.dup())
					print('| > Бонус собран.')
				print('------------')
				self.socks.append([uid, sock, name])
				self.connected = True
				continue
			else:
				print(q[0], 'не смог пройти авторизацию.\n', data)
				sock.close()
				break
		return 0

	def ex(self):
		for q in self.socks:
			q[1].close()

	def reconnect(self):
		self.connected = False
		self.ex()
		self.socks = []
		self.conn()
		if self.currentroom:
			self.goto(self.currentroom)
		
	def roll(self):
		while True:
			char = input('> ')
			if char == 'h':
				self.help()
				continue
			elif char == 'q':
				self.ex()
				exit()
			elif char == 'c':
				self.conn()
				print('Подключено:', len(self.socks))
				continue
			elif char == 'l':
				self.lik()
				continue
			elif char == 'L':
				self.suplik()
				continue
			elif char == 'd':
				self.dis()
				continue
			elif char == 'g':
				self.goto()
				continue
			elif char[0] == 'm':
				m = char.split(' ', 1)[1]
				self.msg(m)
				continue
			elif char == 'e':
				self.egg()
				continue
			elif char == 'r':
				self.reconnect()
				continue

def setup_console(sys_enc="utf-8"):
	import codecs
	try:
		if sys.platform.startswith("win"):
			import ctypes
			enc = "cp%d" % ctypes.windll.kernel32.GetOEMCP()
		else:
			enc = (sys.stdout.encoding if sys.stdout.isatty() else
						sys.stderr.encoding if sys.stderr.isatty() else
							sys.getfilesystemencoding() or sys_enc)
		sys.setdefaultencoding(sys_enc)
		if sys.stdout.isatty() and sys.stdout.encoding != enc:
			sys.stdout = codecs.getwriter(enc)(sys.stdout, 'replace')
		if sys.stderr.isatty() and sys.stderr.encoding != enc:
			sys.stderr = codecs.getwriter(enc)(sys.stderr, 'replace')
	except:
		pass

if __name__ == '__main__':
	setup_console()
	main = ClubWiper()
	exit()


