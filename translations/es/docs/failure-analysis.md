<!-- i18n-source: docs/failure-analysis.md -->
<!-- i18n-date: 2026-04-10 -->

# Análisis de Errores: 48 Problemas Reales en la Traducción de Repositorios

Cada problema documentado aquí fue encontrado durante el trabajo real de traducción en [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐). Cada entrada incluye: escenario, nivel de riesgo y defensa implementada.

---

## Categoría 1: Escaneo y Análisis del Repo

### P1.1: Repositorio gigante
**Escenario**: El usuario ejecuta la herramienta en un monorepo con 50.000+ archivos.
**Defensa**: Límite de archivos (por defecto: 500), límite de profundidad (10 niveles), advertencia con sugerencia de reducir el alcance.

### P1.2: Repositorio sin git
**Escenario**: Directorio sin `.git/`.
**Defensa**: La herramienta funciona sin git. Sync-check desactivado con advertencia. Usa hash de archivo en lugar de SHA de commit.

### P1.3: Estructura de traducción existente
**Escenario**: El repo ya tiene directorios `uk/`, `translations/`, `i18n/`.
**Defensa**: Detección automática de traducciones existentes y exclusión del escaneo. Reporte de lo encontrado.

### P1.4: Symlinks y referencias circulares
**Defensa**: No seguir symlinks. Rastrear rutas visitadas mediante `set(realpath)`.

### P1.5: Archivos binarios con extensión .md
**Defensa**: Verificar los primeros 8KB para bytes nulos. Si >1% nulos → clasificar como binario, omitir.

### P1.6: Archivos .md vacíos
**Defensa**: Omitir archivos <10 bytes. Omitir archivos con solo frontmatter (sin prosa).

### P1.7: Mismo nombre de archivo en diferentes directorios
**Defensa**: Siempre preservar la estructura completa de directorios. Nunca aplanar.

---

## Categoría 2: Calidad de Traducción (Salida de IA)

### P2.1: La IA acorta el archivo ⚠️ CRÍTICO
**Caso real**: Original 1945 líneas, la IA devolvió 540 (58% perdido).
**Defensa**: Verificar conteo de líneas después de la traducción. Rechazar si <85% del original.

### P2.2: La IA traduce bloques de código ⚠️ CRÍTICO
**Caso real**: `mkdir -p .claude/commands` se convirtió en `створити_каталог .claude/commands`.
**Defensa**: Extraer bloques de código como marcadores ANTES de enviar a la IA. Restaurar DESPUÉS. El código nunca pasa por la IA.

### P2.3: La IA traduce etiquetas de Mermaid
**Defensa**: Tratar bloques Mermaid como bloques de código (extracción de marcadores).

### P2.4: La IA cambia el formato Markdown
**Defensa**: Validar conteo de encabezados, filas de tabla, marcadores bold/italic contra el original.

### P2.5: La IA inventa URLs
**Defensa**: Extraer URLs del original y la traducción. Reportar URLs añadidas/eliminadas.

### P2.6: La IA elimina etiquetas HTML
**Defensa**: Extraer HTML como marcadores (como bloques de código).

### P2.7: La IA añade notas del traductor
**Defensa**: Regla de prompt: "NO añadir notas." Validación: buscar patrones "note:", "translator".

### P2.8: Archivo grande excede el contexto ⚠️ CRÍTICO
**Caso real**: Archivo de 87KB / 3136 líneas.
**Defensa**: Dividir por encabezados `##`. Si la sección sigue siendo demasiado grande → dividir por `###`. Cada fragmento recibe el mismo glosario y reglas.

### P2.9: La IA devuelve respuesta truncada
**Defensa**: Verificar si la última línea es una oración completa. Verificar si el conteo de code fences es par (todos los bloques cerrados).

---

## Categoría 3: Enlaces y Anclas

### P3.1: Anclas rotas después de la traducción ⚠️ CRÍTICO
**Caso real**: `[See below](#slash-commands)` pero el encabezado ahora es `## Слеш-команди` → ancla es `#слеш-команди`.
**Defensa**: Después de la traducción, recopilar todos los encabezados → generar anclas → comparar con enlaces → auto-corregir discrepancias.

### P3.2: Variantes de apóstrofe en anclas ⚠️ CRÍTICO
**Caso real**: Encabezado usa `'` (U+0027) que se elimina en el ancla, pero el enlace usa `ʼ` (U+02BC) que se mantiene → discrepancia.
**Defensa**: Normalizar todas las variantes de apóstrofe al comparar anclas.

### P3.3: Encabezados duplicados
**Caso real**: Dos encabezados `## Prompt-хуки`. GitHub añade sufijo `-1` al segundo. El validador no manejaba esto.
**Defensa**: Rastrear contador de encabezados. Generar sufijos `-1`, `-2` para duplicados.

### P3.4: Enlaces relativos a archivos no traducidos
**Escenario**: `translations/uk/docs/guide.md` enlaza a `../src/deploy.sh` que no existe en esa ruta.
**Defensa**: Reescribir enlaces relativos: si el destino está traducido → mantener enlace local. Si no → reescribir al original.

### P3.5: Rutas absolutas
**Defensa**: Detectar y advertir. No reescribir automáticamente (comportamiento específico del framework).

### P3.6: Enlaces de ancla entre archivos
**Escenario**: `[See](other.md#section)` donde `other.md` está traducido → `#section` puede convertirse en `#секція`.
**Defensa**: Primero resolver el archivo destino, luego verificar anclas en la versión correcta.

---

## Categoría 4: Codificación y Formato de Archivo

### P4.1: Archivo no es UTF-8 ⚠️ CRÍTICO
**Caso real**: La IA devolvió CP1251 parcial en archivo UTF-8. 240 bytes inválidos.
**Defensa**: Verificar UTF-8 después de cada escritura. Auto-reparación: detectar rangos de bytes incorrectos, intentar recodificación CP1251 → UTF-8.

### P4.2: BOM (Byte Order Mark)
**Defensa**: Ignorar BOM al leer. Nunca escribir BOM.

### P4.3: CRLF vs LF
**Defensa**: Coincidir con los finales de línea del original. Por defecto LF.

### P4.4: Salto de línea final faltante
**Defensa**: Siempre añadir `\n` al final del archivo.

### P4.5: Caracteres Unicode invisibles
**Defensa**: Eliminar U+200B (espacio de ancho cero), U+200C, U+200D, U+200E, U+200F después de la traducción.

---

## Categoría 5: Problemas Específicos del Idioma

### P5.1: Idiomas RTL (árabe, hebreo)
**Defensa**: Advertencia al inicializar. Soporte limitado de Markdown para RTL.

### P5.2: Idiomas CJK (chino, japonés, coreano)
**Defensa**: Ajustar tolerancia de conteo de líneas (texto CJK es más corto). Usar conteo de bloques de código como verificación estructural primaria.

### P5.3: Mayúsculas/minúsculas especiales (turco İ/ı)
**Defensa**: Usar comparación Unicode-consciente (`str.casefold()`).

### P5.4: Glosario por idioma
**Defensa**: Glosario generado por idioma. Base de datos de términos integrada para 10-15 idiomas populares.

---

## Categoría 6: Frontmatter y Metadatos

### P6.1: Frontmatter YAML se rompe en la traducción
**Defensa**: Parsear YAML por separado. Traducir solo el campo `description`. Siempre entrecomillar valores después de la traducción.

### P6.2: Frontmatter doble
**Defensa**: Solo el primer bloque `---...---` al inicio del archivo es frontmatter.

### P6.3: Bloques con tilde (`~~~~`)
**Defensa**: Manejar tanto ` ``` ` como `~~~~` como marcadores de bloques de código.

---

## Categoría 7: Sistema de Archivos

### P7.1: Sin permisos de escritura
**Defensa**: Verificar acceso de escritura antes de comenzar.

### P7.2: Disco lleno
**Defensa**: Estimar espacio requerido (2× tamaño de .md fuente). Verificar espacio libre.

### P7.3: Rutas largas (límite de 260 caracteres en Windows)
**Defensa**: Advertir si la ruta resultante >250 caracteres.

### P7.4: Caracteres especiales en nombres de archivo
**Defensa**: Preservar nombres originales. Usar objetos `Path`, no concatenación de strings.

### P7.5: Sensibilidad a mayúsculas/minúsculas
**Defensa**: Usar nombres de archivo originales exactos. Advertir sobre duplicados que difieren solo en mayúsculas/minúsculas.

---

## Categoría 8: Git y Control de Versiones

### P8.1: Diff enorme
**Defensa**: Recomendar dividir en PRs por lotes según prioridad.

### P8.2: Conflictos de merge
**Defensa**: Cada idioma es un subdirectorio separado → sin conflictos entre idiomas.

### P8.3: Squash merge pierde rastreo de SHA
**Defensa**: Fallback a búsqueda basada en fecha cuando SHA no se encuentra en el historial.

---

## Categoría 9: Configuración

### P9.1: YAML inválido en configuración
**Defensa**: Validar al cargar. Fallback a valores por defecto con advertencia.

### P9.2: Código de idioma desconocido
**Defensa**: Validar contra ISO 639-1. Coincidencia difusa: "ukr" → "¿Quiso decir uk?"

### P9.3: Conflictos de glosario
**Defensa**: Verificar traducciones conflictivas de palabras raíz al cargar. Advertir.

---

## Categoría 10: Casos Límite

### P10.1: Archivo que solo contiene tablas
**Defensa**: Procesar tablas fila por fila. Verificar conteo de `|` por línea contra el original.

### P10.2: Markdown con HTML inline
**Defensa**: Etiquetas HTML → marcadores. Traducir texto entre etiquetas, no atributos.

### P10.3: Fórmulas LaTeX
**Defensa**: Detectar `$...$` y `$$...$$`. Extraer como marcadores.

### P10.4: Emoji en encabezados
**Defensa**: Eliminar emoji al generar anclas (coincide con el comportamiento de GitHub).

### P10.5: Archivo sin encabezados
**Defensa**: Dividir por líneas en blanco en lugar de `##`. Si <4000 tokens → traducir archivo completo.

### P10.6: Metadatos i18n duplicados
**Defensa**: Verificar metadatos existentes antes de añadir. Actualizar, no duplicar.

### P10.7: Traducir traducciones ⚠️ CRÍTICO
**Defensa**: SIEMPRE excluir `translations_dir` del escaneo. Verificar que origen ≠ directorio destino.

### P10.8: Inclusión/exclusión recursiva
**Defensa**: `exclude: ["**/CHANGELOG.md"]` excluye en cualquier directorio. `exclude: ["CHANGELOG.md"]` solo en raíz.

---

## Resumen de Defensas

### Automáticas (sin acción del usuario):
| Defensa | Cuándo | Acción |
|---------|--------|--------|
| Verificación UTF-8 | Después de cada escritura | Auto-reparación o rechazo |
| Marcadores de bloques de código | Durante traducción | El código nunca pasa por la IA |
| Verificación de conteo de líneas | Después de traducción | Rechazar si <85% |
| Corrección de anclas | Después de traducción | Auto-reemplazo de anclas rotas |
| Reescritura de enlaces | Durante creación de archivo | Auto-reescritura de rutas relativas |
| Salto de línea final | Al escribir | Auto-añadir |
| Eliminación de Unicode invisible | Después de traducción | Auto-eliminar |
| Deduplicación de metadatos | Al añadir header | Actualizar en lugar de duplicar |

### Advertencias (requieren atención del usuario):
| Defensa | Cuándo | Mensaje |
|---------|--------|---------|
| Repo grande | Al escanear | "12.847 archivos, se recomienda reducir alcance" |
| Traducciones existentes | Al inicializar | "¿Encontrado uk/, importar?" |
| Discrepancia de glosario | Al validar | "hook traducido como гачок (1x)" |
| Idioma RTL | Al inicializar | "Requiere atención extra" |
| Rutas absolutas | Al escanear | "No se pueden reescribir automáticamente" |

### Bloqueantes (detener proceso):
| Defensa | Cuándo | Razón |
|---------|--------|-------|
| Archivo acortado >15% | Después de traducción | La IA perdió contenido |
| Desajuste en conteo de bloques de código | Después de traducción | Estructura rota |
| Origen = directorio destino | Al inicializar | Traduciría traducciones |
| Sin permisos de escritura | Al inicializar | No puede guardar |

---

## Prioridad de Implementación

### MVP (implementado):
1. ✅ Validación UTF-8 (P4.1)
2. ✅ Verificación de conteo de líneas (P2.1)
3. ✅ Verificación de conteo de bloques de código (P2.1)
4. ✅ Auto-corrección de anclas (P3.1, P3.2, P3.3)
5. ✅ Exclusión del directorio de traducciones (P10.7)
6. ✅ Auto-detección de traducciones existentes (P1.3)

### Siguiente (planificado):
7. Extracción de marcadores de bloques de código (P2.2)
8. Extracción de marcadores HTML (P2.6)
9. Verificación de glosario (P5.4)
10. Manejo de frontmatter (P6.1)
11. División de archivos grandes (P2.8)
12. Reescritura de enlaces relativos (P3.4)

### Futuro:
13. Soporte RTL (P5.1)
14. Coeficientes CJK (P5.2)
15. Marcadores LaTeX (P10.3)
16. Memoria de traducción
