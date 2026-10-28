# Sistema de Asistencia — CFP Nº1

Aplicación de gestión de asistencia desarrollada con **Python, FastAPI, SQLAlchemy y SQLite**.

## Requisitos previos

- Tener Python instalado.
- Tener conexión a Internet durante la instalación de las dependencias.
- Descargar la carpeta del proyecto.

## 1. Preparar el entorno

Abrir PowerShell dentro de la carpeta del proyecto y ejecutar los siguientes comandos, uno por uno:

### Crear el entorno virtual

```powershell
python -m venv .venv
```

### Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución del script, ejecutar:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Confirmar si lo solicita y volver a activar el entorno virtual.

### Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

**Importante:** el archivo `requirements.txt` debe estar en la carpeta del proyecto.

## 2. Ejecutar el servidor

Con el entorno virtual activado, ejecutar:

```powershell
python -m uvicorn main:app --reload
```

Mientras el servidor esté funcionando, mantener abierta la terminal.

## 3. Acceder a la aplicación

Abrir el navegador y utilizar las siguientes direcciones:

- **API:** http://127.0.0.1:8000
- **Documentación interactiva:** http://127.0.0.1:8000/docs

Desde la documentación interactiva se pueden consultar y probar los endpoints disponibles.

## 4. Próximas ejecuciones

Una vez instalado el proyecto, no es necesario volver a instalar las dependencias cada vez.

Abrir PowerShell dentro de la carpeta y ejecutar:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

## 5. Detener el servidor

Para detener el servidor, volver a la terminal y presionar:

```text
Ctrl + C
```

## Consideraciones

- Cada integrante debe crear su propio entorno virtual.
- No es necesario compartir la carpeta `.venv`.
- La base de datos SQLite se crea localmente en el proyecto.
- Si se comparte una base de datos con información de prueba, evitar modificar o sobrescribir datos de otros integrantes.
- Si se realizan cambios en el código mientras el servidor está activo con `--reload`, normalmente se reinicia automáticamente.
