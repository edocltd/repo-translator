<!-- i18n-source: docs/failure-analysis.md -->
<!-- i18n-date: 2026-04-10 -->

# Analyse des Erreurs : 48 Problèmes Réels dans la Traduction de Dépôts

Chaque problème documenté ici a été rencontré lors du travail réel de traduction sur [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐). Chaque entrée comprend : scénario, niveau de risque et défense implémentée.

---

## Catégorie 1 : Scan et Analyse du Dépôt

### P1.1 : Dépôt géant
**Scénario** : L'utilisateur lance l'outil sur un monorepo avec 50 000+ fichiers.
**Défense** : Limite de fichiers (par défaut : 500), limite de profondeur (10 niveaux), avertissement avec suggestion de réduire la portée.

### P1.2 : Dépôt sans git
**Scénario** : Répertoire sans `.git/`.
**Défense** : L'outil fonctionne sans git. Sync-check désactivé avec avertissement. Utilise le hash de fichier au lieu du SHA de commit.

### P1.3 : Structure de traduction existante
**Scénario** : Le dépôt a déjà des répertoires `uk/`, `translations/`, `i18n/`.
**Défense** : Détection automatique des traductions existantes et exclusion du scan. Rapport de ce qui a été trouvé.

### P1.4 : Liens symboliques et références circulaires
**Défense** : Ne pas suivre les liens symboliques. Suivre les chemins visités via `set(realpath)`.

### P1.5 : Fichiers binaires avec extension .md
**Défense** : Vérifier les 8 premiers Ko pour les octets nuls. Si >1% de nuls → classer comme binaire, ignorer.

### P1.6 : Fichiers .md vides
**Défense** : Ignorer les fichiers <10 octets. Ignorer les fichiers avec uniquement du frontmatter (pas de prose).

### P1.7 : Même nom de fichier dans différents répertoires
**Défense** : Toujours préserver la structure complète des répertoires. Jamais aplatir.

---

## Catégorie 2 : Qualité de Traduction (Sortie IA)

### P2.1 : L'IA raccourcit le fichier ⚠️ CRITIQUE
**Cas réel** : Original 1945 lignes, l'IA a retourné 540 (58% perdu).
**Défense** : Vérifier le nombre de lignes après traduction. Rejeter si <85% de l'original.

### P2.2 : L'IA traduit les blocs de code ⚠️ CRITIQUE
**Cas réel** : `mkdir -p .claude/commands` est devenu `створити_каталог .claude/commands`.
**Défense** : Extraire les blocs de code comme marqueurs AVANT l'envoi à l'IA. Restaurer APRÈS. Le code ne passe jamais par l'IA.

### P2.3 : L'IA traduit les étiquettes Mermaid
**Défense** : Traiter les blocs Mermaid comme des blocs de code (extraction de marqueurs).

### P2.4 : L'IA modifie le formatage Markdown
**Défense** : Valider le nombre de titres, lignes de tableau, marqueurs gras/italique par rapport à l'original.

### P2.5 : L'IA invente des URLs
**Défense** : Extraire les URLs de l'original et de la traduction. Signaler les URLs ajoutées/supprimées.

### P2.6 : L'IA supprime les balises HTML
**Défense** : Extraire le HTML comme marqueurs (comme les blocs de code).

### P2.7 : L'IA ajoute des notes de traducteur
**Défense** : Règle de prompt : "NE PAS ajouter de notes." Validation : rechercher les motifs "note:", "translator".

### P2.8 : Fichier volumineux dépasse le contexte ⚠️ CRITIQUE
**Cas réel** : Fichier de 87 Ko / 3136 lignes.
**Défense** : Découper par titres `##`. Si la section est encore trop grande → découper par `###`. Chaque fragment reçoit le même glossaire et les mêmes règles.

### P2.9 : L'IA retourne une réponse tronquée
**Défense** : Vérifier si la dernière ligne est une phrase complète. Vérifier si le nombre de clôtures de code est pair (tous les blocs fermés).

---

## Catégorie 3 : Liens et Ancres

### P3.1 : Ancres cassées après traduction ⚠️ CRITIQUE
**Cas réel** : `[See below](#slash-commands)` mais le titre est maintenant `## Слеш-команди` → l'ancre est `#слеш-команди`.
**Défense** : Après traduction, collecter tous les titres → générer les ancres → comparer avec les liens → auto-corriger les écarts.

### P3.2 : Variantes d'apostrophe dans les ancres ⚠️ CRITIQUE
**Cas réel** : Le titre utilise `'` (U+0027) qui est supprimé dans l'ancre, mais le lien utilise `ʼ` (U+02BC) qui est conservé → écart.
**Défense** : Normaliser toutes les variantes d'apostrophe lors de la comparaison des ancres.

### P3.3 : Titres en double
**Cas réel** : Deux titres `## Prompt-хуки`. GitHub ajoute le suffixe `-1` au second. Le validateur ne gérait pas cela.
**Défense** : Suivre le compteur de titres. Générer les suffixes `-1`, `-2` pour les doublons.

### P3.4 : Liens relatifs vers des fichiers non traduits
**Scénario** : `translations/uk/docs/guide.md` pointe vers `../src/deploy.sh` qui n'existe pas à ce chemin.
**Défense** : Réécrire les liens relatifs : si la cible est traduite → garder le lien local. Sinon → réécrire vers l'original.

### P3.5 : Chemins absolus
**Défense** : Détecter et avertir. Ne pas réécrire automatiquement (comportement spécifique au framework).

### P3.6 : Liens d'ancre entre fichiers
**Scénario** : `[See](other.md#section)` où `other.md` est traduit → `#section` peut devenir `#секція`.
**Défense** : D'abord résoudre le fichier cible, puis vérifier les ancres dans la version correcte.

---

## Catégorie 4 : Encodage et Format de Fichier

### P4.1 : Fichier non UTF-8 ⚠️ CRITIQUE
**Cas réel** : L'IA a retourné du CP1251 partiel dans un fichier UTF-8. 240 octets invalides.
**Défense** : Vérifier UTF-8 après chaque écriture. Auto-réparation : détecter les plages d'octets incorrects, tenter le réencodage CP1251 → UTF-8.

### P4.2 : BOM (Byte Order Mark)
**Défense** : Ignorer le BOM en lecture. Ne jamais écrire de BOM.

### P4.3 : CRLF vs LF
**Défense** : Correspondre aux fins de ligne de l'original. Par défaut LF.

### P4.4 : Saut de ligne final manquant
**Défense** : Toujours ajouter `\n` en fin de fichier.

### P4.5 : Caractères Unicode invisibles
**Défense** : Supprimer U+200B (espace de largeur nulle), U+200C, U+200D, U+200E, U+200F après traduction.

---

## Catégorie 5 : Problèmes Spécifiques aux Langues

### P5.1 : Langues RTL (arabe, hébreu)
**Défense** : Avertissement à l'initialisation. Support Markdown limité pour RTL.

### P5.2 : Langues CJK (chinois, japonais, coréen)
**Défense** : Ajuster la tolérance du nombre de lignes (le texte CJK est plus court). Utiliser le nombre de blocs de code comme vérification structurelle principale.

### P5.3 : Casse spéciale (turc İ/ı)
**Défense** : Utiliser une comparaison Unicode (`str.casefold()`).

### P5.4 : Glossaire par langue
**Défense** : Glossaire généré par langue. Base de termes intégrée pour 10-15 langues populaires.

---

## Catégorie 6 : Frontmatter et Métadonnées

### P6.1 : Le frontmatter YAML casse à la traduction
**Défense** : Parser le YAML séparément. Traduire uniquement le champ `description`. Toujours mettre les valeurs entre guillemets après traduction.

### P6.2 : Double frontmatter
**Défense** : Seul le premier bloc `---...---` au début du fichier est du frontmatter.

### P6.3 : Blocs délimités par des tildes (`~~~~`)
**Défense** : Gérer à la fois ` ``` ` et `~~~~` comme marqueurs de blocs de code.

---

## Catégorie 7 : Système de Fichiers

### P7.1 : Pas de droits d'écriture
**Défense** : Vérifier l'accès en écriture avant de commencer.

### P7.2 : Disque plein
**Défense** : Estimer l'espace requis (2× taille des .md source). Vérifier l'espace libre.

### P7.3 : Chemins longs (limite Windows 260 caractères)
**Défense** : Avertir si le chemin résultant >250 caractères.

### P7.4 : Caractères spéciaux dans les noms de fichiers
**Défense** : Préserver les noms originaux. Utiliser des objets `Path`, pas de concaténation de chaînes.

### P7.5 : Sensibilité à la casse
**Défense** : Utiliser les noms de fichiers originaux exacts. Avertir sur les doublons différant uniquement par la casse.

---

## Catégorie 8 : Git et Contrôle de Version

### P8.1 : Diff énorme
**Défense** : Recommander de diviser en PRs par lots selon la priorité.

### P8.2 : Conflits de merge
**Défense** : Chaque langue est un sous-répertoire séparé → pas de conflits entre langues.

### P8.3 : Squash merge perd le suivi SHA
**Défense** : Repli sur la recherche par date quand le SHA n'est pas trouvé dans l'historique.

---

## Catégorie 9 : Configuration

### P9.1 : YAML invalide dans la configuration
**Défense** : Valider au chargement. Repli sur les valeurs par défaut avec avertissement.

### P9.2 : Code de langue inconnu
**Défense** : Valider contre ISO 639-1. Correspondance floue : "ukr" → "Vouliez-vous dire uk ?"

### P9.3 : Conflits de glossaire
**Défense** : Vérifier les traductions conflictuelles de mots racines au chargement. Avertir.

---

## Catégorie 10 : Cas Limites

### P10.1 : Fichier composé uniquement de tableaux
**Défense** : Traiter les tableaux ligne par ligne. Vérifier le nombre de `|` par ligne par rapport à l'original.

### P10.2 : Markdown avec HTML en ligne
**Défense** : Balises HTML → marqueurs. Traduire le texte entre les balises, pas les attributs.

### P10.3 : Formules LaTeX
**Défense** : Détecter `$...$` et `$$...$$`. Extraire comme marqueurs.

### P10.4 : Emoji dans les titres
**Défense** : Supprimer les emoji lors de la génération des ancres (correspond au comportement de GitHub).

### P10.5 : Fichier sans titres
**Défense** : Découper par lignes vides au lieu de `##`. Si <4000 tokens → traduire le fichier entier.

### P10.6 : Métadonnées i18n en double
**Défense** : Vérifier les métadonnées existantes avant d'ajouter. Mettre à jour, ne pas dupliquer.

### P10.7 : Traduire des traductions ⚠️ CRITIQUE
**Défense** : TOUJOURS exclure `translations_dir` du scan. Vérifier que source ≠ répertoire cible.

### P10.8 : Inclusion/exclusion récursive
**Défense** : `exclude: ["**/CHANGELOG.md"]` exclut dans tout répertoire. `exclude: ["CHANGELOG.md"]` uniquement à la racine.

---

## Résumé des Défenses

### Automatiques (sans action utilisateur) :
| Défense | Quand | Action |
|---------|-------|--------|
| Vérification UTF-8 | Après chaque écriture | Auto-réparation ou rejet |
| Marqueurs de blocs de code | Pendant la traduction | Le code ne passe jamais par l'IA |
| Vérification du nombre de lignes | Après traduction | Rejeter si <85% |
| Correction des ancres | Après traduction | Auto-remplacement des ancres cassées |
| Réécriture des liens | Lors de la création de fichier | Auto-réécriture des chemins relatifs |
| Saut de ligne final | À l'écriture | Auto-ajout |
| Suppression Unicode invisible | Après traduction | Auto-suppression |
| Déduplication des métadonnées | À l'ajout d'en-tête | Mise à jour au lieu de duplication |

### Avertissements (nécessitent l'attention de l'utilisateur) :
| Défense | Quand | Message |
|---------|-------|---------|
| Gros dépôt | Au scan | "12 847 fichiers, réduction de portée recommandée" |
| Traductions existantes | À l'initialisation | "uk/ trouvé, importer ?" |
| Écart de glossaire | À la validation | "hook traduit comme гачок (1x)" |
| Langue RTL | À l'initialisation | "Nécessite une attention particulière" |
| Chemins absolus | Au scan | "Impossible de réécrire automatiquement" |

### Bloquantes (arrêt du processus) :
| Défense | Quand | Raison |
|---------|-------|--------|
| Fichier raccourci >15% | Après traduction | L'IA a perdu du contenu |
| Écart du nombre de blocs de code | Après traduction | Structure cassée |
| Source = répertoire cible | À l'initialisation | Traduirait des traductions |
| Pas de droits d'écriture | À l'initialisation | Impossible de sauvegarder |

---

## Priorité d'Implémentation

### MVP (implémenté) :
1. ✅ Validation UTF-8 (P4.1)
2. ✅ Vérification du nombre de lignes (P2.1)
3. ✅ Vérification du nombre de blocs de code (P2.1)
4. ✅ Auto-correction des ancres (P3.1, P3.2, P3.3)
5. ✅ Exclusion du répertoire de traductions (P10.7)
6. ✅ Auto-détection des traductions existantes (P1.3)

### Prochaine étape (planifié) :
7. Extraction de marqueurs de blocs de code (P2.2)
8. Extraction de marqueurs HTML (P2.6)
9. Vérification du glossaire (P5.4)
10. Gestion du frontmatter (P6.1)
11. Découpage de fichiers volumineux (P2.8)
12. Réécriture des liens relatifs (P3.4)

### Futur :
13. Support RTL (P5.1)
14. Coefficients CJK (P5.2)
15. Marqueurs LaTeX (P10.3)
16. Mémoire de traduction
