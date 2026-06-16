param(
    [string]$ProjectName = "aicp-docs",
    [string]$Branch = "main",
    [string]$Domain = "aicp.wuu73.org",
    [switch]$BindDomain
)

$ErrorActionPreference = "Stop"

Write-Host "Building MkDocs site..."
uv run --with-requirements requirements-docs.txt mkdocs build --strict

Write-Host "Deploying site/ to Cloudflare Pages project '$ProjectName'..."
pnpm dlx wrangler pages deploy site --project-name $ProjectName --branch $Branch --commit-dirty=true

if ($BindDomain) {
    if (-not $env:CLOUDFLARE_API_TOKEN) {
        throw "Set CLOUDFLARE_API_TOKEN before using -BindDomain."
    }
    if (-not $env:CLOUDFLARE_ACCOUNT_ID) {
        throw "Set CLOUDFLARE_ACCOUNT_ID before using -BindDomain."
    }

    $headers = @{
        Authorization = "Bearer $env:CLOUDFLARE_API_TOKEN"
        "Content-Type" = "application/json"
    }
    $baseUri = "https://api.cloudflare.com/client/v4/accounts/$env:CLOUDFLARE_ACCOUNT_ID/pages/projects/$ProjectName/domains"

    Write-Host "Checking Pages custom domains for '$ProjectName'..."
    $existing = Invoke-RestMethod -Method Get -Uri $baseUri -Headers $headers
    $alreadyBound = $false
    foreach ($item in $existing.result) {
        if ($item.name -eq $Domain) {
            $alreadyBound = $true
            break
        }
    }

    if ($alreadyBound) {
        Write-Host "Domain '$Domain' is already associated with '$ProjectName'."
    } else {
        Write-Host "Adding Pages custom domain '$Domain'..."
        $body = @{ name = $Domain } | ConvertTo-Json
        Invoke-RestMethod -Method Post -Uri $baseUri -Headers $headers -Body $body | Out-Null
        Write-Host "Domain add request submitted. Cloudflare may take a few minutes to validate DNS/TLS."
    }
}

Write-Host "Done."
