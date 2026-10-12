FROM python:3.12-slim AS luajit-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    git make gcc libc6-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --branch v2.1 --depth 1 https://github.com/LuaJIT/LuaJIT.git /tmp/luajit \
    && cd /tmp/luajit \
    && git fetch --depth 1 origin c6ffc141a8762b41703f9287d63d93622a13dd8f \
    && git checkout c6ffc141a8762b41703f9287d63d93622a13dd8f \
    && make -j2 XCFLAGS="-DLUAJIT_DISABLE_GC64" \
    && cp src/luajit /usr/local/bin/luajit-gxb3

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GXB2_LUAJIT=/usr/local/bin/luajit-gxb3

WORKDIR /app

COPY --from=luajit-builder /usr/local/bin/luajit-gxb3 /usr/local/bin/luajit-gxb3
RUN chmod +x /usr/local/bin/luajit-gxb3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep the multi-GB browser art in stable layers. Code-only deploys should
# not rebuild/re-upload every character asset.
COPY web/assets ./web/assets
COPY web/vendor ./web/vendor
COPY data ./data
COPY runtime ./runtime
COPY localization ./localization

# Small, frequently changing application layers come last.
COPY web/*.html ./web/
COPY web/*.css ./web/
COPY web/*.js ./web/
COPY gxb2 ./gxb2
COPY tools ./tools
COPY server.py ./server.py

RUN python -m compileall -q gxb2 server.py tools \
    && /usr/local/bin/luajit-gxb3 -v

EXPOSE 9080

CMD ["python","server.py"]
