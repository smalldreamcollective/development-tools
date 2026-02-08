# References: CLI

Sources consulted during design and implementation of the CLI.

## Library Documentation

- **Click documentation**
  https://click.palletsprojects.com/
  Used for: all CLI implementation — command groups, argument/option decorators, `@click.pass_context`, `click.echo`, `click.style`, `click.confirm`, `click.Choice`, `click.version_option`. Click was chosen for its decorator-based API and built-in help generation.

## Provider SDK Documentation

- **Anthropic Python SDK — Messages API**
  https://docs.anthropic.com/en/api/messages
  Used for: the `_call_anthropic()` function that creates messages via `client.messages.create()`.

- **OpenAI Python SDK — Chat Completions API**
  https://platform.openai.com/docs/api-reference/chat/create
  Used for: the `_call_openai()` function that creates completions via `client.chat.completions.create()`.

## CLI Design References

- **12 Factor App — Config**
  https://12factor.net/config
  Used for: API keys via environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) rather than config files.

- **XDG Base Directory Specification (loosely)**
  Used for: default paths under `~/.tokenmeter/` for database and config files.

## Design Decisions

| Decision | Source |
|----------|--------|
| Click as CLI framework | Click docs — mature, decorator-based, auto-generates help text |
| SQLite as default CLI storage | Persistent storage needed for cross-session tracking |
| Budget config in `~/.tokenmeter/config.json` | Separate from usage data; human-readable |
| API keys via environment variables | 12 Factor App convention |
| `--db` global option for database path | Allows testing and multi-environment use |
| stdin support for `prompt` and `estimate` | Standard Unix convention for piping text |
| Date parsing with multiple format attempts | User convenience — accept `YYYY-MM-DD` and `YYYY-MM-DDTHH:MM:SS` |
