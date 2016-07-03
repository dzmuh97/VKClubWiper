import socket
import binascii
import random
import time
import json
import signal

# 79414881 // русский шансон
# 74230986 // чисто рэп
# 58534882 // целуй и знакомься
# 107796898 // кавказ дом родной
# 108667826 // ставим все подряд

#46.182.24.155:2222 - sock сервер

banner = '''            _         _                        
 \  / |/   /  |  | | |_)   \    / o ._   _  ._ 
  \/  |\   \_ |_ |_| |_)    \/\/  | |_) (/_ |  
                                    |          
by dzmuh                             for 2ch.hk'''

class ClubWiper():

	def __init__(self):
		print(banner, end='\n\n')
		self.accs = self.load_accs()
		self.socks = []
		self.rooms = []
		self.romm_data = []
		self.connected = False
		self.clubs = []
		print('"h" - вывод справки.', end='\n\n')
		self.roll()

	def load_accs(self):
		arr = [ 
		[ b'ID_аккаунта_1', b'возраст_на_аккаунте', b'auth_key' ],
		[ b'ID_аккаунта_2' , b'возраст_на_аккаунте_2', b'auth_key_2' ],
		]
		return arr

	def help(self):
		hlp = '''
		h - вывод справки.
		c - подключение всех аккаунтов
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
		for q in self.socks:
			sock = q[1]
			while True:
				try:
					with timeout(seconds=1):
						if not sock.recv(1024):
							break
				except Exception as e:
					break

	def dec(self, sock):
		MSGLEN = sock.recv(2)
		MSGLEN= int(binascii.hexlify(MSGLEN), 16)
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			try:
				with timeout(seconds=2):
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
			print('{:<3} {:<15} {:<15}'.format(i, q[0], q[1]))
		print('-----')
		no = int(input('>> ')) - 1
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
			#print(s.recv(1024))

	def goto(self):
		if not self.connected:
			print('Аккаунты не подключены.')
			return 0
		if not self.connected:
			print('Клубы не загружены.')
			return 0
		i = 0
		print('-----')
		for q in self.clubs:
			i += 1
			print('{:<3} {:<50} {:<15} {:<3}'.format(i, q[0], q[1], q[2]))
		print('-----')
		no = int(input('>> ')) - 1
		club = self.clubs[no][1]
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
		for q in self.accs:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.connect(('46.182.24.155', 2222))
			payload = b'{"id":"'+q[0]+b'","age":'+q[1]+b',"type":"login","referrer_type":"user_apps","club_id":"0","auth":"'+q[2]+b'","referrer_id":""}'
			payload = binascii.unhexlify(format(len(payload), '#06x')[2:] ) + payload
			sock.send(payload)
			print(q[0], 'отправил запрос на авторизацию..')
			data = self.dec(sock.dup())
			user = json.loads(data)
			if '"profile":' in data:
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
					for q in clubs['clubs']:
						self.clubs.append( [ q['title'], q['id'], q['population'] ] )
				if bonus > 0:
					payload = binascii.unhexlify('001c') + b'{"type":"claim_daily_bonus"}'
					sock.send(payload)
					self.flush(sock.sup())
					print('| > Бонус собран.')
				print('------------')
				self.socks.append([uid, sock, name])
				continue
			else:
				print(q[0], 'не смог пройти авторизацию.\n', data)
				sock.close()
				break

		self.connected = True
		return 0

	def ex(self):
		for q in self.socks:
			q[1].close()
		exit()

	def roll(self):
		while True:
			char = input('> ')
			if char == 'h':
				self.help()
				continue
			elif char == 'q':
				self.ex()
				continue
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

class timeout:
    def __init__(self, seconds=1, error_message='| recv -> timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

if __name__ == '__main__':
	main = ClubWiper()
	exit()


