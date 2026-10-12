try {
    flask db init
} catch {
    Write-Host "flask db init gagal, lanjut ke migrate..."
}

flask db migrate
flask db upgrade
