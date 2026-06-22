# commit-helper

> 🌐 **Bilingual** — English first, Português logo abaixo. [→ Pular para o português](#portugues)

## English

`commit-helper` generates [Conventional Commits v1.0.0](https://www.conventionalcommits.org)
messages from your staged changes, and commits them after you confirm.

### When it triggers

When you ask to write a commit message, to commit staged changes, or for a Conventional Commits
message — including natural-language phrasings, not just the exact keywords.

### How it works

1. **Validate the stage.** Runs `git diff --staged`. If nothing is staged, it stops and tells you
   to `git add` first — no empty commits.
2. **Compose the message.** Builds a Conventional Commits header `type(scope): description`
   (≤50 chars ideal, 72 hard limit), with an optional body (*what* and *why*, wrapped at 72) and
   optional footer (issue refs, `BREAKING CHANGE:`).
3. **Confirm, then commit.** Shows the proposed message and waits for your OK. If you explicitly
   asked to commit directly, it skips the confirmation.

### Language behavior

The **commit message itself is always written in English** — even when the conversation is in
another language. Everything the skill says **to you** (prompts, warnings) follows the **language
you are using in the conversation** (Portuguese, English, Spanish, German, …). This split is
deliberate: the commit history stays in one consistent language while the interaction meets you in
yours.

### Allowed types

`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.

### Example

Staged change: a login endpoint plus JWT validation middleware.

```
feat(auth): implement JWT-based authentication

Add the login endpoint and token validation middleware so protected
routes reject requests without a valid token.

Refs #42
```

Imperative mood, no trailing period, body explains *what/why* wrapped at 72, footer references the issue.

See the [CHANGELOG](../commit-helper/skills/commit-helper/CHANGELOG.md) for version history.

---

<a name="portugues"></a>

## Português

O `commit-helper` gera mensagens de commit no padrão
[Conventional Commits v1.0.0](https://www.conventionalcommits.org) a partir das suas mudanças em
stage e, após você confirmar, faz o commit.

### Quando é acionado

Quando você pede para escrever uma mensagem de commit, commitar as mudanças em stage, ou uma
mensagem no padrão Conventional Commits — inclusive em linguagem natural, não só com as palavras
exatas.

### Como funciona

1. **Valida o stage.** Roda `git diff --staged`. Se não houver nada em stage, ele para e avisa para
   você usar `git add` antes — nada de commit vazio.
2. **Compõe a mensagem.** Monta o cabeçalho Conventional Commits `tipo(escopo): descrição`
   (≤50 chars ideal, 72 no limite), com corpo opcional (*o quê* e *por quê*, quebrado em 72) e
   rodapé opcional (referências de issue, `BREAKING CHANGE:`).
3. **Confirma e commita.** Mostra a mensagem proposta e espera seu OK. Se você pediu explicitamente
   para commitar direto, ele pula a confirmação.

### Comportamento de idioma

A **mensagem de commit é sempre escrita em inglês** — mesmo quando a conversa está em outro idioma.
Tudo que a skill fala **com você** (prompts, avisos) segue o **idioma que você está usando na
conversa** (português, inglês, espanhol, alemão, …). Essa divisão é proposital: o histórico de
commits fica num idioma consistente enquanto a interação te encontra no seu.

### Tipos permitidos

`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.

### Exemplo

Mudança em stage: um endpoint de login e um middleware de validação de JWT.

```
feat(auth): implement JWT-based authentication

Add the login endpoint and token validation middleware so protected
routes reject requests without a valid token.

Refs #42
```

Modo imperativo, sem ponto final, corpo explicando *o quê/por quê* quebrado em 72, rodapé
referenciando a issue.

Veja o [CHANGELOG](../commit-helper/skills/commit-helper/CHANGELOG.md) para o histórico de versões.
