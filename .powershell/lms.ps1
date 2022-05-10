$cred = Get-AutomationPSCredential -Name 'srv_account_name'
$sas = Get-AutomationVariable -Name 'sas_name'
New-PSDrive -Name 'S' -Root '\\fqdn_server_name\dir_name$\folder_name' -Persist -PSProvider 'FileSystem' -Credential $cred
Set-Location -Path 'C:\Tools\Utilities'
.\azcopy.exe sync 'S:\' $sas --recursive=false
Get-PSDrive S | Remove-PSDrive -Force -Verbose