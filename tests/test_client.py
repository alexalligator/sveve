import re

import pytest
import requests_mock

from sveve.client import SveveClient, SveveError, SveveSendSMSData, SveveSendSMSFailure

BALANCE_URL = "sveve.no/SMS/AccountAdm"
SEND_URL = "sveve.no/SMS/SendMessage"


def test_send_success():
    "Test call made to correct url and that the response data is unpacked and returned"
    client = SveveClient(user="usr", password="123", default_sender="funbit")

    with requests_mock.mock() as m:
        # Given: Message gets sent successfully and Sveve returns a JSON response
        m.post(
            re.compile(SEND_URL),
            json={
                "response": {
                    "msgOkCount": 1,
                    "stdSMSCount": 1,
                    "ids": [29_828_050],
                }
            },
            status_code=200,
        )
        data = client.send_sms(to="12345678", msg="Hello world!")
        history = m.request_history

    assert data == SveveSendSMSData(
        msgOkCount=1, stdSMSCount=1, ids=[29_828_050], errors=None
    )
    assert len(history) == 1
    api_call = history[0]
    assert api_call.method == "POST"
    assert api_call.json() == {
        "user": "usr",
        "passwd": "123",
        "to": "12345678",
        "from": "funbit",
        "msg": "Hello world!",
        "f": "json",
    }
    assert api_call.url == f"https://{SEND_URL}"


def test_send_to_multiple():
    "Test we can convert a list of recipients to a comma separated string when making call to API"
    client = SveveClient(user="usr", password="123", default_sender="funbit")

    with requests_mock.mock() as m:
        # Given: Message gets sent successfully and Sveve returns a JSON response
        m.post(
            re.compile(SEND_URL),
            json={
                "response": {
                    "msgOkCount": 3,
                    "stdSMSCount": 3,
                    "ids": [1, 2, 3],
                }
            },
            status_code=200,
        )
        client.send_sms(to=["11111111", "22222222", "33333333"], msg="Hello world!")
        history = m.request_history

    assert len(history) == 1
    api_call = history[0]
    assert api_call.json() == {
        "user": "usr",
        "passwd": "123",
        "to": "11111111,22222222,33333333",
        "from": "funbit",
        "msg": "Hello world!",
        "f": "json",
    }
    assert api_call.url == f"https://{SEND_URL}"


def test_send_partial_success():
    "Test when Sveve sends some messages successfully and some fail"
    client = SveveClient(user="usr", password="mypwd", default_sender="funbit")

    with requests_mock.mock() as m:
        m.post(
            re.compile(SEND_URL),
            json={
                "response": {
                    "msgOkCount": 1,
                    "stdSMSCount": 1,
                    "ids": [42824387],
                    "errors": [
                        {
                            "number": "1792873691",
                            "message": "Brukeren har ikke tilgang til å sende meldinger til dette landet",
                        },
                        {
                            "number": "63987654",
                            "message": "Telefonnummeret er ikke et mobilnummer",
                        },
                    ],
                }
            },
            status_code=200,
        )

        data = client.send_sms(
            to=["123456789", "1792873691", "63987654"], msg="Hello world!"
        )
        assert data == SveveSendSMSData(
            msgOkCount=1,
            stdSMSCount=1,
            ids=[42824387],
            errors=[
                SveveSendSMSFailure(
                    number="1792873691",
                    message="Brukeren har ikke tilgang til å sende meldinger til dette landet",
                ),
                SveveSendSMSFailure(
                    number="63987654", message="Telefonnummeret er ikke et mobilnummer"
                ),
            ],
        )


def test_send_fatal_error():
    "Test that a Sveve fatalError message is converted to a requests exception"
    client = SveveClient(user="usr", password="wrong", default_sender="funbit")

    with requests_mock.mock() as m:
        m.post(
            re.compile(SEND_URL),
            json={
                "response": {
                    "msgOkCount": 0,
                    "stdSMSCount": 0,
                    "fatalError": "Feil brukernavn/passord",
                    "ids": [],
                }
            },
            status_code=200,
        )
        with pytest.raises(SveveError) as error:
            client.send_sms(to="12345678", msg="Hello world!")
        assert str(error.value) == "Feil brukernavn/passord"


def test_send__returns_invalid_response():
    "Test Sveve returning an undocumented response"
    client = SveveClient(user="usr", password="wrong", default_sender="funbit")

    with requests_mock.mock() as m:
        m.post(
            re.compile(SEND_URL),
            json={"response": ["some weird response"]},
            status_code=200,
        )
        with pytest.raises(SveveError) as error:
            client.send_sms(to="12345678", msg="Hello world!")
        assert (
            str(error.value)
            == """Sveve response does not match documented data structure: {"response": ["some weird response"]}"""
        )


def test_remaining_sms_success():
    "Test call made to correct url and that the response data is unpacked and returned"
    client = SveveClient(user="usr", password="123", default_sender="funbit")

    with requests_mock.mock() as m:
        expect_balance = 1601
        m.get(re.compile(BALANCE_URL), text="1601", status_code=200)
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
        with pytest.raises(SveveError) as error:
            client.remaining_sms()
        assert str(error.value) == error_msg
