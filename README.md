# sveve
A (limited) Python wrapper for Sveve's API

Based on [API documentation](https://sveve.no/apidok/send).

I am in no way affiliated with Sveve and accept no liability for damages caused as a result of using this code.

## Usage

The client returns a pydantic class that matches the data structure in the API documentation unless a fatal error occurs, in which case it raises a `SveveError` with a descriptive error message.

### Initialising client
```python
from sveve.client import SveveClient, SveveError
client = SveveClient(user="usr", password="123", default_sender="funbit")
```

### Sending an SMS
```python
try:
  # Sending to one recipient using client's default_sender
  client.send_sms(to="12345678", msg="Hello world!")
except SveveError:
  print("Something went wrong...")

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
except SveveError:
  print("Something went wrong...")
```
