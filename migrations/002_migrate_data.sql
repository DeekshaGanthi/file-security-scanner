-- Milestone 4: SQLite to PostgreSQL data migration
-- Generated from the verified SQLite backup
BEGIN;
INSERT INTO scans (id, filename, sha256, file_type, file_size, risk_score, risk_level, created_at) VALUES (1, 'Cruise.pdf', '949443297670a81a9797863a0e54898d013594ba07be0df986a8b9b79a643da7', 'PDF', 92757, 0, 'LOW', '2026-10-03 22:38:13');
INSERT INTO scans (id, filename, sha256, file_type, file_size, risk_score, risk_level, created_at) VALUES (2, 'Complex.pdf', 'a2c875058bc7dd66fca6d4ef08d05dd264d967ba12143581b40b8684dbbdad6d', 'PDF', 80081, 0, 'LOW', '2026-10-03 23:18:45');
INSERT INTO scans (id, filename, sha256, file_type, file_size, risk_score, risk_level, created_at) VALUES (3, 'Complex.jpg', 'edd9a135bdf5abbf6d25bc96873a5c699b2c9d5d4acdf956a38107055ed34a42', 'JPEG Image', 146886, 0, 'LOW', '2026-10-03 23:40:21');
INSERT INTO scans (id, filename, sha256, file_type, file_size, risk_score, risk_level, created_at) VALUES (4, 'Complex.pdf', 'a2c875058bc7dd66fca6d4ef08d05dd264d967ba12143581b40b8684dbbdad6d', 'PDF', 80081, 0, 'LOW', '2026-10-05 04:25:00');
SELECT setval(pg_get_serial_sequence('scans', 'id'), COALESCE((SELECT MAX(id) FROM scans), 1), (SELECT COUNT(*) > 0 FROM scans));
SELECT setval(pg_get_serial_sequence('indicators', 'id'), COALESCE((SELECT MAX(id) FROM indicators), 1), (SELECT COUNT(*) > 0 FROM indicators));
INSERT INTO llm_reports (id, scan_id, model, report, created_at) VALUES (1, 1, 'gemini-3.6-flash', 'SUMMARY:
Static analysis was performed on a single-page PDF document (SHA256: `949443297670a81a9797863a0e54898d013594ba07be0df986a8b9b79a643da7`). The file exhibits standard PDF structure without any active content, embedded scripts, external URLs, or obfuscation techniques.

RISK ASSESSMENT:
- Classification: Clean
- Risk Level: LOW (Risk Score: 0 / 100)
- Threat Analysis: The rule-based static evaluation returned zero risk triggers. Common PDF attack vectors—such as automatic execution via JavaScript, external callouts via URLs, embedded payload files, or `/Launch` actions—are completely absent in this file. Based strictly on the provided evidence, there is no threat detected.

SUSPICIOUS INDICATORS:
- None identified.

RECOMMENDED ACTIONS:
- Allow standard processing/opening of the file as no suspicious elements were detected during static analysis.
- Maintain standard endpoint protection and ensure PDF viewers are updated to the latest secure versions as a general best practice.', '2026-10-03 22:38:57');
INSERT INTO llm_reports (id, scan_id, model, report, created_at) VALUES (2, 2, 'gemini-3.6-flash', 'SUMMARY:
Static security analysis was conducted on a single-page PDF file (SHA256: `a2c875058bc7dd66fca6d4ef08d05dd264d967ba12143581b40b8684dbbdad6d`). The inspection revealed a standard PDF structure without any common malicious components such as embedded scripts, executable payloads, external URLs, or obfuscated streams. Based on the provided static evidence, the file is assessed as **Clean**.

RISK ASSESSMENT:
* **Classification:** Clean
* **Risk Score:** 0 / 100
* **Risk Level:** LOW
* **Analysis:** The file presents no detectable static threat indicators. Key PDF-specific attack vectors—such as automatic launch actions, embedded executable files, JavaScript execution, and external link redirection—are entirely absent. The header signature matches a valid PDF version 1.7 file format.

SUSPICIOUS INDICATORS:
* None.

RECOMMENDED ACTIONS:
* No remediation or blocking actions are required.
* The file is considered safe to open using a standard, up-to-date PDF reader.
* Follow standard security practices by maintaining updated software across all document-viewing applications.', '2026-10-03 23:19:56');
INSERT INTO llm_reports (id, scan_id, model, report, created_at) VALUES (3, 3, 'gemini-3.6-flash', 'SUMMARY:
The analyzed file is a standard JPEG image with the SHA256 hash `edd9a135bdf5abbf6d25bc96873a5c699b2c9d5d4acdf956a38107055ed34a42`. Static analysis confirms valid JPEG file headers (`FF D8 FF E0`), standard image dimensions (1024x559), and standard JFIF metadata. Based on the provided evidence, the file displays no anomalies or malicious indicators and is assessed as **Clean**.

RISK ASSESSMENT:
* **Classification:** Clean
* **Risk Level:** LOW (Score: 0/100)
* **Justification:** Both rule-based heuristics and structural analysis indicate no threats. The file matches standard JPEG formatting without any hidden data, appended payloads, trailing bytes, or elevated entropy at the end of the file structure.

SUSPICIOUS INDICATORS:
* None detected.

RECOMMENDED ACTIONS:
* No remediation or containment action is necessary.
* File can be safely processed or opened using standard image viewers.
* Continue adhering to default organization security controls for incoming media files.', '2026-10-03 23:40:33');
INSERT INTO llm_reports (id, scan_id, model, report, created_at) VALUES (4, 4, 'gemini-3.6-flash', 'SUMMARY:
Static security analysis was conducted on a single-page PDF document (SHA256: `a2c875058bc7dd66fca6d4ef08d05dd264d967ba12143581b40b8684dbbdad6d`). The file possesses a valid PDF signature (`%PDF-1.7`) and exhibits no features typical of malicious PDF documents, such as embedded scripts, executable code, or outbound links.

RISK ASSESSMENT:
**Classification:** Clean  
**Risk Level:** LOW (Score: 0/100)  

The static analysis revealed zero high-risk indicators. Common PDF exploitation mechanisms—including JavaScript execution (`javascript_found: False`), auto-launch actions (`launch_action_found: False`), embedded payloads (`embedded_files_found: False`), and stream obfuscation (`obfuscated_stream_found: False`)—are completely absent.

SUSPICIOUS INDICATORS:
* None identified.

RECOMMENDED ACTIONS:
* No threat response or quarantine is necessary based on the provided static analysis.
* Standard security controls (e.g., keeping PDF readers updated) should be maintained as a routine precaution.', '2026-10-05 04:25:07');
SELECT setval(pg_get_serial_sequence('llm_reports', 'id'), COALESCE((SELECT MAX(id) FROM llm_reports), 1), (SELECT COUNT(*) > 0 FROM llm_reports));
COMMIT;
