# GXB3 Social Voice
Dedicated LiveKit 1.13.11 SFU, audio only; no recordings or media storage.
Service: gxb3-voice.service, config /etc/gxb3-voice/livekit.yaml,
credentials /etc/gxb3-voice/credentials.json (root:gxb3, mode 0640).
Never commit these secrets. SFU signal/admin HTTP binds loopback:7880.
Public Caddy /voice/ allows only / and /rtc routes; room admin RPC is local.
ICE TCP 7881; UDP mux 7882; TURN UDP 3478. TURN/TLS is not configured.
Runtime flags: GXB3_SOCIAL_VOICE_ENABLED=1; both parent features
GXB3_SOCIAL_BAR_ENABLED and GXB3_SOCIAL_ARENA_ENABLED must be enabled separately.
Tokens are listener-only and expire for initial connection after 20 seconds.
Server grants microphone permission for at most 8 concurrent seats per room.
32 participants per room, 48 leases across rooms; 35-second heartbeat lease.
No game inventory, player profile or economy writes from Voice.
Test coverage: isolated authorization unit tests; actual two-browser RTP,
forced TURN UDP, mute/revoke/disconnect, two authenticated game browser
sessions through Quán Bar. Physical Android/iOS/Windows devices, external
mobile carrier NAT and full-capacity CPU/network soak remain to be verified.
