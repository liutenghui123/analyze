@echo off
chcp 65001 >nul
echo ========================================
echo   Fenxi8 打包工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.13+
    pause
    exit /b 1
)

echo [1/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
for /r %%i in (*.pyc) do del "%%i" 2>nul
echo [完成] 清理完成
echo.

echo [2/4] 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller安装失败
        pause
        exit /b 1
    )
)
echo [完成] PyInstaller已就绪
echo.

echo [3/4] 打包GUI版本...
pyinstaller --clean Fenxi8.spec
if errorlevel 1 (
    echo [错误] GUI版本打包失败
    pause
    exit /b 1
)
echo [完成] GUI版本打包成功
echo.

echo [4/4] 打包CLI版本...
pyinstaller --clean Fenxi8_CLI.spec
if errorlevel 1 (
    echo [错误] CLI版本打包失败
    pause
    exit /b 1
)
echo [完成] CLI版本打包成功
echo.

echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 生成的文件:
dir /B dist\*.exe 2>nul
echo.
echo 文件大小:
for %%i in (dist\*.exe) do echo   %%~nxi: %%~zi bytes
echo.
echo 提示: 查看 "打包说明.md" 了解使用方法
echo.
pause
