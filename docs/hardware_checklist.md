# 📋 SentinelEdge: Human Team Hardware Deployment Checklist
## Phase 8 (WP8: Android Phone Deployment) Preparation Guide
*Mandatory verification checklist for student team members prior to flashing and running on physical mobile hardware.*

---

## 1. Target Physical Device Specifications

Before deploying SentinelEdge onto a physical smartphone, verify that the device satisfies these minimum hardware specifications:

| Hardware Attribute | Minimum Requirement | Recommended Specification | Verified Device Details (To Be Filled By Team) |
|:---|:---|:---|:---|
| **Device Model** | Any 64-bit Android Smartphone | Snapdragon 7/8 series, Dimensity 8000+, or Google Tensor | *e.g. OnePlus 11R / Pixel 7a / Galaxy S21* |
| **Processor Architecture** | 64-bit Arm (`arm64-v8a`) | Multi-core Arm Cortex-A78 / A55 or Cortex-X | _____________________________________________ |
| **Operating System** | Android 10 (API Level 29) | Android 13 or Android 14 (API Level 33/34) | _____________________________________________ |
| **Physical RAM** | **4 GB RAM** | **6 GB or 8 GB RAM** | _____________________________________________ |
| **Free Internal Storage**| **2.5 GB free space** | **5.0 GB free space** | _____________________________________________ |
| **USB Interface** | USB 2.0 Type-C | USB 3.1 Gen 1 Type-C (Fast ADB transfer) | _____________________________________________ |

---

## 2. Workstation & Cable Prerequisites

Ensure the following tools and accessories are ready at your workstation:
- [ ] **High-Speed USB-C Cable:** Must be a full data-sync cable (verify your PC detects the phone; charge-only cables will not work with ADB).
- [ ] **Android Platform Tools (ADB):** Installed on your workstation and added to your system `PATH`.
  * *Verification command:* `adb version` (should output `Android Debug Bridge version 1.0.41+`).
- [ ] **Git & Python 3.11:** Active on workstation with SentinelEdge repo cloned and verified (`.\check.ps1` passing).

---

## 3. Step-by-Step Smartphone Setup

Follow these exact steps on your target Android device:

### Step 3.1: Enable Developer Options
1. Open the phone's **Settings** app.
2. Navigate to **About Phone** (or **System > About Phone**).
3. Locate the **Build Number** field.
4. **Tap "Build Number" 7 times rapidly** until a toast notification appears: *"You are now a developer!"*

### Step 3.2: Enable USB Debugging & Device Stability
1. Go back to **Settings > System > Developer Options**.
2. Toggle **ON** the **USB Debugging** switch.
3. Toggle **ON** **Stay Awake** (keeps the screen on while charging to prevent sleep during benchmarks).
4. If using Xiaomi/Redmi (MIUI/HyperOS): Enable **"Install via USB"** and **"USB Debugging (Security Settings)"**.

### Step 3.3: Authorize Workstation via RSA Key
1. Connect the phone to your workstation using your USB-C cable.
2. A popup prompt will appear on the phone screen: **"Allow USB debugging?"**
3. Check the box: **"Always allow from this computer"**, then tap **Allow**.

---

## 4. Workstation ADB Verification Protocol

Run the following terminal commands to verify the device connection and hardware capabilities:

### Test 1: Check Device Recognition
```bash
adb devices
```
*Expected Output:*
```text
List of devices attached
982348a8f102    device
```
*(If it says `unauthorized`, unlock your phone screen and accept the RSA prompt).*

### Test 2: Verify 64-bit Arm Architecture
```bash
adb shell getprop ro.product.cpu.abi
```
*Expected Output:* `arm64-v8a` *(Mandatory for ExecuTorch 64-bit quantized kernels).*

### Test 3: Inspect Available Device RAM
```bash
adb shell "cat /proc/meminfo | grep MemTotal"
```
*Expected Output:* Shows total memory in kB (e.g. `MemTotal: 5982400 kB` indicates ~6 GB RAM).

### Test 4: Inspect Internal Storage Headroom
```bash
adb shell df -h /data
```
*Expected Output:* Shows available storage in `/data` (verify $\ge 2.5\text{ GB}$ available).

---

## 5. Artifact Transfer Protocol (Pushing Models to Device)

Execute the following commands to push the required model binaries into the device application sandbox (`/data/local/tmp/`):

```bash
# Step 1: Create dedicated sandbox directory on device
adb shell mkdir -p /data/local/tmp/sentineledge/models

# Step 2: Push 4-bit Llama 3.2 ExecuTorch model (~750 MB)
adb push models/llama3_2_1b_4bit.pte /data/local/tmp/sentineledge/models/

# Step 3: Push ExecuTorch BPE Tokenizer binary (~4.5 MB)
adb push models/tokenizer.bin /data/local/tmp/sentineledge/models/

# Step 4: Push Classical Detectors (~0.49 MB)
adb push models/url_detector.pkl /data/local/tmp/sentineledge/models/
adb push models/sms_detector.pkl /data/local/tmp/sentineledge/models/
adb push models/network_detector.pkl /data/local/tmp/sentineledge/models/

# Step 5: Verify all files arrived intact on phone
adb shell ls -lh /data/local/tmp/sentineledge/models/
```

---

## 6. Zero-Cloud / Airplane Mode Verification Checklist

To prove 100% offline compliance in front of your tutor:

- [ ] **Step 1:** On the phone, swipe down the notification shade and enable **Airplane Mode**.
- [ ] **Step 2:** Explicitly verify that:
  * **Wi-Fi is OFF**
  * **Mobile Data (5G/4G) is OFF**
  * **Bluetooth is OFF**
- [ ] **Step 3:** Execute the on-device test suite:
  * Feed a test malicious SMS (`"URGENT: SBI account blocked! Update KYC: http://bit.ly/scam"`).
  * Feed a test phishing URL (`"http://192.168.1.55/paypal.com/security.top"`).
  * Feed a test normal conversational message.
- [ ] **Step 4:** Observe real-time output:
  * Detection verdict appears in **< 15 milliseconds**.
  * Llama 3.2 natural language rationale and 3 concrete defensive steps appear on the device screen.
  * MITRE ATT&CK Mobile badge (`T1476` / `T1566.002`) renders.
- [ ] **Step 5 (Video Evidence):** Record a continuous video showing the phone in Airplane Mode executing the demo without cuts.
