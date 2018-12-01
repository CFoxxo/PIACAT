import requests, json, threading, pickle, string, random
from faker import Faker

# Class for creating accounts.
class CreateAccount:
	global currentproxy

	def __init__(self, name, username, password, email):
		self.session = requests.Session()
		self.name = name
		self.username = username
		self.email = email
		self.password = password
		self.proxies = self.scrape_proxies()
		
		self.headers = {
			"Accept": "*/*",
			"Content-Type": "application/x-www-form-urlencoded",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.5",
			"Host": "www.instagram.com",
			"Referer": "application/x-www-form-urlencoded",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0",
			"X-CSRFToken": "1LzlSm8ACd5UGHEDkDiV9ClJ6l9fFW9A",
			"X-Instagram-AJAX": "a3eb7ccb71df",
			"X-Requested-With": "XMLHttpRequest"
		}
	
	def scrape_proxies(self):
		global currentproxy
		s = requests.Session()
		print("PROXIES -> Getting proxies...")
		
		proxy_providers = ["http://sslproxies24.blogspot.com/feeds/posts/default", "http://proxyserverlist-24.blogspot.com/feeds/posts/default"]
		self.proxies = []

		for provider in proxy_providers:
			r = s.get(url = provider)
			for proxy in r.text.split("&lt;br /&gt;"):
				if not proxy:
					continue
				if (len(proxy) > 21 or len(proxy) < 10) or "span" in proxy:
					continue
				
				self.proxies.append(proxy)
		
		self.proxies = list(set(self.proxies))
		currentproxy = random.choice(self.proxies)
		print(f"PROXIES -> {str(len(self.proxies))} proxies found.")
	
	def create_account(self):
		global currentproxy
		
		data = {
			"email": self.email,
			"first_name": self.name,
			"opt_into_one_tap": "false",
			"password": self.password,
			"seamless_login_enabled": "1",
			"tos_version": "row",
			"username": self.username
		}
		
		proxies = {
			"http": f"http://{currentproxy}",
			"https": f"https://{currentproxy}"
		}
		
		try:
			request = self.session.post(url = 'https://www.instagram.com/accounts/web_create_ajax/', headers=self.headers, data=data)
			response = json.loads(request.text)
			print(f'{self.username} -> {request.text}')
			
			if response["account_created"] == False:
				print(f"{self.username} -> COULDN'T CREATE.")
			else:
				print(f"{self.username} -> SUCCESS! Storing cookies.")
				self.save_cookies()
		except Exception as e:
			print(f"{self.username} -> Something went wrong when trying to create: {e}")
	
	def save_cookies(self):
		try:
			global currentproxy
			pickle.dump(self.session.cookies, open(".\\cookies\\{0.username}.p".format(self), "wb"))
			with open("created-accounts.txt", "ab") as a:
				a.write("{username}:{password}:{email}:{currentproxy}\n")
			print(f"{self.username} -> STORED COOKIES.")
		except Exception as e:
			print(f"{self.username} -> COULD NOT STORE COOKIES! {e}")

if __name__ == "__main__":
	with open("config.json", "r") as config:
		print("START -> Started.")
		config = json.loads(config.read())
		#threads = ThreadManager(MAX_THREADS = int(config[threads])) # threading will come soon, as of now i'm too lazy to get off my ass and do something about it
		
		if config["realistic-usernames"].lower() == "true":
			fake = Faker()
			name = fake.name()
			username = name
			for character in [' ', '\'']:
				username = username.replace(character, '')
			username = username.lower() + str(random.randint(1,99))
		else:
			username = config["username-base"] + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
			name = username
		
		if config["use-random-passwords"].lower() == "true":
			password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
		else:
			password = config['account-passwords']
		
		email = '{}@{}.net'.format(''.join(random.choices(string.ascii_uppercase + string.digits, k=5)), ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))) # i know, inconsistent, but it's a one liner and it looks better.
			
		account = CreateAccount(name, username, password, email)
		account.create_account()
		#threads.load(CreateAccount(name=name, username=username, email=email, password=password))