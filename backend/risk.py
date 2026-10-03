def calculate_risk(analysis, yara_results=None, vt_results=None):
    score = 0
    reasons = []

    file_type = analysis.get("file_type")
    details = analysis.get("details", {})

    # --- 1. Threat Intelligence: VirusTotal ---
    if vt_results and vt_results.get("enabled"):
        positives = vt_results.get("positives", 0)
        if positives >= 5:
            score += 100
            reasons.append(f"VirusTotal Threat Intel: Flagged by {positives} security engines as MALICIOUS")
        elif positives > 0:
            score += 50
            reasons.append(f"VirusTotal Threat Intel: Flagged by {positives} security engines")

    # --- 2. YARA Signature Detections ---
    if yara_results and yara_results.get("matched"):
        for m in yara_results.get("matches", []):
            rule_name = m["rule"]
            severity = m["meta"].get("severity", "HIGH")
            desc = m["meta"].get("description", rule_name)

            if severity == "CRITICAL" or rule_name == "EICAR_Test_File":
                score += 100
                reasons.append(f"YARA Match: {rule_name} - {desc}")
            elif severity == "HIGH":
                score += 60
                reasons.append(f"YARA Match: {rule_name} - {desc}")
            else:
                score += 30
                reasons.append(f"YARA Match: {rule_name} - {desc}")

    # --- 3. EICAR Fallback ---
    if details.get("eicar_detected") and not any("EICAR" in r for r in reasons):
        score += 100
        reasons.append("EICAR antivirus test signature detected")

    # --- 4. PDF Heuristics ---
    if file_type == "PDF":
        if details.get("obfuscated_stream_found"):
            score += 45
            reasons.append("Obfuscated or compressed JavaScript found inside PDF stream")
        elif details.get("javascript_found"):
            score += 25
            reasons.append("PDF contains JavaScript indicators")

        if details.get("launch_action_found"):
            score += 35
            reasons.append("PDF contains launch action indicators (potential remote code execution)")

        if details.get("embedded_files_found"):
            score += 25
            reasons.append("PDF contains embedded file indicators (potential payload dropper)")

        urls = details.get("urls", [])
        if len(urls) >= 5:
            score += 20
            reasons.append(f"High link density: PDF contains {len(urls)} URLs")

    # --- 5. Image Heuristics ---
    if "Image" in file_type:
        if details.get("appended_payload_detected"):
            entropy = details.get("trailing_entropy", 0.0)
            trailing_size = details.get("trailing_bytes", 0)
            if entropy > 7.0:
                score += 50
                reasons.append(f"High-entropy appended data ({trailing_size} bytes, entropy {entropy}) - possible encrypted payload")
            else:
                score += 30
                reasons.append(f"Trailing data detected after EOF marker ({trailing_size} bytes)")

    # --- 6. Text Files ---
    if file_type == "Text File":
        keywords = details.get("suspicious_keywords", [])
        if keywords:
            score += min(len(keywords) * 15, 45)
            reasons.append("Suspicious keywords: " + ", ".join(keywords))

    # --- 7. Parser Non-conformance ---
    if details.get("parser_error"):
        score += 15
        reasons.append("File parser encountered an error (malformed header or intentional corruption)")

    score = min(score, 100)

    if score >= 75:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"score": score, "level": level, "reasons": reasons}