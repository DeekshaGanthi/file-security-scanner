"""Digest-only GKE releases with durable, pod-template rollback metadata.

Linux Actions and Windows PowerShell: python scripts/release.py PHASE ...
Only Deployment pod templates are patched; HPA owns replicas.
"""
import argparse
import copy
import json
import re
import subprocess
import urllib.request
from pathlib import Path

COMPONENTS = ("backend", "frontend")


def kubectl(*args, payload=None):
    result = subprocess.run(["kubectl", "-n", "scanner", *args],
                            input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, timeout=660)
    if result.returncode:
        # Do not echo arbitrary API output, which could contain configuration values.
        raise RuntimeError(f"kubectl {args[0]} failed (exit {result.returncode})")
    return result.stdout


def get(kind, name):
    return json.loads(kubectl("get", kind, name, "-o", "json"))


def image(template, component):
    return next(c["image"] for c in template["spec"]["containers"] if c["name"] == component)


def check_digest(value):
    if not re.fullmatch(r"us-central1-docker.pkg.dev/file-security-scanner/file-security-scanner-repo/file-scanner-(backend|frontend)@sha256:[a-f0-9]{64}", value):
        raise ValueError("Release and rollback images must use the approved registry and immutable digests")


def verify(expected, url):
    for component in COMPONENTS:
        kubectl("rollout", "status", f"deployment/{component}", "--timeout=600s")
        deployment = get("deployment", component)
        desired = deployment["spec"]["replicas"]
        status = deployment["status"]
        assert desired >= 2, f"{component}: fewer than two desired replicas"
        assert status.get("observedGeneration", 0) >= deployment["metadata"]["generation"]
        assert status.get("updatedReplicas", 0) == desired
        assert status.get("readyReplicas", 0) == desired
        assert status.get("availableReplicas", 0) == desired
        assert image(deployment["spec"]["template"], component) == expected[component]
        pods = json.loads(kubectl("get", "pods", "-l", f"app={component}", "-o", "json"))["items"]
        active = [p for p in pods if not p["metadata"].get("deletionTimestamp")]
        assert len(active) == desired
        for pod in active:
            container = next(c for c in pod["spec"]["containers"] if c["name"] == component)
            assert container["image"] == expected[component]
            cs = next(c for c in pod["status"]["containerStatuses"] if c["name"] == component)
            assert cs["ready"] and cs.get("imageID"), "Image must be running and ready"
            paths = ["/health/live", "/health/ready"] if component == "backend" else ["/_stcore/health"]
            port = 8000 if component == "backend" else 8501
            for path in paths:
                # Check each new pod directly so an old Service endpoint cannot mask a bad release.
                code = ("import urllib.request; "
                        f"r=urllib.request.urlopen('http://127.0.0.1:{port}{path}',timeout=15); "
                        "assert r.status==200")
                kubectl("exec", pod["metadata"]["name"], "-c", component, "--", "python", "-c", code)
        print(f"VERIFIED {component}: {desired} replicas, {expected[component]}")
    if not url.startswith("https://"):
        raise ValueError("Public health check requires HTTPS")
    with urllib.request.urlopen(url, timeout=30) as response:
        assert response.status == 200
    print("VERIFIED public HTTPS 200")


def restore(snapshot):
    # Attempt both restores even if one patch fails; retain every failure.
    failures = []
    for component in COMPONENTS:
        try:
            template = copy.deepcopy(snapshot[component])
            template["$patch"] = "replace"
            kubectl("patch", "deployment", component, "--type=strategic", "-p",
                    json.dumps({"spec": {"template": template}}))
        except Exception as error:
            failures.append(f"{component}: {error}")
    if failures:
        raise RuntimeError("Rollback patch failed: " + "; ".join(failures))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["capture", "deploy", "verify", "rollback"])
    parser.add_argument("--directory", default="milestone6-tmp/release")
    parser.add_argument("--backend-image")
    parser.add_argument("--frontend-image")
    parser.add_argument("--sha")
    parser.add_argument("--demo-failure", action="store_true")
    parser.add_argument("--url", default="https://scanner.136-69-114-222.sslip.io/")
    args = parser.parse_args()
    directory = Path(args.directory)
    directory.mkdir(parents=True, exist_ok=True)
    snapshot_file = directory / "previous.json"
    if args.phase == "capture":
        snapshot = {c: get("deployment", c)["spec"]["template"] for c in COMPONENTS}
        expected = {c: image(snapshot[c], c) for c in COMPONENTS}
        for value in expected.values():
            check_digest(value)
        verify(expected, args.url)
        snapshot_file.write_text(json.dumps(snapshot), encoding="utf-8")
        print("Previous healthy pod templates captured; snapshot stays private")
        return
    snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))
    if args.phase == "rollback":
        if not (directory / "attempted").exists():
            print("No deployment mutation attempted; rollback skipped")
            return
        print("ROLLBACK INITIATED")
        restore(snapshot)
        verify({c: image(snapshot[c], c) for c in COMPONENTS}, args.url)
        print("PREVIOUS VERSION RESTORED AND VERIFIED")
        return
    expected = {"backend": args.backend_image, "frontend": args.frontend_image}
    for value in expected.values():
        check_digest(value)
    if args.phase == "verify":
        verify(expected, args.url)
        return
    if not args.sha or not re.fullmatch(r"[a-f0-9]{40}", args.sha):
        raise ValueError("Full release commit SHA required")
    for component in COMPONENTS:
        template = copy.deepcopy(snapshot[component])
        template.setdefault("metadata", {}).setdefault("annotations", {})["scanner/release-sha"] = args.sha
        container = next(c for c in template["spec"]["containers"] if c["name"] == component)
        container["image"] = expected[component]
        if args.demo_failure and component == "backend":
            container["readinessProbe"]["httpGet"]["path"] = "/milestone6-intentional-readiness-failure"
        template["$patch"] = "replace"
        (directory / "attempted").touch()
        kubectl("patch", "deployment", component, "--type=strategic", "-p",
                json.dumps({"spec": {"template": template}}))
        kubectl("rollout", "status", f"deployment/{component}", "--timeout=600s")


if __name__ == "__main__":
    main()
