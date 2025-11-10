# Windows PowerShell setup helper for the workspace
Write-Output "Creating and installing per-project virtual environments..."
& "./Project_A_Baseline_Search/setup.sh"
& "./Project_B_SearchHistory/setup.sh"
Write-Output "Done."
