import base64
import json
import logging
import sys

import requests
from nacl import encoding, public

logging.basicConfig(level=logging.INFO)


class Secret(object):
    API_BASE_URL = "https://api.github.com"
    API_PUBLIC_KEY_URL = "/repos/{owner}/{repo}/actions/secrets/public-key"
    API_SECRET_GET_URL = "/repos/{owner}/{repo}/actions/secrets/{key}"
    API_SECRET_LIST_URL = "/repos/{owner}/{repo}/actions/secrets"
    API_SECRET_UPDATE_URL = "/repos/{owner}/{repo}/actions/secrets/{key}"
    API_SECRET_DELETE_URL = "/repos/{owner}/{repo}/actions/secrets/{key}"

    def __init__(self, owner, repo, token, debug=False):
        """
        Accessing and changing GitHub secrets

        :param owner: str, GitHub owner, e.g. anna-money
        :param repo: str, GitHub repo for owner, e.g. workflow-tools
        :param token: str, GitHub access token with proper rights for secrets
        :param debug: bool, if True set log level to logging.ERROR
        """
        self.owner = owner
        self.repo = repo
        self.user, self.password = self._token_to_basic_auth(token)
        self.loglevel = logging.INFO if debug else logging.NOTSET

    def _token_to_basic_auth(self, token):
        """
        Split token to user and password

        :param token: str
        :return: tuple[str, str]
        """
        try:
            user, auth = token.split(":")
        except ValueError:
            raise ValueError("Invalid token. Expected string of format 'user:password', got {}".format(token))
        else:
            return user, auth

    def _log(self, message, *args, **kwargs):
        logging.log(self.loglevel, message, *args, **kwargs)

    def _base64encode(self, value):
        """

        :param value: byte, encrypted message
        :return: string
        """
        self._log("Use base64 library for Python version: %d.%d", sys.version_info[0], sys.version_info[1])
        if sys.version_info <= (3, 1):
            return base64.encodestring(value).decode("utf-8")
        else:
            return base64.encodebytes(value).decode("utf-8")

    def encrypt(self, public_key, value):
        """
        Encrypt a Unicode string using the public key.

        :param public_key: str
        :param value: str
        :return: str
        """
        public_key_encoded = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key_encoded)
        encrypted = sealed_box.encrypt(value.encode("utf-8"))
        encrypted_string = self._base64encode(encrypted)

        # In Python 3.1+ base64.encodebytes inserts "\n" after every 76 bytes of output and
        # adds a trailing newline character to follow RFC 2045
        # https://docs.python.org/3/library/base64.html#base64.encodebytes
        # To make sure GitHub API accepts payload, remove "\n" from the encrypted value.
        result = encrypted_string.replace("\n", "")
        self._log("Encrypted value %s", result)
        return result

    def _request(self, url_path, method="get", params=None, payload=None, raise_for_error=True):
        """
        Base method for requests

        :param url_path: str, path to the base url
        :param method: str, one of "get", "post", "put", "delete"
        :param params: Optional[dict], GET parameters
        :param payload: Optional[dict], payload
        :return: dict
        """
        request_method = getattr(requests, method, "get")
        url = "{}{}".format(self.API_BASE_URL, url_path)
        data = json.dumps(payload)
        response = request_method(url, auth=(self.user, self.password), data=data, params=params)
        self._log("%s %s %s", method.upper(), response.request.url, response.request.body)
        if raise_for_error:
            response.raise_for_status()
        return response

    def _get_public_key(self):
        url = self.API_PUBLIC_KEY_URL.format(owner=self.owner, repo=self.repo)
        response = self._request(url_path=url)
        return response.json()

    def get(self, key):
        url = self.API_SECRET_GET_URL.format(owner=self.owner, repo=self.repo, key=key)
        response = self._request(url_path=url, raise_for_error=False)
        return self._dump(response.json())

    def _dump(self, data):
        """
        Return a string to be echoed by the script

        :param data: dict to be dumped
        :return: str
        """
        return json.dumps(data)

    def delete(self, key):
        url = self.API_SECRET_DELETE_URL.format(owner=self.owner, repo=self.repo, key=key)
        response = self._request(url_path=url, method="delete", raise_for_error=False)

        if response.status_code == 404:
            message = "No such secret: {}".format(key)
        elif response.status_code == 204:
            message = "Removed secret: {}".format(key)
        else:
            message = response.text
        return self._dump({"message": message})

    def list(self):
        url = self.API_SECRET_LIST_URL.format(owner=self.owner, repo=self.repo)
        response = self._request(url_path=url)
        data = response.json()
        secrets = data["secrets"]
        result = []

        if secrets:
            result = [d["name"] for d in secrets]
        return self._dump(result)

    def update(self, key, value):
        """
        Create or update secret in GitHub repository

        :param key: str
        :param value: str
        :return: str
        """
        url = self.API_SECRET_UPDATE_URL.format(owner=self.owner, repo=self.repo, key=key)
        public_key_data = self._get_public_key()
        encrypted_value = self.encrypt(public_key=public_key_data["key"], value=value)
        payload = {"key_id": public_key_data["key_id"], "encrypted_value": encrypted_value}
        response = self._request(url_path=url, method="put", payload=payload)

        if response.status_code == 201:
            # Oddly enough, even newly created secrets never return 201, but rather return 204
            # GitHub API documentation for secrets is obsolete?
            message = "Secret created"
        elif response.status_code == 204:
            message = "Secret updated"
        else:
            message = "GitHub responded with: {} {}".format(response.status_code, response.text)
        return self._dump({"message": message})
