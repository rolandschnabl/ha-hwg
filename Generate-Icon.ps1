# PowerShell script to create a simple icon for HW Group integration
# This creates a basic PNG icon using .NET graphics

Add-Type -AssemblyName System.Drawing

# Create bitmap
$size = 256
$bitmap = New-Object System.Drawing.Bitmap($size, $size)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias

# Define colors
$blue = [System.Drawing.Color]::FromArgb(255, 0, 102, 204)
$white = [System.Drawing.Color]::FromArgb(230, 255, 255, 255)
$darkBlue = [System.Drawing.Color]::FromArgb(255, 0, 68, 170)

# Draw background circle
$center = $size / 2
$radius = 120
$graphics.FillEllipse(
    (New-Object System.Drawing.SolidBrush($blue)),
    $center - $radius, 
    $center - $radius, 
    $radius * 2, 
    $radius * 2
)

# Draw device/server rectangle
$graphics.FillRectangle(
    (New-Object System.Drawing.SolidBrush($white)),
    70, 60, 116, 80
)

# Draw server lines
$lineBrush = New-Object System.Drawing.SolidBrush($blue)
$graphics.FillRectangle($lineBrush, 80, 70, 96, 8)
$graphics.FillRectangle($lineBrush, 80, 88, 96, 8)
$graphics.FillRectangle($lineBrush, 80, 106, 96, 8)

# Draw sensor circles
$font = New-Object System.Drawing.Font("Arial", 18, [System.Drawing.FontStyle]::Bold)
$whiteBrush = New-Object System.Drawing.SolidBrush($white)
$textBrush = New-Object System.Drawing.SolidBrush($blue)
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center

# Sensor 1 - Temperature (T)
$x1 = 95
$y1 = 170
$graphics.FillEllipse($whiteBrush, ($x1 - 15), ($y1 - 15), 30, 30)
$rect1 = New-Object System.Drawing.RectangleF(($x1 - 15), ($y1 - 15), 30, 30)
$graphics.DrawString("T", $font, $textBrush, $rect1, $format)

# Sensor 2 - Humidity (H)
$x2 = 128
$y2 = 170
$graphics.FillEllipse($whiteBrush, ($x2 - 15), ($y2 - 15), 30, 30)
$rect2 = New-Object System.Drawing.RectangleF(($x2 - 15), ($y2 - 15), 30, 30)
$graphics.DrawString("H", $font, $textBrush, $rect2, $format)

# Sensor 3 - Voltage (V)
$x3 = 161
$y3 = 170
$graphics.FillEllipse($whiteBrush, ($x3 - 15), ($y3 - 15), 30, 30)
$rect3 = New-Object System.Drawing.RectangleF(($x3 - 15), ($y3 - 15), 30, 30)
$graphics.DrawString("V", $font, $textBrush, $rect3, $format)

# Draw "HWG" text at bottom
$largeFont = New-Object System.Drawing.Font("Arial", 26, [System.Drawing.FontStyle]::Bold)
$rect = New-Object System.Drawing.RectangleF(0, 200, $size, 40)
$graphics.DrawString("HWG", $largeFont, $whiteBrush, $rect, $format)

# Save the image
$outputPath = "custom_components\hwgroup\icon.png"
$bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)

# Cleanup
$graphics.Dispose()
$bitmap.Dispose()

Write-Host "✅ Icon created successfully: $outputPath" -ForegroundColor Green
Write-Host "   Size: ${size}x${size} pixels" -ForegroundColor Gray
Write-Host "   Format: PNG" -ForegroundColor Gray
