#!/usr/bin/env python3
"""Tiny HTTP service: GET /api/node?vm=<name> -> where the VMI runs right now.

Only the Python standard library is used. It reads the VirtualMachineInstance
from the Kubernetes API with the pod's service account (Role: get VMIs).
"""
import json
import os
import ssl
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

SA_DIR = "/var/run/secrets/kubernetes.io/serviceaccount"
API = "https://kubernetes.default.svc"
NAMESPACE = open(os.path.join(SA_DIR, "namespace")).read().strip()
ALLOWED = {v.strip() for v in os.environ.get("ALLOWED_VMS", "vm-web").split(",") if v.strip()}
PORT = int(os.environ.get("PORT", "8080"))
CTX = ssl.create_default_context(cafile=os.path.join(SA_DIR, "ca.crt"))


def get_vmi(name):
    token = open(os.path.join(SA_DIR, "token")).read().strip()
    req = urllib.request.Request(
        "%s/apis/kubevirt.io/v1/namespaces/%s/virtualmachineinstances/%s" % (API, NAMESPACE, name),
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, context=CTX, timeout=5) as resp:
        return json.load(resp)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 (http.server API)
        url = urlparse(self.path)
        if url.path == "/healthz":
            return self._send(200, {"ok": True})
        if url.path != "/api/node":
            return self._send(404, {"error": "not found"})
        vm = parse_qs(url.query).get("vm", ["vm-web"])[0]
        if vm not in ALLOWED:
            return self._send(403, {"error": "vm not allowed"})
        try:
            status = get_vmi(vm).get("status", {})
        except urllib.error.HTTPError as err:
            return self._send(200 if err.code == 404 else 502,
                              {"vm": vm, "phase": "NotRunning" if err.code == 404 else "Unknown",
                               "node": None, "error": err.reason})
        except Exception as err:  # pylint: disable=broad-except
            return self._send(502, {"vm": vm, "phase": "Unknown", "node": None, "error": str(err)})
        mig = status.get("migrationState") or {}
        return self._send(200, {
            "vm": vm,
            "namespace": NAMESPACE,
            "phase": status.get("phase"),
            "node": status.get("nodeName"),
            "migration": {
                "source": mig.get("sourceNode"),
                "target": mig.get("targetNode"),
                "completed": mig.get("completed", False),
                "failed": mig.get("failed", False),
                "end": mig.get("endTimestamp"),
            } if mig else None,
        })

    def log_message(self, fmt, *args):  # quieter logs: only errors
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
