Get-ChildItem -Path $PSScriptRoot\sandbox\ -File -Filter "*.py" -Exclude "_*" -Recurse | ForEach-Object {
    Write-Output "Running $($_.Directory.Name)/$($_.Name)..."
    python $_.FullName
}
