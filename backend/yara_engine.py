import os
import yara

# Embedded production-grade detection rules
DEFAULT_RULES = """
rule EICAR_Test_File {
    meta:
        description = "Standard EICAR Antivirus Test Signature"
        severity = "CRITICAL"
        threat_type = "test_file"
    strings:
        $eicar = "X5O!P%@AP[4\\\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    condition:
        $eicar
}

rule Suspicious_Webshell_PHP {
    meta:
        description = "Common PHP Web Shell Execution Functions"
        severity = "HIGH"
        threat_type = "webshell"
    strings:
        $php = "<?php" nocase
        $eval = "eval(" nocase
        $base64 = "base64_decode(" nocase
        $system = "system(" nocase
        $passthru = "passthru(" nocase
        $shell_exec = "shell_exec(" nocase
    condition:
        $php and ($eval or $base64) and ($system or $passthru or $shell_exec)
}

rule Suspicious_Powershell_DownloadCradle {
    meta:
        description = "PowerShell In-Memory Download Cradle"
        severity = "CRITICAL"
        threat_type = "dropper"
    strings:
        $ps1 = "Net.WebClient" nocase
        $ps2 = "DownloadString" nocase
        $ps3 = "DownloadFile" nocase
        $ps4 = "IEX" nocase
        $ps5 = "Invoke-Expression" nocase
    condition:
        ($ps1 and ($ps2 or $ps3)) and ($ps4 or $ps5)
}

rule Suspicious_ReverseShell_Payload {
    meta:
        description = "Generic Socket Reverse Shell Commands"
        severity = "CRITICAL"
        threat_type = "reverse_shell"
    strings:
        $sh1 = "/bin/sh -i"
        $sh2 = "/bin/bash -i"
        $py1 = "socket.socket"
        $py2 = "subprocess.call"
        $nc1 = "nc -e /bin/"
    condition:
        $sh1 or $sh2 or ($py1 and $py2) or $nc1
}
"""

try:
    _compiled_rules = yara.compile(source=DEFAULT_RULES)
except Exception as e:
    _compiled_rules = None
    print(f"[!] Error compiling YARA rules: {e}")


def scan_with_yara(file_path: str):
    """
    Scans a file against compiled YARA rules.
    Returns detected rule names, descriptions, and severity.
    """
    if not _compiled_rules:
        return {"matches": [], "error": "YARA rules not initialized"}

    try:
        matches = _compiled_rules.match(file_path)
        matched_rules = []

        for match in matches:
            matched_rules.append({
                "rule": match.rule,
                "meta": match.meta,
                "tags": match.tags,
                "strings": [str(s.identifier) for s in match.strings]
            })

        return {
            "matched": len(matched_rules) > 0,
            "count": len(matched_rules),
            "matches": matched_rules
        }
    except Exception as error:
        return {
            "matched": False,
            "count": 0,
            "error": str(error)
        }