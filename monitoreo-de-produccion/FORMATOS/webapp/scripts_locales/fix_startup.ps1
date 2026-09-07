$startupPath = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$shortcutPath = [System.IO.Path]::Combine($startupPath, "StartOsmosisServer.lnk")
$targetPath = "C:\PROYECTOS\FORMATOS\webapp\start_server.vbs"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$targetPath`""
$Shortcut.WorkingDirectory = "C:\PROYECTOS\FORMATOS\webapp"
$Shortcut.WindowStyle = 7 # Minimized
$Shortcut.Save()

Write-Host "Acceso directo creado en: $shortcutPath" -ForegroundColor Green
