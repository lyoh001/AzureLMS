# https://docs.microsoft.com/en-us/azure/automation/automation-windows-hrw-install

# deploy automation account, log analytics workspace via bicep

# Install-Script -Name New-OnPremiseHybridWorker

# Install-Module -Name Az -AllowClobber

# $NewOnPremiseHybridWorkerParameters = @{
#   AutomationAccountName = <nameOfAutomationAccount>
#   AAResourceGroupName   = <nameOfResourceGroup>
#   OMSResourceGroupName  = <nameOfResourceGroup>
#   HybridGroupName       = <nameOfHRWGroup>
#   SubscriptionID        = <subscriptionId>
#   WorkspaceName         = <nameOfLogAnalyticsWorkspace>
# }
# New-OnPremiseHybridWorker.ps1 @NewOnPremiseHybridWorkerParameters

$NewOnPremiseHybridWorkerParameters = @{
  AutomationAccountName = 'hybridworkeraa'
  AAResourceGroupName   = 'hybridworkerrg'
  OMSResourceGroupName  = 'hybridworkerrg'
  HybridGroupName       = 'hybridworkergroups'
  SubscriptionID        = '<subscriptionId>'
}
New-OnPremiseHybridWorker.ps1 @NewOnPremiseHybridWorkerParameters

$cred = Get-AutomationPSCredential -Name 'srv_account_name'
$sas = Get-AutomationVariable -Name 'sas_name'
New-PSDrive -Name 'S' -Root '\\fqdn_server_name\dir_name$\folder_name' -Persist -PSProvider 'FileSystem' -Credential $cred
Set-Location -Path 'C:\Tools\Utilities'
.\azcopy.exe sync $sas 'S:\' --recursive=false
Get-PSDrive S | Remove-PSDrive -Force -Verbose