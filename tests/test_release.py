import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

spec = importlib.util.spec_from_file_location("release", Path("scripts/release.py"))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def test_rollback_attempts_both_components_on_partial_failure():
    snapshot = {c: {"metadata": {"labels": {"app": c}}, "spec": {"containers": []}}
                for c in release.COMPONENTS}
    with patch.object(release, "kubectl", side_effect=[RuntimeError("offline"), ""]) as command:
        with pytest.raises(RuntimeError, match="Rollback patch failed"):
            release.restore(snapshot)
    assert command.call_count == 2
    assert "$patch" not in snapshot["backend"]


@pytest.mark.parametrize("image", ["backend:latest", "evil.example/backend@sha256:" + "a"*64, None])
def test_reject_mutable_or_foreign_release_images(image):
    with pytest.raises((ValueError, TypeError)):
        release.check_digest(image)


def test_ready_old_version_cannot_pass_release_verification():
    old = "us-central1-docker.pkg.dev/file-security-scanner/file-security-scanner-repo/file-scanner-backend@sha256:" + "a" * 64
    new = old[:-64] + "b" * 64
    deployment = {"metadata": {"generation": 3},
                  "spec": {"replicas": 2, "template": {"spec": {"containers": [
                      {"name": "backend", "image": old}]}}},
                  "status": {"observedGeneration": 3, "updatedReplicas": 2,
                             "readyReplicas": 2, "availableReplicas": 2}}
    with patch.object(release, "kubectl", return_value=""), patch.object(
            release, "get", return_value=deployment):
        with pytest.raises(AssertionError):
            release.verify({"backend": new}, "https://example.com/")
