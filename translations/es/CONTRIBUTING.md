<!-- i18n-source: CONTRIBUTING.md -->
<!-- i18n-date: 2026-04-10 -->

# Contribuir a repo-translator

Gracias por tu interés en contribuir. Esta guía cubre el proceso y los estándares para realizar cambios.

## Tipos de contribuciones

- **Correcciones de errores** — Solucionar problemas con escaneo, validación o anclas
- **Nuevas verificaciones** — Agregar verificaciones que detecten problemas reales de traducción
- **Soporte de idiomas** — Agregar glosarios, probar en nuevos idiomas, corregir problemas específicos
- **Documentación** — Mejorar explicaciones, agregar ejemplos, corregir errores
- **Traducciones** — Traducir la documentación del proyecto usando la propia herramienta

## Inicio

```bash
git clone https://github.com/edocltd/repo-translator.git
cd repo-translator
git checkout -b your-branch-name
```

No se requieren dependencias externas para los scripts principales.

## Estándares de código

### Python

- Python 3.10+ (usar `list[str]` no `List[str]`, `str | None` no `Optional[str]`)
- Funciones con docstrings explicando su propósito
- Sin importaciones no utilizadas ni código muerto
- Sin rutas codificadas — usar objetos `Path`

### Sin código vacío

- Sin funciones placeholder
- Sin bloques de código comentados
- Sin `pass` excepto en métodos abstractos
- Sin comentarios TODO sin issue vinculado

## Mensajes de commit

Seguir conventional commits: `type(scope): description`

Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Licencia

Al contribuir, aceptas que tus contribuciones se licencian bajo MIT.
