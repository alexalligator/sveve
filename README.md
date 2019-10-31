# sveve
A (limited) Python wrapper for Sveve's API

Based on [API documentation](https://www.sveve.no/sms-api.jsp).

I am in no way affiliated with Sveve and accept no liability for damages caused as a result of using this code.

## Usage

The client attempts to convert any error messages returned by Sveve to `HTTPExceptions` from the `requests` library.

### Initialising client
```python
from sveve.client import SveveClient
client = SveveClient(user="usr", password="123", default_sender="funbit")
```

### Sending an SMS
```python
try:
  # Sending to one recipient using client's default_sender
  delivery_report = client.send_sms(to="12345678", msg="Hello world!")
except Exception:
  print("Something went wrong...")
else:
  print(delivery_report)

# Alternatively with multiple recipients
recipients = ["12345001", "12345002", "12345003"]
client.send_sms(to=recipients, msg="Hello world!")
# Or using a custom sender name
client.send_sms(to="12345678", msg="Hello world!", sender="Your Name")
```

### Checking remaining balance
```python
try:
  balance = client.remaining_sms()
except Exception:
  print("Something went wrong...")
else:
  print(f"You have {balance} messages remaining.")

# Alternatively with multiple recipients
recipients = ["12345001", "12345002", "12345003"]
client.send_sms(to=recipients, msg="Hello world!")
# Or using a custom sender name
client.send_sms(to="12345678", msg="Hello world!", sender="Your Name")
```
