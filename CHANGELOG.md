
<a id='changelog-1.1.0'></a>
# 1.1.0 — 2024-01-18

## Added

- `outbox` added to `SveveMockClient` to store a history of sent messages.

## Changed

- `SveveMockClient` now uses successful results for `send_sms` and `remaining_sms` by default.

<a id='changelog-1.0.0'></a>
# 1.0.0 — 2024-01-17

## Added

- `SveveMockClient`: A helper you may wish to use in your unittests (via depedency injection)
- `SveveConsoleClient`: A helper which prints SMSs to console rather than actually sending them.
- Type hints.

## Changed

- Rewritten to return pydantic models rather than dicts.

<a id='changelog-0.1.0'></a>
# 0.1.0 — 2019-10-31

## Added

- Initial release
