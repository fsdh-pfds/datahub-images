$projCode = $env:PROJ_CD
$projRgName = $env:PROJ_RG
$projKeyVaultName = $env:PROJ_KV
$projSub = $env:PROJ_SUB
$projStorageAcct = $env:PROJ_STORAGE_ACCT
$azClientId = $env:CLIENT_ID

if ($env:ROOT_CA) {
    try {
        Write-Host "Installing custom root CA"
        $dest = "/tmp/custom-root-ca.crt"
        Copy-Item -Path "/etc/ssl/certs/ca-certificates.crt" -Destination $dest -Force
        Add-Content -Path $dest -Value "`n$($env:ROOT_CA)`n"
        Write-Host "Custom RootCA set to $dest"
    }
    catch {
        Write-Host "Failed to install custom root CA: $($_.Exception.Message)"
    }
}

Write-Host Rotate the SAS token in AKV Secret name storage-sas for project $projCode
$currentDate = Get-Date
$fiscalYearStart = if ($currentDate.Month -ge 4 ) { [datetime]::new($currentDate.Year, 4, 1) } else { [datetime]::new($currentDate.Year - 1, 4, 1) }

Connect-AzAccount -Identity -AccountId $azClientId
Set-AzContext -Subscription $projSub

$key_vault_name = $projKeyVaultName
$sas_secret_name = "container-sas"
$storage_acct_name = "$projStorageAcct"
$resource_group_name = $projRgName
$container_name = "datahub"
$context = $null;

try {
  $context = (Get-AzStorageAccount -ResourceGroupName $resource_group_name -AccountName $storage_acct_name).context
}
catch {
  Write-Host Error getting storage account $storage_acct_name in resource group $resource_group_name                           
}

if ($null -ne $context) {
  try {
    $secret_start = (Get-AzKeyVaultSecret -VaultName $key_vault_name -Name $sas_secret_name).tags.start
    $secret_expiry = (Get-AzKeyVaultSecret -VaultName $key_vault_name -Name $sas_secret_name).tags.expiry
    Write-Output "Existing expiry date: from $secret_start to $secret_expiry for key vault $key_vault_name secret $sas_secret_name"

    if ((get-date).addDays(14) -ge (get-date $secret_expiry)) {
      $new_start = (get-date).addDays(-1).toString("yyyy-MM-dd")
      $new_expiry = (get-date).addDays(91).toString("yyyy-MM-dd")
      $new_tags = @{ "start" = "$new_start"; "expiry" = "$new_expiry" } 
      Write-Output "Rotating SAS token - generating a new SAS token"
      $new_sas = New-AzStorageContainerSASToken -Name $container_name -Permission rwd -StartTime $new_start -ExpiryTime $new_expiry -context $context
      $new_sas_secret = ConvertTo-SecureString -String "$new_sas" -AsPlainText -Force
      Set-AzKeyVaultSecret -VaultName $key_vault_name -Name $sas_secret_name -SecretValue $new_sas_secret -Tags $new_tags
      Write-Output "New expiry date: from $new_start to $new_expiry"
    }

    Write-Output "Completed: New expiry $new_expiry"
  }
  catch {
    Write-Host Error rotating SAS for project $projCode.ToUpper() !!!
    Write-Host "Exception: $($_.Exception)"
    Write-Host "Error Message: $($_.Exception.Message)"                    
  }
}
else { Write-Output "Could not establish context to storage $storage_acct_name in resource group $resource_group_name" }

