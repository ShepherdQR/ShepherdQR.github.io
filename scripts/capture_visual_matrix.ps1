param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [Parameter(Mandatory = $true)][string]$CliPath,
    [string]$OutputDir = "output/playwright/aesthetic-summit-2026-08-01",
    [switch]$IncludeChronicle,
    [string[]]$OnlySurface = @(),
    [switch]$PreserveExisting
)

$ErrorActionPreference = "Stop"
$session = "zqr-aesthetic-matrix"
$root = (Resolve-Path -LiteralPath ".").Path
$output = Join-Path $root $OutputDir
New-Item -ItemType Directory -Force -Path $output | Out-Null
if (-not $PreserveExisting) {
    Get-ChildItem -LiteralPath $output -Filter "*.png" -File | Remove-Item -Force
}

$allSurfaces = @(
    @{ Name = "field"; Path = "/index.html" },
    @{ Name = "atlas"; Path = "/archive.html" },
    @{ Name = "atlas-ledger"; Path = "/archive.html?view=ledger" },
    @{ Name = "evidence"; Path = "/stats.html" },
    @{ Name = "system"; Path = "/field.html" },
    @{ Name = "article-exposition"; Path = "/thoughts/0003/" },
    @{ Name = "article-research-log"; Path = "/study/0001/" },
    @{ Name = "article-reading"; Path = "/books/0032/" },
    @{ Name = "article-visual-essay"; Path = "/thoughts/0028/" }
)
if ($IncludeChronicle) {
    $allSurfaces += @{ Name = "chronicle"; Path = "/chronicle.html" }
}
$surfaces = $allSurfaces
if ($OnlySurface.Count -gt 0) {
    $surfaces = @($allSurfaces | Where-Object { $OnlySurface -contains $_.Name })
    if ($surfaces.Count -eq 0) {
        throw "No visual surface matched: $($OnlySurface -join ', ')"
    }
}
if ($PreserveExisting) {
    foreach ($surface in $surfaces) {
        Get-ChildItem -LiteralPath $output -Filter "$($surface.Name)-*.png" -File | Remove-Item -Force
    }
}

$viewports = @(
    @{ Name = "desktop"; Width = 1440; Height = 1100 },
    @{ Name = "mobile"; Width = 390; Height = 844 }
)
$profiles = @("field", "museum")

function Invoke-PlaywrightCli {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $result = & $CliPath "-s=$session" @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "playwright-cli failed: $($Arguments -join ' ')`n$($result -join "`n")"
    }
    return $result
}

function Warm-VisualPage {
    $script = 'async () => { const pause = ms => new Promise(resolve => setTimeout(resolve, ms)); const root = document.scrollingElement || document.documentElement; document.querySelectorAll("img[loading=lazy]").forEach(image => { image.loading = "eager"; }); const step = Math.max(480, Math.floor(window.innerHeight * 0.72)); for (let y = 0; y <= root.scrollHeight; y += step) { window.scrollTo(0, y); await pause(35); } window.scrollTo(0, root.scrollHeight); await pause(140); const images = Array.from(document.images).filter(image => image.currentSrc || image.src); await Promise.all(images.map(image => typeof image.decode === "function" ? image.decode().catch(() => {}) : Promise.resolve())); await pause(140); return { imageCount: images.length, height: root.scrollHeight }; }'
    Invoke-PlaywrightCli eval $script | Out-Null
}

Invoke-PlaywrightCli open "$BaseUrl/index.html" | Out-Null
Invoke-PlaywrightCli snapshot | Out-Null

foreach ($profile in $profiles) {
    Invoke-PlaywrightCli localstorage-set zqr-visual-system $profile | Out-Null
    foreach ($viewport in $viewports) {
        Invoke-PlaywrightCli resize $viewport.Width $viewport.Height | Out-Null
        foreach ($surface in $surfaces) {
            Invoke-PlaywrightCli goto "$BaseUrl$($surface.Path)" | Out-Null
            Warm-VisualPage
            if ($surface.Name -eq "field") {
                Invoke-PlaywrightCli eval '(element) => { element.scrollIntoView(); return window.scrollY; }' '.portrait-card' | Out-Null
            } else {
                Invoke-PlaywrightCli eval '() => { window.scrollTo(0, 0); return window.scrollY; }' | Out-Null
            }
            if ($surface.Name -eq "atlas-ledger") {
                $segments = @(
                    @{ Name = "start"; Script = 'async () => { window.scrollTo(0, 0); await new Promise(resolve => setTimeout(resolve, 180)); return window.scrollY; }' },
                    @{ Name = "middle"; Script = 'async () => { const root = document.scrollingElement || document.documentElement; window.scrollTo(0, Math.max(0, (root.scrollHeight - window.innerHeight) / 2)); await new Promise(resolve => setTimeout(resolve, 180)); return window.scrollY; }' },
                    @{ Name = "end"; Script = 'async () => { const root = document.scrollingElement || document.documentElement; window.scrollTo(0, root.scrollHeight); await new Promise(resolve => setTimeout(resolve, 180)); return window.scrollY; }' }
                )
                foreach ($segment in $segments) {
                    Invoke-PlaywrightCli eval $segment.Script | Out-Null
                    $filename = "$($surface.Name)-$profile-$($viewport.Name)-$($segment.Name).png"
                    Invoke-PlaywrightCli screenshot --filename (Join-Path $output $filename) | Out-Null
                }
            } else {
                $filename = "$($surface.Name)-$profile-$($viewport.Name).png"
                Invoke-PlaywrightCli screenshot --filename (Join-Path $output $filename) --full-page | Out-Null
            }
        }
    }
}

Invoke-PlaywrightCli close | Out-Null

$records = Get-ChildItem -LiteralPath $output -Filter "*.png" | Sort-Object Name | ForEach-Object {
    [ordered]@{
        file = $_.Name
        bytes = $_.Length
        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$manifest = [ordered]@{
    generatedAt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    baseUrl = $BaseUrl
    profiles = $profiles
    viewports = $viewports
    baselineSurfaceCount = 9
    surfaces = $allSurfaces
    capturedSurfaces = $surfaces
    includesChronicle = [bool]$IncludeChronicle
    screenshotCount = $records.Count
    screenshots = $records
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $output "manifest.json") -Encoding utf8
Write-Output "Captured $($records.Count) screenshots in $output"
