#!/usr/bin/env python3
"""Poll already-queued Kie tasks (queued.csv: taskId,slug) and download results.
Never creates tasks — safe to re-run, skips already-downloaded slugs."""
import csv
import json
import os
import time
import urllib.request

INFO = "https://api.kie.ai/api/v1/jobs/recordInfo?taskId="
KEY = os.environ["KIE_API_KEY"]
HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


with open(os.path.join(HERE, "queued.csv")) as f:
    pending = {tid: slug for slug, tid in csv.reader(f)
               if not os.path.exists(os.path.join(OUT, slug + ".png"))}
print(f"pending: {len(pending)}")

deadline = time.time() + 1800
failed = []
while pending and time.time() < deadline:
    for tid in list(pending):
        slug = pending[tid]
        try:
            d = get(INFO + tid)["data"]
        except Exception as e:  # noqa: BLE001
            print(f"poll error {slug}: {e}")
            continue
        if not d:
            print(f"no data yet {slug}")
            continue
        if d["state"] == "success":
            url = json.loads(d["resultJson"])["resultUrls"][0]
            try:
                download(url, os.path.join(OUT, slug + ".png"))
                pending.pop(tid)
                print(f"DONE {slug} ({len(pending)} left)", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"download error {slug}: {e}")
        elif d["state"] == "fail":
            pending.pop(tid)
            failed.append(slug)
            print(f"FAIL {slug}: {d.get('failCode')} {d.get('failMsg')}", flush=True)
    if pending:
        time.sleep(15)

if pending:
    print(f"TIMEOUT pending: {sorted(pending.values())}")
if failed:
    print(f"FAILED (regenerate with generate.py --only {','.join(failed)}): {failed}")
print("collect complete")
