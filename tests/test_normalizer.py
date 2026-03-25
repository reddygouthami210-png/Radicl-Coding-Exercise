import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.normalizer import LogNormalizer

n = LogNormalizer()


def test_json_success():
    line = '{"System":{"EventID":4624,"TimeCreated":"2026-02-14T14:22:10Z","Computer":"dc01"},"EventData":{"TargetUserName":"jsmith","IpAddress":"10.0.0.1"},"RenderingInfo":{"Message":"login success","Level":"Information"}}'

    result = n.normalize_line(line)

    assert result["event.outcome"] == "success"
    assert result["user.name"] == "jsmith"


def test_json_failure():
    line = '{"System":{"EventID":4625,"TimeCreated":"2026-02-14T14:22:10Z","Computer":"dc01"},"EventData":{"TargetUserName":"admin","IpAddress":"10.0.0.2"},"RenderingInfo":{"Message":"login failed","Level":"Information"}}'

    result = n.normalize_line(line)

    assert result["event.outcome"] == "failure"


def test_syslog():
    line = "<134>Feb 14 14:22:10 host CEF:0|Test|App|1|4624|Login success|6|src=10.0.0.1 suser=jsmith outcome=success act=logon"

    result = n.normalize_line(line)

    assert result["user.name"] == "jsmith"
    assert result["source.ip"] == "10.0.0.1"
