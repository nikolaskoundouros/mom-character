#!/bin/bash
# usage: fitm.sh GAP FLARE CURL ZEND "label"
S=/private/tmp/claude-501/-Users-nick/e53bbed9-cca3-49b0-bf6a-b54722760597/scratchpad
scp -q -o BatchMode=yes ~/Desktop/mom-character/scripts/hair2_locks.py ~/Desktop/mom-character/scripts/fit_multi.py nick@37.27.148.115:Desktop/mom-character/scripts/
OUT=$(ssh -o BatchMode=yes nick@37.27.148.115 "cd ~/Desktop/mom-character && ~/Desktop/render-desk/bin/workbench push ~/Desktop/mom-character >/dev/null 2>&1; python3 live/bcall.py 'P_GAP=$1
P_FLARE=$2
P_CURL=$3
P_ZEND=$4
exec(open(\"/Users/nick/Desktop/mom-character/scripts/fit_multi.py\").read())' --timeout 900 2>&1 | grep FITM; rm -rf /tmp/fpull; mkdir -p /tmp/fpull; ~/Desktop/render-desk/bin/workbench pull /root/live_snaps /tmp/fpull >/dev/null 2>&1")
echo "$OUT"
scp -q -o BatchMode=yes nick@37.27.148.115:'/tmp/fpull/live_snaps/fit_side.png' nick@37.27.148.115:'/tmp/fpull/live_snaps/fit_q34.png' $S/ana/ 2>/dev/null || { scp -q -o BatchMode=yes nick@37.27.148.115:/tmp/fpull/live_snaps/fit_side.png $S/ana/; scp -q -o BatchMode=yes nick@37.27.148.115:/tmp/fpull/live_snaps/fit_q34.png $S/ana/; }
MEAN=$(echo "$OUT" | sed -n 's/.*MEAN=\([0-9.]*\).*/\1/p'); PER=$(echo "$OUT" | sed -n 's/^FITM \(.*\) MEAN.*/\1/p' | sed 's/(extra[^)]*)//g')
[ -n "$MEAN" ] && python3 -I ~/Desktop/mom-character/scripts/viz_multi.py "$MEAN" "${5:-$1 $2 $3 $4}" "$PER"
