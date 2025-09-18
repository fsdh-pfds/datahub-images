$projCode = $env:PROJ_CD
$projRgName = $env:PROJ_RG
$projBudget = [Math]::Round($env:PROJ_BUDGET, 4)
$projBudgetEnforce = $null -eq $env:PROJ_ENFORCE -or [bool]::Parse("$env:PROJ_ENFORCE")
$projDatabricksRgName = $env:PROJ_DBR_RG
$azClientId = $env:CLIENT_ID
$projCMK = "project-cmk"
$projKeyVaultName = $env:PROJ_KV
$projSub = $env:PROJ_SUB

Write-Host FSDH Checking spend for project $projCode $projBudget
$currentDate = Get-Date
$fiscalYearStart = if ($currentDate.Month -ge 4 ) { [datetime]::new($currentDate.Year, 4, 1) } else { [datetime]::new($currentDate.Year - 1, 4, 1) }

Connect-AzAccount -Identity -AccountId $azClientId
Set-AzContext -Subscription $projSub

Write-Host FSDH Checking existence for resource group $projRgName with FY annual budget $projBudget                  
$maxRetries = 10 ; $retryCount = 0 ; $delay = 30 # Delay in seconds
while ($retryCount -lt $maxRetries) {
  try {
    $resourceGroupCost = 0
    if (-not ($null -eq $projRgName)) { $resourceGroupCost = (Get-AzConsumptionUsageDetail -StartDate $fiscalYearStart.toUniversalTime() -EndDate $currentDate.toUniversalTime() -ResourceGroup $projRgName | Measure-Object -Property PretaxCost -Sum).Sum }
    $dbrResourceGroupCost = 0
    if (-not ($null -eq $projDatabricksRgName)) { $dbrResourceGroupCost = (Get-AzConsumptionUsageDetail -StartDate $fiscalYearStart.toUniversalTime() -EndDate $currentDate.toUniversalTime() -ResourceGroup $projDatabricksRgName | Measure-Object -Property PretaxCost -Sum).Sum }

    if ($null -eq $resourceGroupCost) { $resourceGroupCost = 0 }
    if ($null -eq $dbrResourceGroupCost) { $dbrResourceGroupCost = 0 }
    break
  }
  catch {
    if ($_.Exception.Response.StatusCode -eq 429) {
      Write-Output "TooManyRequests error. Retrying in $delay seconds..."
      Start-Sleep -Seconds $delay
      $retryCount++
    }
    else {
      throw $_
    }
  }
}
$totalSpendDollar = [math]::round(($resourceGroupCost + $dbrResourceGroupCost ), 2)
Write-Host Current spend for $projCode.ToUpper() is $totalSpendDollar

$formattedBudget = $projBudget.ToString("C", [System.Globalization.CultureInfo]::GetCultureInfo("en-CA"))
$formattedTotalSpend = $totalSpendDollar.ToString("C", [System.Globalization.CultureInfo]::GetCultureInfo("en-CA"))
$formattedProjRGSpend = $resourceGroupCost.ToString("C", [System.Globalization.CultureInfo]::GetCultureInfo("en-CA"))
$formattedDbrRGSpend = $dbrResourceGroupCost.ToString("C", [System.Globalization.CultureInfo]::GetCultureInfo("en-CA"))

Write-Host Current spend for $projCode.ToUpper() = $formattedProjRGSpend + $formattedDbrRGSpend = $formattedTotalSpend "(budget $formattedBudget, spend $formattedTotalSpend)"
if ( $totalSpendDollar -gt $projBudget ) {
  Write-Host Budget of $projBudget for $projCode.ToUpper() has run out: actual $formattedTotalSpend. Attemping to disable CMK

  try {
    # Write-Host Adding key permission on $projKeyVaultName to ${{ variables.serviceConnectionSPN }}
    # Set-AzKeyVaultAccessPolicy -VaultName $projKeyVaultName -ServicePrincipalName ${{ variables.serviceConnectionSPN }} -PermissionsToKeys list,update
    if ((Get-AzKeyVaultKey -VaultName $projKeyVaultName -KeyName $projCMK).enabled) {
      Write-Host Disabling CMK for $projCode.ToUpper() because the key is currently enabled
      $Tags = @{'disabledDate' = "$currentDate"; 'disabledReason' = 'Exceeded budget' }
      if ( $projBudgetEnforce ) {
        Update-AzKeyVaultKey -VaultName $projKeyVaultName -Name $projCMK -Enable $False -Tag $Tags -PassThru
      }
      else { Write-Host $projCode.ToUpper() CMK in key vault $projKeyVaultName is not being disabled as the enforce parameter was set to false }
    }
    else { Write-Host CMK for $projCode.ToUpper() has already been disabled, no action to be taken }
    # Write-Host Removing key permission on $projKeyVaultName to ${{ variables.serviceConnectionSPN }}
    # Remove-AzKeyVaultAccessPolicy $projKeyVaultName -ServicePrincipalName ${{ variables.serviceConnectionSPN }} -PassThru
  }
  catch {
    Write-Host Error disabling CMK for project $projCode.ToUpper() "(budget $formattedBudget, spend $formattedTotalSpend) !!!"
    Write-Host "Exception: $($_.Exception)"
    Write-Host "Error Message: $($_.Exception.Message)"                    
  }
}

