# Local rendering dependencies

- PixiJS 6.5.10: https://github.com/pixijs/pixijs/tree/v6.5.10 (MIT).
- @pixi/unsafe-eval 6.5.10: installs the interpreter that avoids Function constructors under CSP. It does **not** enable unsafe-eval in the server policy.
- pixi-spine 3.1.2: https://github.com/pixijs-userland/spine/tree/pixi6. Uses its legacy JSON runtime for Spine 3.6.37. See SPINE-LICENSE.
- Original binary format reference for the archival converter: https://github.com/EsotericSoftware/spine-runtimes/blob/3.6/spine-csharp/src/SkeletonBinary.cs.

Fetched pinned packages from npm registry. No external CDN is required while playing.
