# Wedding Invitation Sender

Personalizes wedding invitation images with each guest's name and sends them via WhatsApp Web with a custom message.

---

## Files

| File | Purpose |
|---|---|
| `make_invitations.py` | Renders guest names onto the base invitation image |
| `send_invitations.py` | Sends personalized invitations via WhatsApp Web |
| `guests.csv` | Guest list with name, phone, and display name |
| `base_inv.png` | Base invitation image |
| `fonts/GreatVibes.ttf` | Font used for the guest name |
| `invitations/` | Output folder — generated PNGs land here |

---

## Setup

```bash
pip install selenium Pillow
```

Chrome is required. On first run, WhatsApp Web will ask you to scan a QR code. Your login is saved after that, so you only scan once.

---

## guests.csv format

```
name,phone,display_name
Mr. & Mrs. Silva,+94771234567,Silva Family
Dr. Kasun Perera,+94712345678,Kasun
```

- **name** — printed on the invitation image
- **phone** — must include country code (e.g. `+94`)
- **display_name** — used in the message greeting ("Dear ...")

---

## Usage

**Preview only** (generates images and prints messages, nothing is sent):
```bash
python send_invitations.py --dry-run
```

**Send invitations:**
```bash
python send_invitations.py
```

Chrome will open WhatsApp Web. Once it's fully loaded, press **ENTER** in the terminal and the script will send one invitation per guest automatically.

---

## Generate images only

To generate all invitation images without sending:
```bash
python make_invitations.py
```

Names are read from `guests.txt` (one name per line) when `USE_FILE = True`.
