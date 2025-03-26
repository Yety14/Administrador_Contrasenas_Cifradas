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



# Me queda:

Mejorar la instalación (que sea un exe y listo)
	Dificultad: Media
	Descripción: Utilizar herramientas como PyInstaller o cx_Freeze para empaquetar la aplicación en un ejecutable. Puede requerir ajustes en la configuración y pruebas para asegurar que todas las dependencias se incluyan correctamente.

Generador de Contraseñas Seguras
	Dificultad: Baja
	Descripción: Crear una función que genere contraseñas aleatorias con opciones para incluir caracteres especiales, números y mayúsculas. Esto puede hacerse utilizando la biblioteca random.

Exportar e Importar Credenciales
	Dificultad: Media
	Descripción: Implementar funciones para exportar las credenciales a un archivo (CSV o JSON) y para importar desde un archivo. Esto requiere manejo de archivos y posiblemente validación de datos.

Implementar un log
	Dificultad: Media
	Descripción: Crear un sistema de registro que almacene eventos importantes (como intentos de inicio de sesión, cambios de contraseña, etc.). Esto puede hacerse utilizando la biblioteca logging de Python.

Verificación de Seguridad
	Dificultad: Media
	Descripción: Integrar una API como "Have I Been Pwned" para verificar si las contraseñas han sido comprometidas. Esto implica hacer solicitudes HTTP y manejar respuestas JSON.

Interfaz de Usuario Mejorada
	Dificultad: Alta
	Descripción: Rediseñar la interfaz utilizando gráficos, iconos atractivos y una mejor disposición de los elementos. Esto puede requerir un cambio significativo en el diseño y posiblemente el uso de un framework de diseño como Material Design.

Soporte Multilingüe
	Dificultad: Media
	Descripción: Implementar un sistema que permita la traducción de la interfaz a diferentes idiomas. Esto puede hacerse utilizando archivos de recursos o bibliotecas como gettext.

2FA (Autenticación de Dos Factores)
	Dificultad: Alta
	Descripción: Implementar un sistema de autenticación de dos factores, que puede incluir el uso de aplicaciones de autenticación o SMS. Esto requiere una comprensión de la seguridad y posiblemente la integración con servicios externos.

Modo oscuro automático
	Dificultad: Media
	Descripción: Implementar un modo oscuro que se active automáticamente según la hora del día o la configuración del sistema operativo. Esto implica cambios en la lógica de la interfaz y posiblemente el uso de bibliotecas adicionales.

Análisis de Fuerza de Contraseña
	Dificultad: Media
	Descripción: Crear una función que evalúe la fuerza de las contraseñas ingresadas y sugiera mejoras. Esto puede hacerse utilizando reglas simples (longitud, variedad de caracteres) y puede requerir pruebas adicionales.