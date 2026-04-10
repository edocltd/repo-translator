<!-- i18n-source: docs/failure-analysis.md -->
<!-- i18n-date: 2026-04-10 -->

# Análise de Falhas: 48 Problemas Reais na Tradução de Repositórios

Cada problema documentado aqui foi encontrado durante o trabalho real de tradução em [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐). Cada entrada inclui: cenário, nível de risco e defesa implementada.

---

## Categoria 1: Escaneamento e Análise do Repo

### P1.1: Repositório gigante
**Cenário**: Usuário executa a ferramenta em um monorepo com 50.000+ arquivos.
**Defesa**: Limite de arquivos (padrão: 500), limite de profundidade (10 níveis), aviso com sugestão de reduzir o escopo.

### P1.2: Repositório sem git
**Cenário**: Diretório sem `.git/`.
**Defesa**: A ferramenta funciona sem git. Sync-check desativado com aviso. Usa hash de arquivo em vez de SHA de commit.

### P1.3: Estrutura de tradução existente
**Cenário**: Repo já tem diretórios `uk/`, `translations/`, `i18n/`.
**Defesa**: Detecção automática de traduções existentes e exclusão do escaneamento. Relatório do que foi encontrado.

### P1.4: Symlinks e referências circulares
**Defesa**: Não seguir symlinks. Rastrear caminhos visitados via `set(realpath)`.

### P1.5: Arquivos binários com extensão .md
**Defesa**: Verificar os primeiros 8KB para bytes nulos. Se >1% nulos → classificar como binário, pular.

### P1.6: Arquivos .md vazios
**Defesa**: Pular arquivos <10 bytes. Pular arquivos com apenas frontmatter (sem prosa).

### P1.7: Mesmo nome de arquivo em diretórios diferentes
**Defesa**: Sempre preservar a estrutura completa de diretórios. Nunca achatar.

---

## Categoria 2: Qualidade da Tradução (Saída da IA)

### P2.1: IA encurta o arquivo ⚠️ CRÍTICO
**Caso real**: Original 1945 linhas, IA retornou 540 (58% perdido).
**Defesa**: Verificar contagem de linhas após tradução. Rejeitar se <85% do original.

### P2.2: IA traduz blocos de código ⚠️ CRÍTICO
**Caso real**: `mkdir -p .claude/commands` virou `створити_каталог .claude/commands`.
**Defesa**: Extrair blocos de código como marcadores ANTES de enviar à IA. Restaurar DEPOIS. Código nunca passa pela IA.

### P2.3: IA traduz rótulos Mermaid
**Defesa**: Tratar blocos Mermaid como blocos de código (extração de marcadores).

### P2.4: IA altera formatação Markdown
**Defesa**: Validar contagem de cabeçalhos, linhas de tabela, marcadores negrito/itálico contra o original.

### P2.5: IA inventa URLs
**Defesa**: Extrair URLs do original e da tradução. Reportar URLs adicionadas/removidas.

### P2.6: IA remove tags HTML
**Defesa**: Extrair HTML como marcadores (como blocos de código).

### P2.7: IA adiciona notas do tradutor
**Defesa**: Regra de prompt: "NÃO adicionar notas." Validação: buscar padrões "note:", "translator".

### P2.8: Arquivo grande excede o contexto ⚠️ CRÍTICO
**Caso real**: Arquivo de 87KB / 3136 linhas.
**Defesa**: Dividir por cabeçalhos `##`. Se a seção ainda for grande demais → dividir por `###`. Cada fragmento recebe o mesmo glossário e regras.

### P2.9: IA retorna resposta truncada
**Defesa**: Verificar se a última linha é uma frase completa. Verificar se a contagem de code fences é par (todos os blocos fechados).

---

## Categoria 3: Links e Âncoras

### P3.1: Âncoras quebradas após tradução ⚠️ CRÍTICO
**Caso real**: `[See below](#slash-commands)` mas o cabeçalho agora é `## Слеш-команди` → âncora é `#слеш-команди`.
**Defesa**: Após tradução, coletar todos os cabeçalhos → gerar âncoras → comparar com links → auto-corrigir discrepâncias.

### P3.2: Variantes de apóstrofe em âncoras ⚠️ CRÍTICO
**Caso real**: Cabeçalho usa `'` (U+0027) que é removido na âncora, mas o link usa `ʼ` (U+02BC) que é mantido → discrepância.
**Defesa**: Normalizar todas as variantes de apóstrofe ao comparar âncoras.

### P3.3: Cabeçalhos duplicados
**Caso real**: Dois cabeçalhos `## Prompt-хуки`. GitHub adiciona sufixo `-1` ao segundo. O validador não tratava isso.
**Defesa**: Rastrear contador de cabeçalhos. Gerar sufixos `-1`, `-2` para duplicatas.

### P3.4: Links relativos para arquivos não traduzidos
**Cenário**: `translations/uk/docs/guide.md` linka para `../src/deploy.sh` que não existe nesse caminho.
**Defesa**: Reescrever links relativos: se o alvo está traduzido → manter link local. Se não → reescrever para o original.

### P3.5: Caminhos absolutos
**Defesa**: Detectar e avisar. Não reescrever automaticamente (comportamento específico do framework).

### P3.6: Links de âncora entre arquivos
**Cenário**: `[See](other.md#section)` onde `other.md` está traduzido → `#section` pode virar `#секція`.
**Defesa**: Primeiro resolver o arquivo alvo, depois verificar âncoras na versão correta.

---

## Categoria 4: Codificação e Formato de Arquivo

### P4.1: Arquivo não é UTF-8 ⚠️ CRÍTICO
**Caso real**: IA retornou CP1251 parcial em arquivo UTF-8. 240 bytes inválidos.
**Defesa**: Verificar UTF-8 após cada escrita. Auto-reparo: detectar faixas de bytes incorretos, tentar recodificação CP1251 → UTF-8.

### P4.2: BOM (Byte Order Mark)
**Defesa**: Ignorar BOM na leitura. Nunca escrever BOM.

### P4.3: CRLF vs LF
**Defesa**: Corresponder aos finais de linha do original. Padrão LF.

### P4.4: Quebra de linha final ausente
**Defesa**: Sempre adicionar `\n` no final do arquivo.

### P4.5: Caracteres Unicode invisíveis
**Defesa**: Remover U+200B (espaço de largura zero), U+200C, U+200D, U+200E, U+200F após tradução.

---

## Categoria 5: Problemas Específicos do Idioma

### P5.1: Idiomas RTL (árabe, hebraico)
**Defesa**: Aviso na inicialização. Suporte Markdown limitado para RTL.

### P5.2: Idiomas CJK (chinês, japonês, coreano)
**Defesa**: Ajustar tolerância de contagem de linhas (texto CJK é mais curto). Usar contagem de blocos de código como verificação estrutural primária.

### P5.3: Capitalização especial (turco İ/ı)
**Defesa**: Usar comparação Unicode (`str.casefold()`).

### P5.4: Glossário por idioma
**Defesa**: Glossário gerado por idioma. Banco de dados de termos integrado para 10-15 idiomas populares.

---

## Categoria 6: Frontmatter e Metadados

### P6.1: Frontmatter YAML quebra na tradução
**Defesa**: Parsear YAML separadamente. Traduzir apenas o campo `description`. Sempre colocar valores entre aspas após tradução.

### P6.2: Frontmatter duplo
**Defesa**: Apenas o primeiro bloco `---...---` no início do arquivo é frontmatter.

### P6.3: Blocos delimitados por til (`~~~~`)
**Defesa**: Tratar tanto ` ``` ` quanto `~~~~` como marcadores de blocos de código.

---

## Categoria 7: Sistema de Arquivos

### P7.1: Sem permissões de escrita
**Defesa**: Verificar acesso de escrita antes de começar.

### P7.2: Disco cheio
**Defesa**: Estimar espaço necessário (2× tamanho dos .md fonte). Verificar espaço livre.

### P7.3: Caminhos longos (limite Windows 260 caracteres)
**Defesa**: Avisar se o caminho resultante >250 caracteres.

### P7.4: Caracteres especiais em nomes de arquivo
**Defesa**: Preservar nomes originais. Usar objetos `Path`, não concatenação de strings.

### P7.5: Sensibilidade a maiúsculas/minúsculas
**Defesa**: Usar nomes de arquivo originais exatos. Avisar sobre duplicatas que diferem apenas em maiúsculas/minúsculas.

---

## Categoria 8: Git e Controle de Versão

### P8.1: Diff enorme
**Defesa**: Recomendar divisão em PRs por lotes segundo prioridade.

### P8.2: Conflitos de merge
**Defesa**: Cada idioma é um subdiretório separado → sem conflitos entre idiomas.

### P8.3: Squash merge perde rastreamento de SHA
**Defesa**: Fallback para busca baseada em data quando SHA não é encontrado no histórico.

---

## Categoria 9: Configuração

### P9.1: YAML inválido na configuração
**Defesa**: Validar ao carregar. Fallback para valores padrão com aviso.

### P9.2: Código de idioma desconhecido
**Defesa**: Validar contra ISO 639-1. Correspondência aproximada: "ukr" → "Você quis dizer uk?"

### P9.3: Conflitos de glossário
**Defesa**: Verificar traduções conflitantes de palavras raiz ao carregar. Avisar.

---

## Categoria 10: Casos Limite

### P10.1: Arquivo que contém apenas tabelas
**Defesa**: Processar tabelas linha por linha. Verificar contagem de `|` por linha contra o original.

### P10.2: Markdown com HTML inline
**Defesa**: Tags HTML → marcadores. Traduzir texto entre tags, não atributos.

### P10.3: Fórmulas LaTeX
**Defesa**: Detectar `$...$` e `$$...$$`. Extrair como marcadores.

### P10.4: Emoji em cabeçalhos
**Defesa**: Remover emoji ao gerar âncoras (corresponde ao comportamento do GitHub).

### P10.5: Arquivo sem cabeçalhos
**Defesa**: Dividir por linhas em branco em vez de `##`. Se <4000 tokens → traduzir arquivo inteiro.

### P10.6: Metadados i18n duplicados
**Defesa**: Verificar metadados existentes antes de adicionar. Atualizar, não duplicar.

### P10.7: Traduzir traduções ⚠️ CRÍTICO
**Defesa**: SEMPRE excluir `translations_dir` do escaneamento. Verificar que origem ≠ diretório alvo.

### P10.8: Inclusão/exclusão recursiva
**Defesa**: `exclude: ["**/CHANGELOG.md"]` exclui em qualquer diretório. `exclude: ["CHANGELOG.md"]` apenas na raiz.

---

## Resumo das Defesas

### Automáticas (sem ação do usuário):
| Defesa | Quando | Ação |
|--------|--------|------|
| Verificação UTF-8 | Após cada escrita | Auto-reparo ou rejeição |
| Marcadores de blocos de código | Durante tradução | Código nunca passa pela IA |
| Verificação de contagem de linhas | Após tradução | Rejeitar se <85% |
| Correção de âncoras | Após tradução | Auto-substituição de âncoras quebradas |
| Reescrita de links | Durante criação de arquivo | Auto-reescrita de caminhos relativos |
| Quebra de linha final | Na escrita | Auto-adição |
| Remoção de Unicode invisível | Após tradução | Auto-remoção |
| Deduplicação de metadados | Na adição de header | Atualizar em vez de duplicar |

### Avisos (requerem atenção do usuário):
| Defesa | Quando | Mensagem |
|--------|--------|---------|
| Repo grande | No escaneamento | "12.847 arquivos, recomenda-se reduzir escopo" |
| Traduções existentes | Na inicialização | "uk/ encontrado, importar?" |
| Discrepância de glossário | Na validação | "hook traduzido como гачок (1x)" |
| Idioma RTL | Na inicialização | "Requer atenção extra" |
| Caminhos absolutos | No escaneamento | "Não podem ser reescritos automaticamente" |

### Bloqueantes (parar processo):
| Defesa | Quando | Razão |
|--------|--------|-------|
| Arquivo encurtado >15% | Após tradução | IA perdeu conteúdo |
| Desajuste na contagem de blocos de código | Após tradução | Estrutura quebrada |
| Origem = diretório alvo | Na inicialização | Traduziria traduções |
| Sem permissões de escrita | Na inicialização | Não pode salvar |

---

## Prioridade de Implementação

### MVP (implementado):
1. ✅ Validação UTF-8 (P4.1)
2. ✅ Verificação de contagem de linhas (P2.1)
3. ✅ Verificação de contagem de blocos de código (P2.1)
4. ✅ Auto-correção de âncoras (P3.1, P3.2, P3.3)
5. ✅ Exclusão do diretório de traduções (P10.7)
6. ✅ Auto-detecção de traduções existentes (P1.3)

### Próximo (planejado):
7. Extração de marcadores de blocos de código (P2.2)
8. Extração de marcadores HTML (P2.6)
9. Verificação de glossário (P5.4)
10. Tratamento de frontmatter (P6.1)
11. Divisão de arquivos grandes (P2.8)
12. Reescrita de links relativos (P3.4)

### Futuro:
13. Suporte RTL (P5.1)
14. Coeficientes CJK (P5.2)
15. Marcadores LaTeX (P10.3)
16. Memória de tradução
