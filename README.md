# Log Normalizer Service
## Overview

This project is a small TCP-based service that accepts log messages, detects their format, and converts them into a normalized structure.

It supports two input types:

- RFC 3164 syslog (including CEF messages)
- JSON logs (Windows Event–style structure)

Each incoming message is parsed and mapped into a consistent schema, then output as a single NDJSON record.


## How it works

The service listens on a TCP port (default: 6000).
For each incoming message:

- Reads one line at a time
- Detects whether it is JSON or syslog
- Parses the input accordingly
- Extracts key fields (timestamp, user, IP, etc.)
- Maps everything into a normalized format
- Prints the result as NDJSON

Format detection is done per line (based on whether the message starts with {), which keeps things simple and works well for mixed inputs.

## Fields extracted

The following fields are normalized:

- @timestamp  
- event.type  
- event.category  
- event.outcome  
- source.ip  
- user.name  
- host.name  
- log.level  
- message  

## Mapping logic

- EventID 4624 → authentication success  
- EventID 4625 → authentication failure  
- EventID 4688 → process start  

For syslog (CEF), fields like `src`, `suser`, and `outcome` are extracted from the extension.

## Project Structure

```
log-normalizer/
├── app/
│   ├── server.py         # TCP server handling connections and input
│   ├── normalizer.py     # parsing and schema mapping logic
│   └── __init__.py
│
├── samples/
│   ├── json/             # sample JSON log files (Windows Event format)
│   └── syslog/           # sample syslog files (RFC 3164 + CEF)
│
├── tests/
│   └── test_normalizer.py  # basic tests for parsing and mapping
│
├── send_file.py            # helper script to send sample logs to server
├── README.md
├── AI_USAGE.md

```

## How to run

### Start the server:

```
python -m app.server
```

The server will start and listen on the configured port (default: 6000).


### Send sample data:

### Input (JSON)
```
python send_file.py samples/json/sample-1.json
```
### Output
```
{"@timestamp":"2026-02-14T14:22:10.8831200Z","event.type":"start","event.category":"authentication","event.outcome":"success","source.ip":"10.0.50.42","user.name":"jsmith","host.name":"dc01.contoso.local","log.level":"info","message":"An account was successfully logged on."}
```

### Input (syslog)
```
python send_file.py samples/syslog/sample-1.log
```
### Output
```
{"@timestamp":"Dec 05 10:30:45","event.type":"start","event.category":"authentication","event.outcome":"success","source.ip":"10.0.50.42","user.name":"jsmith","host.name":"192.168.1.1","log.level":"info","message":"An account was successfully logged on"}
```

## Error handling

The service is designed to keep running even when it receives bad input. If a log line is malformed, such as invalid JSON or an incomplete syslog message, it is skipped instead of crashing the server. This keeps the pipeline simple and resilient during testing.

## Notes

Format detection is done per line, which makes it easy to handle both JSON and syslog inputs without relying on a separate connection for each format. JSON inputs are expected as one object per line, so multi-line sample files are converted into single-line JSON before being sent. The output is written as one normalized JSON record per input line.

## What I would improve with more time

With more time, the next step would be to make the parser more robust for real-world inputs. That would include normalizing syslog timestamps into a standard format, improving CEF parsing for edge cases, adding more unit tests, and making the output destination configurable instead of printing only to stdout.