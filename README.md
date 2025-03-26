# 🔐 Gestor de Contraseñas Seguro

Un gestor de contraseñas robusto y seguro desarrollado en Python con interfaz gráfica Tkinter. Proporciona almacenamiento, recuperación, listado y eliminación de credenciales con múltiples capas de seguridad.

![Demo](https://via.placeholder.com/800x400?text=Gestor+de+Contraseñas+Demo) <!-- Reemplaza con imagen real -->

## ✨ Características Principales

### 🔒 Seguridad Avanzada
- Cifrado de contraseñas con Fernet (algoritmo de cifrado simétrico)
- Autenticación de administrador con protección contra fuerza bruta
- Sistema de bloqueo tras intentos fallidos de inicio de sesión
- Almacenamiento seguro en base de datos SQLite

### 🖥️ Interfaz de Usuario Intuitiva
- Diseño moderno con pestañas para diferentes funciones
- Gestión completa de credenciales en una sola aplicación
- Feedback visual para todas las operaciones

### 🛡️ Funcionalidades de Seguridad
- Generación de claves de cifrado únicas
- Protección de archivos de configuración con permisos restringidos
- Copiado automático de contraseñas al portapapeles
- Limpieza automática de campos sensibles

## 📋 Requisitos del Sistema

- Python 3.7+
- Bibliotecas requeridas:
  ```
  tkinter
  sqlite3
  cryptography
  hashlib
  ```

## ⚙️ Instalación

### Dependencias
```bash
pip install cryptography
```

### Configuración
1. Clonar el repositorio
2. Asegurar instalación de Python 3.7+
3. Ejecutar la aplicación:
```bash
python gui.py
```

## 📖 Guía de Uso

### Primera Ejecución
- Al iniciar por primera vez, se solicitará crear una contraseña de administrador
- Esta contraseña será crucial para todas las operaciones posteriores

### Funciones Principales

#### Guardar/Actualizar Contraseñas
- Ingresa usuario, sitio/aplicación y contraseña
- Opción de actualizar credenciales existentes

#### Recuperar Contraseñas
- Introduce usuario y sitio
- Requiere contraseña de administrador
- Contraseña se muestra y copia automáticamente al portapapeles

#### Listar Credenciales
- Vista de todas las credenciales almacenadas
- Requiere autenticación de administrador

#### Eliminar Credenciales
- Eliminar credenciales específicas
- Confirmación y autenticación de administrador requeridas

## 🚨 Seguridad Implementada

- Cifrado Fernet para protección de datos
- Salting y hashing de contraseña de administrador
- Bloqueo tras 5 intentos fallidos (duración: 5 minutos)
- Permisos de archivo restringidos
- Limpieza automática de campos sensibles

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:
- Reporta issues en GitHub
- Realiza pull requests con mejoras
- Mantén el enfoque en seguridad y usabilidad

## ⚠️ Disclaimer de Seguridad

- Mantén la contraseña de administrador en un lugar seguro
- No compartas tus credenciales
- Actualiza regularmente tus contraseñas maestras

## 📜 Licencia

Distribuido bajo Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 📩 Contacto

Para soporte o consultas, abre un issue en el repositorio.



Me queda mejorar la instalación(q sea un exe y listo) y Autocompletado de Campos:
Generador de Contraseñas Seguras:
Exportar e Importar Credenciales:
Implementar un log:
Verificación de Seguridad:
	Implementa una función que verifique si las contraseñas almacenadas han sido comprometidas en violaciones de datos conocidas. Puedes usar APIs de servicios como "Have I Been Pwned" para esto.
Interfaz de Usuario Mejorada:
	Mejora la interfaz de usuario con gráficos, iconos más atractivos y una mejor disposición de los elementos. Considera usar un diseño más moderno o incluso un framework de diseño como Material Design.
Soporte Multilingüe:
2FA:
Modo oscuro automatico:
Análisis de Fuerza de Contraseña:
	Proporciona un análisis de la fuerza de las contraseñas ingresadas, sugiriendo mejoras si son demasiado débiles.