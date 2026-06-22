# Changelog

All notable changes to the `desrobotizar` skill are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com);
the `metadata.version` / `metadata.updated` fields in `SKILL.md` frontmatter point to the latest entry.

## 2.0.1 - 2026-06-22

### Changed
- Trimmed the `description` frontmatter to focus on triggering conditions
  (per skill-discovery best practices), moving the full pattern catalogue out of
  the description and into the body where it already lives. Validated with
  subagent discovery tests that triggering still fires on paraphrased requests
  (no exact keywords) and stays quiet on unrelated requests.

## 2.0.0 - 2026-06-22

### Added
- New "Substância e posição" category with seven patterns (34–40): excessive abstraction,
  generic examples, absence of opinion, artificial grammatical perfection, source/statistic
  hallucination, standardized transitions, and cultural disconnect/idiomatic translations.
- "Estrutura antes de palavras" key principle: structure and rhythm matter more than vocabulary.
- Insights from four Brazilian sources (Canaltech, Fast Company Brasil, Tecmundo, SciELO).

### Changed
- Reinforced item 9 (negative parallelisms, "não é X, é Y") as the most revealing structural signal.

## 1.0.0

### Added
- Initial release adapted from [blader/humanizer](https://github.com/blader/humanizer) v2.5.1,
  with 33 pt-BR-specific AI-writing patterns.
