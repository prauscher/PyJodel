#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import re
import json
import hmac
import hashlib
import time
import datetime
import urllib.parse
import requests


class Jodel:
    def __init__(self, uid, location):
        self.api_url = "https://api.go-tellm.com/api/v2"
        self.client_id = "81e8a76e-1e02-4d17-9ba0-8a7020261b26"
        self.client_version = "4.14.1"
        self.api_version = "0.2"
        self.hmac_secret = "jcUwaNNZwTSaMgbEEohXJhncvyIMdnZkFecWfPOU"

        self.uid = uid
        self.location = location

        self.token = None
        self.token_expire = None

    def call(self, method, path, content=None, headers={}, auth=True):
        url = self.api_url + path
        body = "" if content is None else json.dumps(content)
        auth_token = self.get_token() if auth else None
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        hmac = self.calculate_hmac(method, url, auth_token, timestamp, body)

        headers["User-Agent"] = "Jodel/" + self.client_version + " Dalvik/2.1.0 (Linux; U; Android 6.0.1; Find7 Build/MMB29M)"
        headers["X-Timestamp"] = timestamp
        headers["X-Client-Type"] = "android_" + self.client_version
        headers["X-Api-Version"] = self.api_version
        headers["X-Authorization"] = "HMAC " + hmac
        headers["Content-Type"] = "application/json;charset=UTF-8"
        if auth:
            headers["Authorization"] = "Bearer " + auth_token

        return requests.request(method, url, data=body, headers=headers)

    def calculate_hmac(self, method, url, auth_token, timestamp, body):
        auth_token = "" if auth_token is None else auth_token
        url_parsed = urllib.parse.urlparse(url)
        query_list = urllib.parse.parse_qsl(url_parsed.query)
        query_list.sort()
        query = "%".join(key + "%" + value for key, value in query_list)
        port = 443 if url_parsed.port is None else url_parsed.port

        requestKey = method.upper() + "@" + url_parsed.path
        requestValue = method + "%" + url_parsed.hostname + "%" + str(port) + "%" + url_parsed.path + "%" + auth_token + "%" + timestamp + "%" + re.sub('[&=]', '%', url_parsed.query) + "%" + body
        return hmac.new(self.hmac_secret.encode("utf-8"), msg=requestValue.encode("utf-8"), digestmod=hashlib.sha1).hexdigest().upper()

    def has_valid_token(self):
        return self.token is not None and time.time() > self.token_expire

    def get_token(self):
        if not self.has_valid_token():
            self.request_token()
        return self.token

    def request_token(self):
        device_uid = hashlib.sha256(self.uid.encode("utf-8")).hexdigest()
        reply = self.call("POST", "/users/", content={"client_id": self.client_id, "device_uid": device_uid, "location": self.location.export()}, auth=False).json()
        self.token_expire = int(reply["expiration_date"]) + int(reply["expires_in"])
        self.token = reply["access_token"]

    def get_post(self, post_id):
        return self.call("GET", "/posts/" + post_id).json()

    def get_posts(self):
        return self.call("GET", "/posts/").json()["posts"]

    def get_karma(self):
        return self.call("GET", "/users/karma/").json()["karma"]


class Location:
    def __init__(self, country, city, lat, lng):
        self.country = country
        self.city = city
        self.lat = lat
        self.lng = lng

    def export(self):
        return {"loc_accuracy": 19.0, "country": self.country, "city": self.city, "loc_coordinates": {"lat": self.lat, "lng": self.lng}}


if __name__ == "__main__":
    client = Jodel("yolo", Location("DE", "Darmstadt", 49.877538, 8.654353))

#    print(client.get_karma())

#    print(client.get_post("57c9fefcc6dbe096795e56c8"))

#    recent_jodels = client.get_posts()
#    for jodel in recent_jodels:
#        print(jodel)

    current_position = datetime.datetime.now()