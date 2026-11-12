#!/usr/bin/env python3
"""iOS 1.1.2 Web Clip profile. No Apple signing needed for this Web Clip.

This is a mobile Safari home-screen web application, not an installable IPA.
On iPhone download profile in Safari; open Settings -> Profile Downloaded ->
Install. Removing the profile removes the icon. Production URLs only.
"""
import plistlib
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
TARGET=ROOT / "NuThanChienDau-GXB3-iOS-1.1.2.mobileconfig"
URL="https://180-93-111-99.sslip.io/?client=ios-webclip&v=1.1.2"
uuid1=str(uuid.uuid4()).upper()
uuid2=str(uuid.uuid4()).upper()

profile={
  "PayloadContent":[{
    "FullScreen":True,
    "IsRemovable":True,
    "Label":"GXB 3 1.1.2",
    "PayloadDescription":"Mo GXB 3 tren may chu VPS",
    "PayloadDisplayName":"GXB 3",
    "PayloadIdentifier":"com.gxb3.alpha.webclip",
    "PayloadOrganization":"GXB 3 ALPHA",
    "PayloadType":"com.apple.webClip.managed",
    "PayloadUUID":uuid1,
    "PayloadVersion":1,
    "URL":URL,
  }],
  "PayloadDescription":"GXB 3 1.1.2: bieu tuong trang chu iOS",
  "PayloadDisplayName":"GXB 3 1.1.2",
  "PayloadIdentifier":"com.gxb3.alpha.webclip.profile",
  "PayloadOrganization":"GXB 3 ALPHA",
  "PayloadRemovalDisallowed":False,
  "PayloadType":"Configuration",
  "PayloadUUID":uuid2,
  "PayloadVersion":1,
}
TARGET.write_bytes(plistlib.dumps(profile,fmt=plistlib.FMT_XML))
print(TARGET)
