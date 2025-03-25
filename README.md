# Administrador_Contraseñas_Cifradas


''Posibles mejoras

La implementación de estas mejoras de seguridad es totalmente viable y te detallo cada una con su nivel de complejidad:

### 1. **Borrado seguro de contraseñas temporales** (Complejidad: Media-Baja)
- **Implementación**: Usar arrays de bytes mutables en lugar de strings (que son inmutables y permanecen en memoria)
- **Beneficio**: Las contraseñas no quedan residentes en memoria
- **Desafío**: Requiere cambios en el manejo de strings en el código
- **Herramientas**: `bytearray` en Python + overwrite explícito

### 2. **Sistema de permisos mínimos en BD** (Complejidad: Media)
- **Implementación**:
  - Crear usuario de BD con permisos solo CRUD necesarios
  - Revocar permisos a tablas del sistema
- **Beneficio**: Limita daño en caso de inyección SQL
- **Desafío**: Requiere configuración manual inicial
- **SQL Ejemplo**: 
```sql
CREATE USER 'passmanager'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE ON database.credentials TO 'passmanager'@'localhost';
```

### 3. **Ocultar contraseñas en memoria** (Complejidad: Media-Alta)
- **Implementación**:
  - Usar librerías especializadas como `keyring`
  - Almacenar en estructuras no paginables
- **Beneficio**: Previene lectura desde swap/volcados memoria
- **Desafío**: Requiere dependencias externas en Python

### 4. **Guardar admin key en archivo separado** (Complejidad: Baja)
- **Implementación**:
  - Dividir la clave en 2 partes (archivo + variable entorno)
  - Usar `configparser` para manejo seguro
- **Beneficio**: Defense in depth
- **Ejemplo Estructura**:
```
/passwd/
  ├── passwords.db
  ├── secret.key (clave cifrado)
  └── admin.key (hash admin separado)
```

### 5. **Bloqueo después de 5 intentos** (Complejidad: Media)
- **Implementación**:
  - Tabla de intentos fallidos con timestamp
  - Temporizador progresivo (ej. 2^n segundos)
- **Beneficio**: Previene fuerza bruta
- **SQL sugerido**:
```sql
CREATE TABLE login_attempts (
  ip VARCHAR(45),
  attempts INT,
  last_attempt DATETIME,
  locked_until DATETIME
);
```

### Viabilidad General:
| Mejora            | Tiempo Estimado | Riesgo Implementación | Impacto Seguridad |
|-------------------|-----------------|-----------------------|-------------------|
| Borrado seguro    | 2-3 horas       | Bajo                  | Alto              |
| Permisos BD       | 1-2 horas       | Medio                 | Medio-Alto        |
| Ocultar memoria   | 4-5 horas       | Alto                  | Medio             |
| Admin key separada| 1 hora          | Bajo                  | Medio             |
| Bloqueo intentos  | 3-4 horas       | Medio                 | Alto              |

### Recomendación de Implementación:
1. **Primera Fase** (Seguridad básica reforzada):
   - Admin key separada + Bloqueo por intentos
   - Estas son las de mayor impacto/relación esfuerzo-beneficio

2. **Segunda Fase** (Protección avanzada):
   - Borrado seguro + Permisos BD
   - Requieren más cambios pero mejoran significativamente

3. **Tercera Fase** (Protección memoria):
   - Ocultar contraseñas en memoria
   - Más compleja pero útil si manejas datos muy sensibles

4 aplicar salting
