
import json
import re

from datetime import datetime



class LogNormalizer:

    def detect_format(self, line):
        if line.strip().startswith("{"):
            return "json"
        return "syslog"

    def normalize_line(self, line):
        fmt = self.detect_format(line)

        if fmt == "json":
            return self.handle_json(line)
        return self.handle_syslog(line)

    def handle_json(self, line):
        try:
            data = json.loads(line)
        except:
            return None

        system = data.get("System", {})
        event_data = data.get("EventData", {})
        render = data.get("RenderingInfo", {})
        openwec = data.get("OpenWEC", {})

        event_id = system.get("EventID")
        timestamp = system.get("TimeCreated")

        target_user = event_data.get("TargetUserName")
        subject_user = event_data.get("SubjectUserName")

        user = None
        if target_user and target_user != "-":
            user = target_user
        elif subject_user and subject_user != "-":
            user = subject_user

        ip = event_data.get("IpAddress") or openwec.get("IpAddress")
        host = system.get("Computer")
        message = render.get("Message")
        level = render.get("Level")

        if level and str(level).lower() in ["information", "info"]:
            level = "info"
        elif level:
            level = str(level).lower()

        category = "host"
        event_type = "info"
        outcome = "unknown"

        if event_id in [4624, 4625]:
            category = "authentication"
            event_type = "start"
            outcome = "success" if event_id == 4624 else "failure"
        elif event_id == 4688:
            category = "process"
            event_type = "start"
            outcome = "success"
        elif event_id == 4689:
            category = "process"
            event_type = "end"
            outcome = "success"

        result = {
            "@timestamp": timestamp,
            "event.type": event_type,
            "event.category": category,
            "event.outcome": outcome,
            "source.ip": ip,
            "user.name": user,
            "host.name": host,
            "log.level": level,
            "message": message
        }

        return {k: v for k, v in result.items() if v is not None}

    def handle_syslog(self, line):
        syslog_re = r"^<\d+>([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(.*)$"
        match = re.match(syslog_re, line)

        if not match:
            return None

        timestamp = match.group(1)
        host = match.group(2)
        message = match.group(3)

        user = None
        ip = None
        outcome = "unknown"
        category = "host"
        event_type = "info"
        final_message = message

        if message.startswith("CEF:"):
            cef_parts = message.split("|", 7)

            if len(cef_parts) >= 8:
                signature = cef_parts[4]
                cef_name = cef_parts[5]
                extension = cef_parts[7]
                final_message = cef_name

                src_match = re.search(r"src=([^\s]+)", extension)
                suser_match = re.search(r"suser=([^\s]+)", extension)
                outcome_match = re.search(r"outcome=([^\s]+)", extension)
                act_match = re.search(r"act=([^\s]+)", extension)

                if src_match:
                    ip = src_match.group(1)
                if suser_match:
                    user = suser_match.group(1)
                if outcome_match:
                    outcome = outcome_match.group(1)

                act = act_match.group(1) if act_match else ""

                if signature in ["4624", "4625"]:
                    category = "authentication"
                    event_type = "start"
                    outcome = "success" if signature == "4624" else "failure"
                elif signature == "4688":
                    category = "process"
                    event_type = "start"
                    outcome = "success"
                elif signature == "4689":
                    category = "process"
                    event_type = "end"
                    outcome = "success"
                elif "logon" in act.lower():
                    category = "authentication"
                    event_type = "start"

        result = {
            "@timestamp": timestamp,
            "event.type": event_type,
            "event.category": category,
            "event.outcome": outcome,
            "source.ip": ip,
            "user.name": user,
            "host.name": host,
            "log.level": "info",
            "message": final_message
        }

        return {k: v for k, v in result.items() if v is not None}