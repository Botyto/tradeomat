from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import os
import pickle
import random
import requests
from requests import HTTPError as HttpError
import time
import typing
import urllib.parse


@dataclass
class HttpRequest:
	url: str
	headers: typing.Dict[str, str]

	def hash(self):
		self_parts = [
			self.url,
			*[f"{k}:{v}" for k, v in sorted(self.headers.items()) if k not in ("User-Agent",)],
		]
		return hashlib.md5(" ".join(self_parts).encode("utf-8")).hexdigest()


@dataclass
class HttpResponse:
	url: str
	status_code: int
	status: str
	body: bytes
	encoding: str
	headers: typing.Dict[str, str]
	
	@property
	def text(self):
		return self.body.decode(self.encoding or "utf-8")

	@property
	def success(self):
		return 200 <= self.status_code < 300

	def raise_for_status(self):
		http_error_msg = None
		if 400 <= self.status_code < 500:
			http_error_msg = f"{self.status_code} Client Error: {self.status} for url: {self.url}"
		elif 500 <= self.status_code < 600:
			http_error_msg = f"{self.status_code} Server Error: {self.status} for url: {self.url}"
		if http_error_msg:
			raise HttpError(http_error_msg)

	def json(self):
		return json.loads(self.text)


class HttpClient:
	# thorttle
	throttle_min: timedelta|None = None
	throttle_max: timedelta|None = None
	last_request: datetime|None = None
	# workarounds
	cache: bool = False
	cache_namespace: str = "__httpcache"
	cache_ttl: timedelta|None = None
	user_agents: typing.List[str]|None = None

	def __cache_get(self, cache_path: str):
		if not os.path.isfile(cache_path):
			return
		now = datetime.now()
		ctime = datetime.fromtimestamp(os.path.getctime(cache_path))
		if self.cache_ttl and (now - ctime) > self.cache_ttl:
			os.remove(cache_path)
			return
		with open(cache_path, "rb") as fh:
			return pickle.load(fh)

	def __requests_get(self, request: HttpRequest):
		response = requests.get(request.url, headers=request.headers)
		return HttpResponse(
			response.url,
			response.status_code,
			response.reason,
			response.content,
			response.encoding,
			response.headers,
		)

	def __rand_throttle(self):
		if self.throttle_min:
			if self.throttle_max:
				return random.uniform(self.throttle_min.total_seconds(), self.throttle_max.total_seconds())
			return self.throttle_min.total_seconds()
		elif self.throttle_max:
			return self.throttle_max.total_seconds()
		return 0
	
	def load_user_agents(self, path: str):
		with open(path, "rt", encoding="utf-8") as fh:
			self.user_agents = [l.strip() for l in fh.readlines()]

	def get(self, url: str):
		now = datetime.utcnow()
		if self.throttle_min or self.throttle_max and self.last_request:
			throttle = self.__rand_throttle()
			if (now - self.last_request).total_seconds() < throttle:
				wait_time = throttle - (now - self.last_request).total_seconds()
				time.sleep(wait_time)
		self.last_request = now
		request = HttpRequest(
			url=url,
			headers={},
		)
		request.headers["Referer"] = urllib.parse.urlparse(request.url).netloc
		if self.user_agents:
			request.headers["User-Agent"] = random.choice(self.user_agents)
		cache_path = None
		if self.cache:
			request_hash = request.hash()
			cache_path = os.path.join(self.cache_namespace, request_hash)
			cached_response = self.__cache_get(cache_path)
			if cached_response:
				return cached_response
		impl = self.__requests_get
		response = impl(request)
		if self.cache and response and response.success:
			os.makedirs(self.cache_namespace, exist_ok=True)
			with open(cache_path, "wb") as fh:
				pickle.dump(response, fh)
		return response
