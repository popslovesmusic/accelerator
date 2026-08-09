param(
    [string]$PackageName = "RT_CALCULUS_ATTACK_EVIDENCE_20260804"
)

$workspace = (Get-Location).Path
$workspaceRoot = (Resolve-Path -LiteralPath $workspace).Path.TrimEnd('\')
$package = Join-Path $workspaceRoot ("evidence_intake\" + $PackageName)
$outboundRoot = Join-Path $workspaceRoot "outbound\acellorator"
$export = Join-Path $outboundRoot $PackageName

if (-not (Test-Path -LiteralPath $package -PathType Container)) { throw "Frozen package not found: $package" }
if (-not (Test-Path -LiteralPath $outboundRoot -PathType Container)) { New-Item -ItemType Directory -Path $outboundRoot | Out-Null }
if (Test-Path -LiteralPath $export) { throw "Immutable export already exists: $export" }

$resolvedPackage = (Resolve-Path -LiteralPath $package).Path
$resolvedOutbound = (Resolve-Path -LiteralPath $outboundRoot).Path
$packagePrefix = $resolvedPackage.TrimEnd('\') + '\'
$outboundPrefix = $resolvedOutbound.TrimEnd('\') + '\'
if (-not $resolvedPackage.StartsWith($workspaceRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw "Package escaped RT workspace boundary" }
if (-not $resolvedOutbound.StartsWith($workspaceRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw "Outbound path escaped RT workspace boundary" }

Copy-Item -LiteralPath $resolvedPackage -Destination $resolvedOutbound -Recurse -Force

$exportFiles = Get-ChildItem -LiteralPath $export -File -Recurse | Where-Object { $_.FullName -notmatch '\\(__pycache__|\.git)(\\|$)' }
$entries = foreach ($file in $exportFiles) {
    $relative = $file.FullName.Substring($export.Length + 1).Replace('\', '/')
    [ordered]@{
        relative_path = $relative
        byte_size = [int64]$file.Length
        sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower()
    }
}

$transfer = [ordered]@{
    schema_id = "rt_attack_transfer_manifest_v1"
    schema_version = "1.0.0"
    transfer_id = "RT_TO_ACELLORATOR_$PackageName"
    source_program = "RT_CALCULUS"
    destination_program = "ACELLORATOR"
    direction = "RT_CALCULUS_TO_ACELLORATOR_ONLY"
    reverse_channel = "DISABLED"
    package_name = $PackageName
    package_path = $export
    generated_utc = [DateTime]::UtcNow.ToString('o')
    intake_status = "NOT_SUBMITTED"
    authority_status = "NON_CANONICAL_PROVISIONAL_EVIDENCE"
    file_count = @($entries).Count
    files = @($entries)
}
$transfer | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $outboundRoot ("$PackageName.transfer.json")) -Encoding UTF8

Write-Output "Created one-way export: $export"
Write-Output "Direction: RT_CALCULUS_TO_ACELLORATOR_ONLY"
Write-Output "Intake status: NOT_SUBMITTED"
