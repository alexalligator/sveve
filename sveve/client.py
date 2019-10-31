import requests


class SveveClient:

    base_url = "https://sveve.no/SMS"

    def __init__(self, user, password, default_sender):
        self.user = user
        self.password = password
        self.default_sender = default_sender

    def remaining_sms(self):
        url = self.base_url + "/AccountAdm"
        payload = {"cmd": "sms_count", "user": self.user, "passwd": self.password}
        r = requests.get(url, payload)
        r.raise_for_status()
        try:
            balance = int(r.text)
        except ValueError:
            raise requests.exceptions.HTTPError(r.text)
        else:
            return balance

    def send_sms(self, to, msg, sender=None):
        if isinstance(to, list):
            to = ",".join(to)
        if not sender:
            sender = self.default_sender
        url = self.base_url + "/SendMessage"
        payload = {
            "user": self.user,
            "passwd": self.password,
            "to": to,
            "from": sender,
            "msg": msg,
            "f": "json",
        }
        r = requests.get(url, payload)
        r.raise_for_status()
        data = r.json()["response"]
        if "fatalError" in data:
            raise requests.exceptions.HTTPError(data["fatalError"])
        return data
