from dataclasses import dataclass

import requests
from pydantic import BaseModel


class SveveError(Exception):
    pass


class SveveSendSMSFailure(BaseModel):
    number: str
    message: str


class SveveSendSMSFatalError(BaseModel):
    fatalError: str


class SveveSendSMSData(BaseModel):
    msgOkCount: int
    stdSMSCount: int
    ids: list[int]
    errors: list[SveveSendSMSFailure] | None = None


class SveveSendSMSResponse(BaseModel):
    # Parse as error first, then as success
    response: SveveSendSMSFatalError | SveveSendSMSData


@dataclass(frozen=True, slots=True)
class SveveClient:
    base_url = "https://sveve.no/SMS"
    user: str
    password: str
    default_sender: str

    def remaining_sms(self) -> int:
        """
        Retrieves the number of remaining SMS for the Sveve client.

        Returns:
            int: The number of remaining SMS.

        Raises:
            SveveError: If there is an error retrieving the remaining SMS.
        """
        url = self.base_url + "/AccountAdm"
        try:
            r = requests.get(
                url,
                params={"cmd": "sms_count", "user": self.user, "passwd": self.password},
            )
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SveveError(f"Error getting remaining SMS: {e}")

        try:
            balance = int(r.text)
        except ValueError:
            # In cases such as incorrect credentials, the response is not an integer but a
            # string with an error message (and a 200 status)
            raise SveveError(r.text)
        else:
            return balance

    def send_sms(
        self, to: str | list[str], msg: str, sender: str | None = None
    ) -> SveveSendSMSData:
        """
        Sends an SMS message using the Sveve API.

        Args:
            to (str | list[str]): The recipient(s) of the SMS. Can be a single phone number or a list of phone numbers.
            msg (str): The content of the SMS message.
            sender (str | None, optional): The sender of the SMS. If not provided, the default sender will be used.

        Returns:
            SveveSendSMSData: The response data from the Sveve API. Contains a list of errors if some of the SMS messages failed to send.

        Raises:
            SveveError: If there is an error sending the SMS or if the response indicates a fatal error.

        Usage:
            try:
                client.send_sms(to=["1234567890", "0987654321"], msg="Hello, world!")
            except SveveError as e:
                # Fatal error, no SMSes sent.
        """
        if isinstance(to, list):
            to = ",".join(to)
        if not sender:
            sender = self.default_sender
        url = self.base_url + "/SendMessage"

        try:
            r = requests.post(
                url,
                json={
                    "user": self.user,
                    "passwd": self.password,
                    "to": to,
                    "from": sender,
                    "msg": msg,
                    "f": "json",
                },
            )
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SveveError(f"Error getting remaining SMS: {e}")

        try:
            data = SveveSendSMSResponse.model_validate(r.json())
        except ValueError:
            raise SveveError(
                f"Sveve response does not match documented data structure: {r.text}"
            )

        # If response data structure matches the fatal error case then
        # raise an error rather than return a value.
        if isinstance(data.response, SveveSendSMSFatalError):
            raise SveveError(data.response.fatalError)

        return data.response
