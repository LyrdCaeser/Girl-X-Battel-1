# Giftcode Studio — GXB 3

**Production native backend:** https://180-93-111-99.sslip.io

The separate frontend can be hosted as a standalone Vercel project with project root `giftcode-studio/`. It includes its own same-origin API bridge in `api/[...slug].js`, limited to the GXB3 login, giftcode, and GM verification routes. Do not point the Vercel project at the entire game repository root.

The frontend can also run on the production game server at `/giftcode-studio/` with no extra proxy. Login is via the same GXB3 username/password and session cookie. Only authenticated SUPER GM and the matching GM action key can create or revoke codes; all players can redeem their own codes. Never commit or store the key in .env files or frontend JavaScript.

Codes and usage records live in production PostgreSQL, not in the Vercel filesystem. Reward delivery is a pending GXB3 mail entry and must be claimed through the existing mailbox.

**Security:** keep the Vercel bridge path allowlist restricted; no CORS wildcard. The upstream server validates the account session and operator key. Deployments do not migrate or overwrite player files.
