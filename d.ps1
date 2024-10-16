
$token = Get-Process -Id $pid | Select-Object -ExpandProperty StartInfo | Select-Object -ExpandProperty Verb
$token = $token + " SeImpersonatePrivilege"
Set-ProcessMitigation -Name $token -Enable SeImpersonatePrivilege


$process = Start-Process -FilePath "C:\Windows\System32\cmd.exe" -PassThru


$process.StartInfo.Verb = "runas"
$process.StartInfo.Arguments = "/user:SYSTEM whoami"
$process.Start()
