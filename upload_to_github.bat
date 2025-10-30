@echo off
chcp 65001 >nul
echo Subiendo Traiden Pro a GitHub...

:: Verificar que Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no está instalado.
    echo Descarga Git desde: https://git-scm.com/
    pause
    exit /b 1
)

:: Inicializar repositorio
cd /d "C:\Traiden_Pro"
git init

:: Configurar usuario (reemplaza con tus datos)
git config user.email "tu-email@ejemplo.com"
git config user.name "Tu Nombre"

:: Agregar archivos
git add .

:: Hacer commit
git commit -m "Deploy Traiden Pro v2.1 - Streamlit Cloud Ready"

:: Preguntar por la URL de GitHub
set /p repo_url="Ingresa la URL de tu repositorio GitHub (ej: https://github.com/tu-usuario/traiden-pro.git): "

:: Agregar remote y subir
git remote add origin %repo_url%
git branch -M main
git push -u origin main

echo.
echo ✅ PROYECTO SUBIDO A GITHUB EXITOSAMENTE!
echo.
echo Ahora ve a: https://share.streamlit.io/
echo y despliega desde tu repositorio.
echo.
pause
