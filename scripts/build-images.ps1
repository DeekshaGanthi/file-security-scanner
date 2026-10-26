param([Parameter(Mandatory=$true)][string]$Tag)
$ErrorActionPreference = 'Stop'
if ($Tag -notmatch '^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}$' -or $Tag -eq 'latest') { throw 'Use a unique immutable release tag' }
if ((gcloud.cmd config get-value project) -ne 'file-security-scanner') { throw 'Wrong project' }
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE) { throw 'Docker unavailable' }
gcloud.cmd auth configure-docker us-central1-docker.pkg.dev --quiet
if ($LASTEXITCODE) { throw 'Registry authentication failed' }
foreach ($component in @('backend','frontend')) {
    $image = "us-central1-docker.pkg.dev/file-security-scanner/file-security-scanner-repo/file-scanner-${component}:$Tag"
    docker build -f "Dockerfile.$component" -t $image .
    if ($LASTEXITCODE) { throw "Build failed: $component" }
    if ($component -eq 'backend') {
        Get-Content scripts/container-smoke.py | docker run --rm -i --entrypoint python $image -
        if ($LASTEXITCODE) { throw 'Backend smoke test failed' }
    }
    docker push $image
    if ($LASTEXITCODE) { throw "Push failed: $component" }
    gcloud.cmd artifacts docker images describe $image --format='value(image_summary.digest)'
    if ($LASTEXITCODE) { throw 'Digest lookup failed' }
}
Write-Output 'Use published digests with render-k8s.py; commit the actual rendered manifests after deployment.'
