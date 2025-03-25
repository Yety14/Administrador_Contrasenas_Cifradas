# Gestor de Contraseñas Seguro

## Descripción
Este proyecto es un gestor de contraseñas seguro desarrollado en Python con una interfaz gráfica creada con Tkinter. Permite almacenar, recuperar, listar y eliminar credenciales de manera segura utilizando cifrado, autenticación de administrador y salting para mejorar la seguridad.

## Características
- Interfaz gráfica intuitiva con Tkinter.
- Cifrado de contraseñas usando `cryptography.fernet`.
- Autenticación con contraseña de administrador.
- Salting de contraseñas para protección adicional en el almacenamiento.
- Protección contra ataques de fuerza bruta con bloqueo tras intentos fallidos.
- Almacenamiento seguro en SQLite.
- Recuperación y gestión de contraseñas mediante una clave de administrador.

## Requisitos
- Python 3.x
- Módulos necesarios:
  - `tkinter`
  - `sqlite3`
  - `cryptography`
  - `hashlib`

Para instalar las dependencias necesarias, ejecuta:
```sh
pip install cryptography
```

## Instalación y Ejecución
1. Clona el repositorio o descarga el código fuente.
2. Asegúrate de que tienes Python 3 instalado.
3. Ejecuta el siguiente comando para iniciar la aplicación:
   ```sh
   python main.py
   ```
4. En la primera ejecución, se solicitará la creación de una contraseña de administrador.

## Uso
- **Guardar/Actualizar contraseñas:** Ingresa el usuario, sitio/aplicación y contraseña.
- **Recuperar contraseñas:** Proporciona el usuario, sitio y la contraseña de administrador.
- **Listar credenciales:** Introduce la contraseña de administrador para ver todas las credenciales almacenadas.
- **Eliminar credenciales:** Introduce el usuario, sitio y la contraseña de administrador para borrar una credencial.

## Seguridad
- **Salting**: Las contraseñas se almacenan con un **salt** único y se hashean utilizando el algoritmo PBKDF2 para aumentar la seguridad.
- Las contraseñas se almacenan de forma cifrada.
- Se protege la autenticación con un sistema de bloqueo tras varios intentos fallidos.
- La base de datos y las claves están protegidas con permisos adecuados.

## Contribución
Si deseas mejorar este proyecto, puedes realizar un fork y enviar pull requests con mejoras o correcciones.

## Licencia
Este proyecto se distribuye bajo la licencia MIT.

---

### Posibles mejoras

La implementación de estas mejoras de seguridad es totalmente viable y te detallo cada una con su nivel de complejidad:

1. **Borrado seguro de contraseñas temporales** (Complejidad: Media-Baja)
   - Implementación: Usar arrays de bytes mutables en lugar de strings (que son inmutables y permanecen en memoria).
   - Beneficio: Las contraseñas no quedan residentes en memoria.
   - Desafío: Requiere cambios en el manejo de strings en el código.
   - Herramientas: `bytearray` en Python + overwrite explícito.

2. **Sistema de permisos mínimos en BD** (Complejidad: Media)
   - Implementación:
     - Crear usuario de BD con permisos solo CRUD necesarios.
     - Revocar permisos a tablas del sistema.
   - Beneficio: Limita daño en caso de inyección SQL.
   - Desafío: Requiere configuración manual inicial.
   - SQL Ejemplo:
   ```sql
   CREATE USER 'passmanager'@'localhost' IDENTIFIED BY 'password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON database.credentials TO 'passmanager'@'localhost';
   ```

3. **Ocultar contraseñas en memoria** (Complejidad: Media-Alta)
   - Implementación: Usar librerías especializadas como `keyring`. Almacenar en estructuras no paginables.
   - Beneficio: Previene lectura desde swap/volcados de memoria.
   - Desafío: Requiere dependencias externas en Python.

4. **Guardar admin key en archivo separado** (Complejidad: Baja)
   - Implementación:
     - Dividir la clave en 2 partes (archivo + variable entorno).
     - Usar `configparser` para manejo seguro.
   - Beneficio: Defense in depth.
   - Ejemplo Estructura:
     ```
     /passwd/
       ├── passwords.db
       ├── secret.key (clave cifrado)
       └── admin.key (hash admin separado)
     ```

5. **Bloqueo después de 5 intentos** (Complejidad: Media)
   - Implementación:
     - Tabla de intentos fallidos con timestamp.
     - Temporizador progresivo (ej. 2^n segundos).
   - Beneficio: Previene ataques de fuerza bruta.
   - SQL sugerido:
   ```sql
   CREATE TABLE login_attempts (
     ip VARCHAR(45),
     attempts INT,
     last_attempt DATETIME,
     locked_until DATETIME
   );
   ```

### Viabilidad General:
| Mejora               | Tiempo Estimado | Riesgo Implementación | Impacto Seguridad |
|----------------------|-----------------|-----------------------|-------------------|
| **Borrado seguro**    | 2-3 horas       | Bajo                  | Alto              |
| **Permisos BD**       | 1-2 horas       | Medio                 | Medio-Alto        |
| **Ocultar memoria**   | 4-5 horas       | Alto                  | Medio             |
| **Admin key separada**| 1 hora          | Bajo                  | Medio             |
| **Bloqueo intentos**  | 3-4 horas       | Medio                 | Alto              |

### Recomendación de Implementación:
#### **Primera Fase (Seguridad básica reforzada):**
- Admin key separada + Bloqueo por intentos.
- Estas son las de mayor impacto/relación esfuerzo-beneficio.

#### **Segunda Fase (Protección avanzada):**
- Borrado seguro + Permisos BD.
- Requieren más cambios pero mejoran significativamente.

#### **Tercera Fase (Protección memoria):**
- Ocultar contraseñas en memoria.
- Más compleja pero útil si manejas datos muy sensibles.