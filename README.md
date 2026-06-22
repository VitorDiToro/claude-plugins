# vitor-plugins

Marketplace pessoal de plugins do [Claude Code](https://code.claude.com).

## Plugins

| Plugin          | Versão | Descrição                                                                 |
|-----------------|--------|---------------------------------------------------------------------------|
| `commit-helper` | 1.1.0  | Gera mensagens de commit no padrão Conventional Commits a partir do stage. |

## Instalação (em qualquer máquina)

```
/plugin marketplace add <seu-usuario>/claude-plugins
/plugin install commit-helper@vitor-plugins
```

> Troque `<seu-usuario>` pelo seu usuário do GitHub depois de publicar o repositório.

### Testar localmente antes de publicar

Dá para apontar o marketplace para a pasta local, sem GitHub:

```
/plugin marketplace add "/home/vitor/Área de trabalho/claude-plugins"
/plugin install commit-helper@vitor-plugins
```

### Atualizar depois de um `git push`

```
/plugin marketplace update vitor-plugins
```

Ou abra o gerenciador interativo com `/plugin`.

## Estrutura

```
claude-plugins/                       # repo = marketplace
├── .claude-plugin/
│   └── marketplace.json              # catálogo (versão DO marketplace)
├── README.md
└── commit-helper/                    # plugin
    ├── .claude-plugin/
    │   └── plugin.json               # versão DO plugin
    └── skills/
        └── commit-helper/
            ├── SKILL.md              # versão DA skill (metadata.version)
            └── CHANGELOG.md
```

## Versionamento

Há três versões independentes:

- **Marketplace** → `.claude-plugin/marketplace.json` (`metadata.version`): versiona o catálogo.
- **Plugin** → `commit-helper/.claude-plugin/plugin.json` (`version`): versiona o pacote.
- **Skill** → `commit-helper/skills/commit-helper/SKILL.md` (`metadata.version`): versiona o conteúdo.

Por enquanto o **plugin** e a **skill** caminham juntos. Ao lançar uma mudança na skill:

1. Atualize `metadata.version` + `metadata.updated` no `SKILL.md`.
2. Atualize `version` no `plugin.json` para o mesmo número.
3. Adicione a entrada no `CHANGELOG.md` da skill.
4. Suba a versão do `marketplace.json` apenas quando o **catálogo** mudar (ex.: adicionar/remover um plugin).
