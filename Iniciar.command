#!/bin/zsh
cd "${0:A:h}"
if ! python3 -c 'import google.protobuf' >/dev/null 2>&1; then
  print 'Falta la dependencia Protocol Buffers. Instala con:'
  print 'python3 -m pip install -r requirements.txt'
  read '?Pulsa Intro para cerrar.'
  exit 1
fi

pkill -f "python3 server.py" 2>/dev/null
sleep 1

python3 server.py --open
