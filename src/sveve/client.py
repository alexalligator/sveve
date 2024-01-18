import sys
from dataclasses import dataclass, field

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


@dataclass(frozen=True, slots=True)
class SveveConsoleClient:
    stream = sys.stdout
    default_sender: str

    def remaining_sms(self) -> int:
        balance = 1234
        self.stream.write("-" * 79)
        self.stream.write("\n")
        self.stream.write("Printing (fake) remaining SMS to console...")
        self.stream.write("\n")
        self.stream.write(f"... balance: {balance}")
        self.stream.write("\n")
        self.stream.write("-" * 79)
        self.stream.write("\n")
        return balance

    def send_sms(
        self, to: str | list[str], msg: str, sender: str | None = None
    ) -> SveveSendSMSData:
        if isinstance(to, str):
            to = [to]
        if not sender:
            sender = self.default_sender
        self.stream.write("-" * 79)
        self.stream.write("\n")
        self.stream.write("Printing SMS to console...")
        self.stream.write("\n")
        self.stream.write(f"... sender: {sender or self.default_sender}")
        self.stream.write("\n")
        self.stream.write(f"... to: {to}")
        self.stream.write("\n")
        self.stream.write(f"... msg: {msg}")
        self.stream.write("\n")
        self.stream.write("-" * 79)
        self.stream.write("\n")

        num_recipients = len(to)

        return SveveSendSMSData(
            msgOkCount=num_recipients,
            stdSMSCount=num_recipients,
            ids=list(range(num_recipients)),
            errors=None,
        )


@dataclass(frozen=True, slots=True)
class SveveOutboxItem:
    """
    A dataclass representing an item in the SveveMockClient outbox.
    """

    to: str | list[str]
    msg: str
    sender: str
    result: SveveSendSMSData | SveveError


@dataclass
class SveveMockClient:
    """
    A mock implementation of the SveveClient class to help you test your code.
    """

    default_sender: str
    remaining_sms_result: int | SveveError | None = 1
    send_sms_result: SveveSendSMSData | SveveError | None = field(
        default_factory=lambda: SveveSendSMSData(msgOkCount=1, stdSMSCount=1, ids=[1])
    )

    # Store the sent messages in an outbox so that you can inspect them
    outbox: list[SveveOutboxItem] = field(default_factory=list, init=False)

    def remaining_sms(self) -> int:
        """
        Returns the number of remaining SMS messages.
        Raises SveveError if there is an error retrieving the count.
        """
        if self.remaining_sms_result is None:
            raise ValueError(
                "SveveMockClient must be initialised with a 'remaining_sms_result' "
                "if you wish to call the 'remaining_sms()' method."
            )
        if isinstance(self.remaining_sms_result, SveveError):
            raise self.remaining_sms_result
        return self.remaining_sms_result

    def send_sms(
        self, to: str | list[str], msg: str, sender: str | None = None
    ) -> SveveSendSMSData:
        """
        Sends an SMS message.
        Returns the SveveSendSMSData object if successful.
        Raises SveveError if there is an error sending the message.
        """
        if self.send_sms_result is None:
            raise ValueError(
                "SveveMockClient must be initialised with a 'send_sms_result' "
                "if you wish to call the 'send_sms()' method."
            )
        self.outbox.append(
            SveveOutboxItem(
                to=to,
                msg=msg,
                sender=sender or self.default_sender,
                result=self.send_sms_result,
            )
        )
        if isinstance(self.send_sms_result, SveveError):
            raise self.send_sms_result
        return self.send_sms_result
