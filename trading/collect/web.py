import bs4
from datetime import datetime, timedelta
import hashlib
import io
import os
import pickle
import random
import requests
import requests.cookies
from requests import PreparedRequest, Response
import time
import typing


class HttpClient(requests.Session):
	# thorttle
	throttle_min: timedelta|None = None
	throttle_max: timedelta|None = None
	last_request: datetime|None = None
	# workarounds
	cache: bool = False
	cache_namespace: str = "__httpcache"
	cache_ttl: timedelta|None = None
	user_agents: typing.List[str]|None = None

	def __init__(self, load_user_agents: bool = True):
		super().__init__()
		if load_user_agents:
			self.load_user_agents()

	def _cache_get(self, cache_path: str) -> Response|None:
		if not os.path.isfile(cache_path):
			return
		now = datetime.now()
		ctime = datetime.fromtimestamp(os.path.getctime(cache_path))
		if self.cache_ttl and (now - ctime) > self.cache_ttl:
			os.remove(cache_path)
			return
		with open(cache_path, "rb") as fh:
			return pickle.load(fh)
		
	def _cache_set(self, cache_path: str, response: Response):
		assert response.ok
		os.makedirs(os.path.dirname(cache_path), exist_ok=True)
		with open(cache_path, "wb") as fh:
			pickle.dump(response, fh)

	def _cache_hash_req(self, req: PreparedRequest) -> str:
		buffer = io.BytesIO()
		buffer.write(req.method.encode("ascii"))
		buffer.write(req.url.encode("utf-8"))
		return hashlib.sha256(buffer).hexdigest()

	def _rand_throttle(self):
		if self.throttle_min:
			if self.throttle_max:
				return random.uniform(self.throttle_min.total_seconds(), self.throttle_max.total_seconds())
			return self.throttle_min.total_seconds()
		elif self.throttle_max:
			return self.throttle_max.total_seconds()
		return 0
	
	def send(self, prep: PreparedRequest, **kwargs):
		# cache
		cache_path: str|None = None
		if self.cache:
			request_hash = self._cache_hash_req(prep)
			cache_path = os.path.join(self.cache_namespace, request_hash)
			cached_response = self._cache_get(cache_path)
			if cached_response:
				return cached_response
		# throttle
		now = datetime.utcnow()
		if self.throttle_min or self.throttle_max and self.last_request:
			throttle = self._rand_throttle()
			time_passed: timedelta = now - self.last_request
			if time_passed.total_seconds() < throttle:
				wait_time = throttle - time_passed.total_seconds()
				time.sleep(wait_time)
		self.last_request = now
		# assign user agent
		if self.user_agents:
			if "User-Agent" not in prep.headers or "python-requests" in prep.headers["User-Agent"]:
				prep.headers["User-Agent"] = random.choice(self.user_agents)
		# send real request
		response = super().send(prep, **kwargs)
		# cache
		if self.cache and response and response.ok:
			self._cache_set(cache_path, response)
		# finish
		return response

	def load_user_agents(self, path: str|None = None):
		if path is None:
			self.user_agents = get_user_agents()
		else:
			with open(path, "rt", encoding="utf-8") as fh:
				self.user_agents = [l.strip() for l in fh.readlines()]


class UserAgents:
	PATH = os.path.join("data", "web", "useragents.txt")
	LIFETIME = timedelta(days=31)

	client: HttpClient

	def __init__(self):
		self.client = HttpClient(load_user_agents=False)

	def _is_fresh(self):
		if not os.path.isfile(self.PATH):
			return False
		mtime = os.path.getmtime(self.PATH)
		if datetime.now() - datetime.fromtimestamp(mtime) < self.LIFETIME:
			return True

	def _fetch_new(self):
		random_url = "https://user-agents.net/random"
		response = requests.post(random_url, data={"limit": 1000, "action": "generate"})
		response.raise_for_status()
		soup = bs4.BeautifulSoup(response.text, "html.parser")
		return [list_item.text.strip() for list_item in soup.find("section").find("ol").find_all("li")]

	def update(self):
		if self._is_fresh():
			return
		user_agents = self._fetch_new()
		os.makedirs(os.path.dirname(self.PATH), exist_ok=True)
		with open(self.PATH, "wt", encoding="utf-8") as fh:
			fh.writelines(ua + "\n" for ua in user_agents)
		return True

	def load(self):
		self.update()
		with open(self.PATH, "rt", encoding="utf-8") as fh:
			return [l.strip() for l in fh.readlines()]


USER_AGENTS = None
def get_user_agents():
	global USER_AGENTS
	ua = UserAgents()
	if ua.update() or not USER_AGENTS:
		USER_AGENTS = ua.load()
	return USER_AGENTS
