import re
import requests

import pytest

import requests_mock
from sveve.client import SveveClient


BALANCE_URL = "sveve.no/SMS/AccountAdm"
SEND_URL = "sveve.no/SMS/SendMessage"


def test_send_success():
    "Test call made to correct url and that the response data is unpacked and returned"
    client = SveveClient(user="usr", password="123", default_sender="funbit")

    with requests_mock.mock() as m:
        expect_data = {"msgOkCount": 1, "stdSMSCount": 1, "ids": [29_828_050]}
        m.get(re.compile(SEND_URL), json={"response": expect_data}, status_code=200)
        data = client.send_sms(to="12345678", msg="Hello world!")
        history = m.request_history

    assert data == expect_data
    assert len(history) == 1
    actual_url = history[0].url
    assert actual_url == (
        f"https://{SEND_URL}"
        "?user=usr&passwd=123&to=12345678&"
        "from=funbit&msg=Hello+world%21&f=json"
    )


def test_send_fatal_error():
    "Test that a Sveve fatalError message is converted to a requests exception"
    client = SveveClient(user="usr", password="wrong", default_sender="funbit")

    with requests_mock.mock() as m:
        error_msg = "Feil brukernavn/passord"
        m.get(
            re.compile(SEND_URL),
            json={
                "response": {
                    "msgOkCount": 0,
                    "stdSMSCount": 0,
                    "fatalError": error_msg,
                    "ids": [],
                }
            },
            status_code=200,
        )
        with pytest.raises(requests.exceptions.HTTPError) as error:
            client.send_sms(to="12345678", msg="Hello world!")
        assert str(error.value) == error_msg


def test_remaining_sms_success():
    "Test call made to correct url and that the response data is unpacked and returned"
    client = SveveClient(user="usr", password="123", default_sender="funbit")

    with requests_mock.mock() as m:
        expect_balance = 1601
        m.get(re.compile(BALANCE_URL), text=f"{expect_balance}", status_code=200)
        balance = client.remaining_sms()
        history = m.request_history

    assert balance == expect_balance
    assert len(history) == 1
    actual_url = history[0].url
    assert actual_url == (f"https://{BALANCE_URL}?cmd=sms_count&user=usr&passwd=123")


def test_remaining_sms_error():
    "Test that a Sveve fatalError message is converted to a requests exception"
    client = SveveClient(user="usr", password="wrong", default_sender="funbit")

    with requests_mock.mock() as m:
        error_msg = "Feil brukernavn/passord"
        m.get(re.compile(BALANCE_URL), text=error_msg, status_code=200)
        with pytest.raises(requests.exceptions.HTTPError) as error:
            client.remaining_sms()
        assert str(error.value) == error_msg
