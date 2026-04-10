<!-- i18n-source: CONTRIBUTING.md -->
<!-- i18n-date: 2026-04-10 -->

# Contribuir para repo-translator

Obrigado pelo interesse. Este guia cobre o processo e os padrões para fazer alterações.

## Tipos de contribuições

- **Correções de bugs** — Resolver problemas com escaneamento, validação ou âncoras
- **Novas verificações** — Adicionar verificações que detectem problemas reais de tradução
- **Suporte a idiomas** — Adicionar glossários, testar novos idiomas
- **Documentação** — Melhorar explicações, adicionar exemplos
- **Traduções** — Traduzir a documentação do projeto usando a própria ferramenta

## Início

```bash
git clone https://github.com/edocltd/repo-translator.git
cd repo-translator
git checkout -b your-branch-name
```

Sem dependências externas para scripts principais.

## Padrões de código

- Python 3.10+ com anotações de tipo modernas
- Funções com docstrings
- Sem código morto ou imports não utilizados
- Sem caminhos codificados — usar objetos `Path`
- Sem funções placeholder ou código comentado

## Mensagens de commit

Seguir conventional commits: `type(scope): description`

Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob MIT.
