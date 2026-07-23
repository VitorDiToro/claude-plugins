# ditoro-plugins

> 🌐 **This README is bilingual — English first, Português logo abaixo.**
> [→ Pular para a versão em português](#portugues)

Personal plugin marketplace for [Claude Code](https://code.claude.com).

## English

### Plugins

| Plugin          | Version | Description                                                        | Details |
|-----------------|---------|--------------------------------------------------------------------|---------|
| `commit-helper` | 1.1.1   | Generates Conventional Commits messages from your staged changes.  | [docs/commit-helper.md](docs/commit-helper.md) |
| `desrobotizar`  | 2.0.1   | Removes AI-writing tells from Brazilian Portuguese text (40 patterns). | [docs/desrobotizar.md](docs/desrobotizar.md) *(pt-BR)* |
| `revisor-academico` | 1.4.0 | Editorial review of academic LaTeX reports (non-strict ABNT), reported as Markdown. | [docs/revisor-academico.md](docs/revisor-academico.md) *(pt-BR)* |

### Installation

```
/plugin marketplace add VitorDiToro/claude-plugins
/plugin install commit-helper@ditoro-plugins
/plugin install desrobotizar@ditoro-plugins
/plugin install revisor-academico@ditoro-plugins
```

### Updating

After a new release, update your machines with:

```
/plugin marketplace update ditoro-plugins
```

Or open the interactive manager with `/plugin`.

### For developers

Repository structure, versioning, the release workflow, local testing, and how to add a new plugin
live in **[docs/development.md](docs/development.md)**.

> Repository: https://github.com/VitorDiToro/claude-plugins

---

<a name="portugues"></a>

## Português

Marketplace pessoal de plugins do [Claude Code](https://code.claude.com).

### Plugins

| Plugin          | Versão | Descrição                                                              | Detalhes |
|-----------------|--------|------------------------------------------------------------------------|----------|
| `commit-helper` | 1.1.1  | Gera mensagens no padrão Conventional Commits a partir do seu stage.   | [docs/commit-helper.md](docs/commit-helper.md) |
| `desrobotizar`  | 2.0.1  | Remove sinais de escrita gerada por IA em textos em pt-BR (40 padrões). | [docs/desrobotizar.md](docs/desrobotizar.md) |
| `revisor-academico` | 1.4.0 | Revisão editorial de relatórios acadêmicos em LaTeX (ABNT não estrita), entregue em Markdown. | [docs/revisor-academico.md](docs/revisor-academico.md) |

### Instalação

```
/plugin marketplace add VitorDiToro/claude-plugins
/plugin install commit-helper@ditoro-plugins
/plugin install desrobotizar@ditoro-plugins
/plugin install revisor-academico@ditoro-plugins
```

### Atualizar

Depois de um novo release, atualize nas máquinas com:

```
/plugin marketplace update ditoro-plugins
```

Ou abra o gerenciador interativo com `/plugin`.

### Para desenvolvedores

A estrutura do repositório, o versionamento, o fluxo de publicação, o teste local e como adicionar
um novo plugin estão em **[docs/development.md](docs/development.md)** (em inglês).

> Repositório: https://github.com/VitorDiToro/claude-plugins
