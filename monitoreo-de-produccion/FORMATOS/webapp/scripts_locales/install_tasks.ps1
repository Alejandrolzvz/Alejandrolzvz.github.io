$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "C:\PROYECTOS\FORMATOS\webapp\start_server.vbs"
$trigger = New-ScheduledTaskTrigger -AtStartup

Unregister-ScheduledTask -TaskName "FlaskWebAppService" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "FlaskWebAppService" -Action $action -Trigger $trigger -User "SYSTEM" -RunLevel Highest -Description "Servidor Web App de Osmosis"

$actionBackup = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c C:\PROYECTOS\FORMATOS\webapp\backup_db.bat"
$triggerBackup = New-ScheduledTaskTrigger -Daily -At "02:00AM"

Unregister-ScheduledTask -TaskName "FlaskWebAppBackup" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "FlaskWebAppBackup" -Action $actionBackup -Trigger $triggerBackup -User "SYSTEM" -RunLevel Highest -Description "Backup Diario BD App Osmosis"
