import hashlib
import math
import os
import re

import fitz  # PyMuPDF
from PIL import Image


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        while True:
            data = file.read(4096)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def get_file_signature(file_path):
    with open(file_path, "rb") as file:
        header = file.read(16)
    return header.hex()


def calculate_entropy(data_bytes):
    """Calculates Shannon Entropy (0.0 to 8.0) to detect encrypted/compressed payloads."""
    if not data_bytes:
        return 0.0
    entropy = 0.0
    length = len(data_bytes)
    freq = {}
    for byte in data_bytes:
        freq[byte] = freq.get(byte, 0) + 1
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 2)


def detect_file_type(file_path):
    with open(file_path, "rb") as file:
        header = file.read(16)

    if header.startswith(b"%PDF"):
        return "PDF"
    elif header.startswith(b"\xff\xd8\xff"):
        return "JPEG Image"
    elif header.startswith(b"\x89PNG"):
        return "PNG Image"
    elif header.startswith(b"GIF"):
        return "GIF Image"
    elif header.startswith(b"RIFF"):
        return "RIFF Media"
    elif header[4:8] == b"ftyp":
        return "MP4 / Media"

    try:
        with open(file_path, "rb") as file:
            sample = file.read(4096)
        sample.decode("utf-8")
        return "Text File"
    except UnicodeDecodeError:
        pass

    return "Unknown"


def detect_eicar(file_path):
    eicar_string = (
        "X5O!P%@AP[4\\PZX54(P^)7CC)7}"
        "$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    )
    try:
        with open(file_path, "rb") as file:
            content = file.read()
        text = content.decode("latin-1", errors="ignore")
        if eicar_string in text:
            return {
                "eicar_detected": True,
                "detection_name": "EICAR Test File",
                "message": "EICAR antivirus test signature detected."
            }
    except Exception as error:
        return {"eicar_detected": False, "parser_error": str(error)}
    return {"eicar_detected": False}


def analyze_pdf(file_path):
    results = {
        "javascript_found": False,
        "embedded_files_found": False,
        "launch_action_found": False,
        "urls": [],
        "page_count": 0,
        "suspicious_indicators": [],
        "obfuscated_stream_found": False
    }

    urls_set = set()

    # Pass 1: Raw byte scan
    try:
        with open(file_path, "rb") as file:
            content_lower = file.read().lower()

        if b"/javascript" in content_lower or b"/js" in content_lower:
            results["javascript_found"] = True
            results["suspicious_indicators"].append("JavaScript indicator found")

        if b"/embeddedfile" in content_lower:
            results["embedded_files_found"] = True
            results["suspicious_indicators"].append("Embedded file indicator found")

        if b"/launch" in content_lower:
            results["launch_action_found"] = True
            results["suspicious_indicators"].append("Launch action indicator found")

        found_urls = re.findall(rb"https?://[^\s<>()\"']+", content_lower)
        for u in found_urls:
            urls_set.add(u.decode("latin-1", errors="ignore"))
    except Exception as error:
        results["suspicious_indicators"].append(f"Byte scanner error: {str(error)}")

    # Pass 2: Deep PyMuPDF internal stream and object parsing
    try:
        doc = fitz.open(file_path)
        results["page_count"] = len(doc)

        # Extract URLs declared in native PDF link annotations
        for page in doc:
            for link in page.get_links():
                if "uri" in link and link["uri"]:
                    urls_set.add(link["uri"])

        # Decompress each internal PDF stream to catch obfuscated/compressed scripts
        for xref in range(1, doc.xref_length()):
            try:
                # Read raw stream data decompressed from /FlateDecode
                stream_bytes = doc.xref_stream(xref)
                if stream_bytes:
                    stream_lower = stream_bytes.lower()
                    if (b"/javascript" in stream_lower or b"eval(" in stream_lower or b"app.alert(" in stream_lower):
                        if not results["javascript_found"]:
                            results["javascript_found"] = True
                            results["obfuscated_stream_found"] = True
                            results["suspicious_indicators"].append(
                                f"Hidden/Decompressed JavaScript detected in object stream #{xref}"
                            )
            except Exception:
                # Non-stream objects will raise an exception in xref_stream; skip safely
                continue

        doc.close()
    except Exception as error:
        results["parser_error"] = str(error)

    results["urls"] = list(urls_set)
    return results


def analyze_image(file_path):
    results = {
        "format": None,
        "width": None,
        "height": None,
        "metadata": {},
        "appended_payload_detected": False,
        "trailing_bytes": 0,
        "trailing_entropy": 0.0,
        "suspicious_indicators": []
    }

    # Step A: Image Parsing via Pillow (isolated)
    try:
        with Image.open(file_path) as img:
            results["format"] = img.format
            results["width"] = img.width
            results["height"] = img.height

            if img.info:
                for key, value in img.info.items():
                    k_str = str(key).lower()
                    if k_str in ("icc_profile", "photoshop", "exif"):
                        results["metadata"][str(key)] = f"<{len(str(value))} bytes binary data>"
                    else:
                        val_str = str(value)
                        results["metadata"][str(key)] = val_str[:120] + ("..." if len(val_str) > 120 else "")
    except Exception as error:
        # Non-fatal: Record parser notice, but proceed to boundary inspection
        results["parser_error"] = str(error)

    # Step B: Raw Binary & Boundary Inspection (always executes)
    try:
        with open(file_path, "rb") as f:
            raw_bytes = f.read()

        trailing_data = b""

        # Check JPEG End-of-Image marker (FF D9)
        if raw_bytes.startswith(b"\xff\xd8\xff"):
            eoi_index = raw_bytes.rfind(b"\xff\xd9")
            if eoi_index != -1 and (eoi_index + 2) < len(raw_bytes):
                trailing_data = raw_bytes[eoi_index + 2:]

        # Check PNG End-of-File chunk (IEND + 4 byte CRC)
        elif raw_bytes.startswith(b"\x89PNG"):
            iend_index = raw_bytes.rfind(b"IEND")
            if iend_index != -1 and (iend_index + 8) < len(raw_bytes):
                trailing_data = raw_bytes[iend_index + 8:]

        if trailing_data:
            results["appended_payload_detected"] = True
            results["trailing_bytes"] = len(trailing_data)
            results["trailing_entropy"] = calculate_entropy(trailing_data)

            if trailing_data.startswith(b"PK\x03\x04"):
                results["suspicious_indicators"].append(
                    f"Hidden ZIP archive appended after image EOF ({len(trailing_data)} bytes)"
                )
            elif results["trailing_entropy"] > 7.0:
                results["suspicious_indicators"].append(
                    f"High-entropy appended data detected ({len(trailing_data)} bytes, entropy {results['trailing_entropy']}) - possible encrypted payload or steganography"
                )
            else:
                results["suspicious_indicators"].append(
                    f"Appended trailing data detected after image EOF ({len(trailing_data)} bytes)"
                )
    except Exception as error:
        results["suspicious_indicators"].append(f"Boundary scanner error: {str(error)}")

    return results


def analyze_text(file_path):
    results = {
        "eicar_detected": False,
        "suspicious_keywords": [],
        "urls": [],
        "text_length": 0,
        "suspicious_indicators": []
    }

    try:
        # Cap read to 1 MB to prevent regex freezes
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read(1_000_000)

        results["text_length"] = len(content)

        eicar_result = detect_eicar(file_path)
        if eicar_result.get("eicar_detected"):
            results["eicar_detected"] = True
            results["suspicious_indicators"].append("EICAR antivirus test signature detected")

        urls = re.findall(r"https?://[^\s<>()\"']+", content)
        results["urls"] = list(set(urls))

        suspicious_keywords = [
            "powershell", "cmd.exe", "wscript", "cscript", "rundll32",
            "regsvr32", "javascript:", "base64", "invoke-expression", "downloadstring"
        ]

        content_lower = content.lower()
        for keyword in suspicious_keywords:
            if keyword in content_lower:
                results["suspicious_keywords"].append(keyword)
                results["suspicious_indicators"].append(f"Suspicious keyword found: {keyword}")

    except Exception as error:
        results["parser_error"] = str(error)

    return results


def analyze_file(file_path):
    file_type = detect_file_type(file_path)
    sha256 = calculate_sha256(file_path)
    signature = get_file_signature(file_path)
    file_size = os.path.getsize(file_path)

    analysis = {
        "sha256": sha256,
        "file_type": file_type,
        "signature": signature,
        "file_size": file_size
    }

    if file_type == "PDF":
        analysis["details"] = analyze_pdf(file_path)
    elif "Image" in file_type:
        analysis["details"] = analyze_image(file_path)
    elif file_type == "Text File":
        analysis["details"] = analyze_text(file_path)
    else:
        analysis["details"] = {
            "message": "Basic static analysis completed",
            "eicar_detected": detect_eicar(file_path).get("eicar_detected", False)
        }

    return analysis