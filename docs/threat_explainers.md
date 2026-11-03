# Cyber Threat Vector Explainers

This document provides a concise, plain-language breakdown of the three target cyber threat vectors handled by SentinelEdge, in compliance with **Work Package 1 (WP1)** of the project PRD.

---

## 1. Phishing URLs

### How the Threat Operates
Phishing URLs are crafted web links designed to trick users into visiting malicious, fraudulent web pages that visually impersonate legitimate services (such as banks, email providers, or enterprise single-sign-on portals). Once the victim visits the link, attackers harvest credentials (usernames, passwords, 2FA codes), prompt users to download infostealer malware, or trick them into unauthorized financial transactions.

Common deception tactics include:
* **Typosquatting & Lookalike Domains:** Replacing characters with visually identical or similar characters (e.g., `paypa1.com` instead of `paypal.com`, or unicode homoglyphs like Cyrillic `а` in place of Latin `a`).
* **Subdomain Masking:** Stacking legitimate brand names as subdomains of an attacker-controlled root domain (e.g., `login.microsoft.com.security-verify.top`).
* **URL Shorteners & Open Redirects:** Hiding malicious destinations behind services like `bit.ly` or abusing open redirects on trusted websites to bypass standard filters.
* **Direct IP Addresses:** Bypassing domain name registration entirely by using raw IP addresses in the host portion (e.g., `http://192.168.1.50/login`).

### Core Distinguishing Features (Offline Extraction)
Because our detector operates 100% offline without querying external DNS or visiting the page, it relies purely on static **lexical and statistical features**:
1. **URL Length & Structure:** Phishing URLs frequently have abnormal character lengths and deeply nested directory paths compared to legitimate sites.
2. **Shannon Entropy:** Measures the randomness of characters. Attackers frequently use algorithmically generated domains (DGA) or randomized hash tokens, yielding elevated entropy scores.
3. **Punctuation & Delimiter Count:** Elevated counts of dots (`.`), hyphens (`-`), underscores (`_`), and `@` symbols in the host and path.
4. **Suspicious Top-Level Domains (TLDs):** Free or low-cost TLDs (such as `.xyz`, `.top`, `.tk`, `.buzz`) frequently associated with ephemeral phishing campaigns.
5. **Brand Impersonation Tokens:** Presence of high-value keywords (`secure`, `login`, `banking`, `verify`, `update`) in the domain string when the primary domain is not the legitimate entity.

### Trade-off Analysis: False Positive vs. False Negative
* **False Negative (Missed Threat - Worst Case):** A malicious phishing link is marked as "Safe". The user clicks the link, enters their credentials or session tokens, resulting in full account compromise, identity theft, or ransomware deployment.
* **False Positive (Benign Flagged as Threat):** A legitimate website (such as an internal corporate intranet link or unusual URL query parameter) is flagged as "Phishing". The user is warned or blocked. While causing user friction and alert fatigue, the user's data and credentials remain intact.
* **Design Verdict:** The detector prioritizes high recall (minimizing false negatives) while passing borderline inputs to the Llama explainer to provide contextual nuance rather than a blind block.

---

## 2. Scam SMS (Smishing)

### How the Threat Operates
SMS Phishing ("Smishing") exploits the trusted and personal nature of mobile text messaging. Attackers spoof sender IDs or use unregistered prepaid SIM cards to send urgent messages claiming to be financial institutions, courier services, government agencies, or utility providers. 

Typical attack scenarios include:
* **Fear & Urgency (The "Immediate Action" Trap):** "Your bank account / debit card has been blocked. Complete KYC update immediately within 24 hours to prevent permanent suspension: [link]".
* **Greed & Reward (The Lottery/Job Scam):** "Congratulations! You have been selected for a remote part-time job earning $500/day. Contact WhatsApp now".
* **Delivery Failure:** "Your parcel delivery could not be completed due to an incorrect address. Update delivery details and pay $1 fee: [link]".

The primary goal is to coerce the victim into either clicking a phishing URL, calling a fraudulent call-center number, or replying with one-time authentication passwords (OTPs).

### Core Distinguishing Features (Offline Extraction)
1. **Urgency & Coercive Linguistics:** High frequency of psychological trigger words (`immediate`, `urgent`, `blocked`, `suspended`, `24 hours`, `penalty`, `action required`).
2. **Financial & Action Tokens:** Mentions of `KYC`, `account`, `PAN`, `credit card`, `refund`, `lottery`, `cash prize`.
3. **Embedded Links & Numbers:** Legitimate automated transactional SMS rarely include external shortened links (`bit.ly`, `tinyurl`) alongside urgent demands.
4. **All-Caps & Non-Standard Punctuation:** Excessive exclamation marks (`!!!`), capitalization (`URGENT`), and monetary symbols (`$`, `₹`, `€`).
5. **Sender Identifier Discrepancy:** Legitimate bank messages originate from registered enterprise alpha-headers (e.g., `AD-HDFCBK`), whereas smishing messages often originate from regular 10-digit mobile numbers or unusual spoofed headers.

### Trade-off Analysis: False Positive vs. False Negative
* **False Negative (Missed Scam - Catastrophic):** The user trusts the message, clicks the fraudulent link or shares an OTP with a fake support agent, resulting in immediate unauthorized money transfer or account draining.
* **False Positive (Legitimate SMS Flagged as Scam):** A genuine bank transaction alert, flight confirmation, or one-time password message is flagged as suspicious. The user may hesitate or experience inconvenience.
* **Design Verdict:** Our dual-stage model pairs an ultra-fast TF-IDF / Naive Bayes/Random Forest detector with the Llama 3.2 explainer. If an SMS is flagged, the explainer clearly states: *"Never share your OTP or password. If you are unsure, contact your bank using the official phone number on your physical card."*

---

## 3. Network Intrusion & Flow Anomalies

### How the Threat Operates
Network intrusions represent unauthorized attempts by adversaries to compromise, disrupt, or gain unauthorized access to a device over local Wi-Fi or cellular networks. Attackers typically follow a structured kill chain:
1. **Reconnaissance & Scanning:** Probing the device for open network ports and listening services (e.g., SYN port scans, Nmap sweeps).
2. **Denial of Service (DoS):** Flooding the device or local router with high volumes of garbage packets (SYN flood, UDP flood) to exhaust memory and battery resources.
3. **Brute-Force & Lateral Movement:** Repeatedly attempting dictionary attacks on open management ports (e.g., SSH on port 22 or ADB over Wi-Fi on port 5555).
4. **Command-and-Control (C2) Communication:** Periodic "beaconing" where compromised software communicates outbound to an adversary's remote server.

### Core Distinguishing Features (Offline Extraction)
In a mobile and edge context, inspecting full packet payloads is computationally prohibitive and violates end-to-end encryption (TLS/HTTPS). Therefore, detection focuses on **statistical flow characteristics (bidirectional flow statistics)**:
1. **Flow Duration & Inter-Arrival Time:** Extremely rapid, bursty packet arrivals characteristic of automated port sweeps or DoS floods.
2. **Byte & Packet Count Asymmetry:** Disproportionate ratio between sent and received bytes (e.g., large outbound bursts indicating exfiltration, or massive inbound bytes indicating a flood).
3. **TCP Flag Distributions:** An anomalous ratio of `SYN` packets without completing the three-way handshake (`ACK`), or illegal flag combinations (`FIN-PSH-URG` / Xmas scans).
4. **Target Port Entropy:** Connections distributed across multiple sequential or random high-numbered ports within milliseconds, signaling port scanning.
5. **Connection State History:** High rates of connection rejection (`RST` responses) from local closed ports.

### Trade-off Analysis: False Positive vs. False Negative
* **False Negative (Missed Intrusion - Severe):** An attacker successfully maps open ports or establishes a persistent background session on an exposed debugging port (e.g., ADB), allowing data exfiltration or malware persistence.
* **False Positive (Normal Traffic Flagged as Anomaly):** Background system syncs, torrent traffic, video streaming bursts, or fast web browsing (HTTP/2 multiplexing) get misclassified as a flood or scan. Flagging normal network activity leads to "alert fatigue", causing users to disable the security tool.
* **Design Verdict:** The network detector focuses on well-defined statistical flow deviations and distinguishes benign high-bandwidth streaming (symmetric flows, valid TLS handshakes) from malicious scanning and flood behavior.

---

## Summary Matrix

| Threat Vector | Attack Objective | Primary Extraction Modality | False Negative Impact | False Positive Impact |
|:---|:---|:---|:---|:---|
| **Phishing URL** | Credential & identity theft | Static lexical tokens, Shannon entropy, domain structure | Account takeover, credential loss | Blocked benign browsing, minor user friction |
| **Scam SMS** | Social engineering, OTP theft, bank fraud | NLP text features, urgency linguistics, token analysis | Immediate financial loss | Misclassified genuine alert or transaction notification |
| **Network Intrusion** | Reconnaissance, port scan, DoS, brute force | Bidirectional flow statistics, packet rate, TCP flag metrics | Device compromise, unauthorized remote access | Alert fatigue, potential network throttling |
