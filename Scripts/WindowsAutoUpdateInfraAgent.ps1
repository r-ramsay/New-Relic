# Define variables
$downloadUrl = "https://download.newrelic.com/infrastructure_agent/windows/newrelic-infra.msi"
$installerPath = "$env:TEMP\newrelic-infra.msi"
$serviceName = "newrelic-infra"
$agentExePath = "C:\Program Files\New Relic\newrelic-infra\newrelic-infra.exe"
$logPath = "C:\ProgramData\New Relic\newrelic-infra\newrelic-infra.log"
$graphqlApiUrl = "https://api.newrelic.com/graphql" # New Relic Change Tracking GraphQL endpoint
$apiKey = "NRAK-0H0N3G6YSVIJHYSRQ9PIMYU50H2" # Replace with your New Relic API key

# Function to log messages
function Log-Message {
    param (
        [string]$message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "$timestamp - $message"
}

# Function to get the current version of the installed agent
function Get-InstalledVersion {
    if (Test-Path $agentExePath) {
        $fileVersionInfo = (Get-Item $agentExePath).VersionInfo
        return $fileVersionInfo.ProductVersion
    } else {
        return $null
    }
}

# Function to get the latest available version from the MSI
function Get-LatestVersion {
    Download-MSI
    $msiInfo = Get-MsiVersion -Path $installerPath
    return $msiInfo.Version
}

# Function to download the MSI installer
function Download-MSI {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing | Out-Null
}

# Function to extract version from MSI file
function Get-MsiVersion {
    param (
        [string]$Path
    )
    $msi = New-Object -ComObject WindowsInstaller.Installer
    $db = $msi.GetType().InvokeMember("OpenDatabase", "InvokeMethod", $null, $msi, @($Path, 0))
    $view = $db.GetType().InvokeMember("OpenView", "InvokeMethod", $null, $db, ("SELECT Value FROM Property WHERE Property='ProductVersion'"))
    $view.Execute()
    $record = $view.Fetch()
    $version = $record.GetType().InvokeMember("StringData", "GetProperty", $null, $record, 1)
    return @{ Version = $version }
}

# Function to normalize version strings
function Normalize-Version {
    param (
        [string]$version
    )
    # Split version string into components
    $versionParts = $version.Split('.')
    
    # Ensure the version string has 4 components
    while ($versionParts.Length -lt 4) {
        $versionParts += "0"
    }

    # Join the components back into a normalized version string
    return [string]::Join('.', $versionParts)
}

# Function to compare two version strings
function Compare-Versions {
    param (
        [string]$version1,
        [string]$version2
    )
    $v1 = [version]$version1
    $v2 = [version]$version2
    return $v1.CompareTo($v2)
}

# Function to retrieve entityGuid from newrelic-infra.log
function Get-EntityGuid {
    if (Test-Path $logPath) {
        $logContent = Get-Content $logPath -Raw
        $entityGuidPattern = 'agent-guid=([^\s]+)'
        $matches = [regex]::Matches($logContent, $entityGuidPattern)
        if ($matches.Count -gt 0) {
            return $matches[0].Groups[1].Value
        } else {
            Log-Message "Entity GUID not found in log."
            return $null
        }
    } else {
        Log-Message "Log file not found."
        return $null
    }
}

# Function to send POST request to New Relic's Change Tracking GraphQL API
function Post-ChangeTracking {
    param (
        [string]$entityGuid,
        [string]$version
    )
    $headers = @{
        "Content-Type" = "application/json"
        "API-Key" = $apiKey
    }
    # Log raw values for debugging
    Log-Message "GraphQL Query: mutation { changeTrackingCreateDeployment(deployment: { entityGuid: ""$entityGuid"", version: ""$version"", deploymentType: BASIC }) { deploymentId } }"

    $body = @{
        query = @"
        mutation {
            changeTrackingCreateDeployment(
                deployment: {
                    entityGuid: `"$entityGuid`",
                    version: `"$version`",
                    deploymentType: BASIC
                }
            ) {
                deploymentId
            }
        }
"@
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri $graphqlApiUrl -Method Post -Headers $headers -Body $body
        if ($response -and $response.data -and $response.data.changeTrackingCreateDeployment -and $response.data.changeTrackingCreateDeployment.deploymentId) {
            Log-Message "Deployment created successfully. Deployment ID: $($response.data.changeTrackingCreateDeployment.deploymentId)"
        } else {
            Log-Message "Deployment creation failed. Response: $($response | ConvertTo-Json -Depth 5)"
        }
    } catch {
        Log-Message "Error posting to Change Tracking API: $_"
    }
}

# Compare versions and update if necessary
$currentVersion = Normalize-Version (Get-InstalledVersion)
$latestVersion = Normalize-Version (Get-LatestVersion)
$entityGuid = Get-EntityGuid

Log-Message "Installed version: $currentVersion"
Log-Message "Latest version: $latestVersion"
Log-Message "Entity GUID: $entityGuid"

if ($currentVersion -eq $null) {
    Log-Message "New Relic Infrastructure agent is not installed."
} elseif (Compare-Versions -version1 $latestVersion -version2 $currentVersion -gt 0) {
    Log-Message "A newer version is available. Updating to version $latestVersion..."

    # Check if the service is running and stop it
    if (Get-Service -Name $serviceName -ErrorAction SilentlyContinue) {
        Log-Message "Stopping the $serviceName service..."
        Stop-Service -Name $serviceName -Force
    } else {
        Log-Message "$serviceName service is not running."
    }

    # Install the new version of the agent
    Log-Message "Installing New Relic Infrastructure agent..."
    Start-Process msiexec.exe -ArgumentList "/i", "`"$installerPath`"", "/qn", "/norestart" -NoNewWindow -Wait

    # Remove the downloaded installer
    Remove-Item -Path $installerPath -Force

    # Restart the service
    Log-Message "Starting the $serviceName service..."
    Start-Service -Name $serviceName

    # Post the update to New Relic's Change Tracking API
    if ($entityGuid) {
        Log-Message "Posting update to Change Tracking API..."
        Post-ChangeTracking -entityGuid $entityGuid -version $latestVersion
    } else {
        Log-Message "Entity GUID not found; skipping Change Tracking POST."
    }

    Log-Message "New Relic Infrastructure agent update to version $latestVersion completed."
} else {
    Log-Message "The installed version is up-to-date. No update required."
}
