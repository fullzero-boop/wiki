---
tags:
  - ai4s
  - open-source
  - research
  - workbench
  - github
created: 2026-07-17
source: https://github.com/ai4s-research/open-science
---

# ai4s-research / open-science

**Open Science Desktop** — локальный, model-agnostic AI-воркбенч для научных исследований. Open-source альтернатива Claude Science.

**Организация:** [ai4s-research](https://github.com/ai4s-research) — MIT, community-driven, инфраструктура AI for Science.

## Технологический стек

- **Tauri 2** + **React** — десктопное приложение (macOS, Windows, Linux)
- **MCP** (Model Context Protocol) — интеграция моделей
- **OpenCode** — рантайм для агентов (sidecar)
- **Agent skills** — цепочка специализированных скиллов

## Полный цикл исследования

1. **Research Explorer** — разведка направления → `research_exploration.md`, `topic_matrix.md`
2. **Literature Survey** — обзор литературы → PDF 6-20 стр., 60+ рецензируемых ссылок
3. **Experiment Suite** — дизайн и код эксперимента → дизайн-док, код, `results.json` с provenance
4. **Paper Writer** — написание статьи → PDF 8-14 стр., 200+ ссылок, 4-8 графиков/таблиц
5. **Integrity Auditor** — аудит целостности (цитаты, числа, код)

Все артефакты — код, графики, таблицы — линкуются обратно к исходному коду, входным данным, окружению.

## Ключевые особенности

- **Local-first** — всё на локальной машине, ничего не уходит по умолчанию
- **Model-agnostic** — любые модели через OpenCode SDK
- **Reproducible by construction** — SSH/Slurm/Modal/notebook-batch runs сохраняются как воспроизводимые записи
- **Проверяемость** — каждая цифра в отчёте ведёт к коду
- **Расширяемость** — agent skills, MCP-серверы, коннекторы, SDK

## Репозитории организации

| Репозиторий | Описание | Звёзды |
|---|---|---|
| [open-science](https://github.com/ai4s-research/open-science) | Десктоп-воркбенч | ~812 ★ |
| [awesome-ai-for-science](https://github.com/ai4s-research/awesome-ai-for-science) | Курированный список AI-инструментов для науки | ~1800 ★ |
| [ai4s-skills](https://github.com/ai4s-research/ai4s-skills) | 7 agent skills для научных задач | ~154 ★ |
| [awesome-vision-language-action](https://github.com/ai4s-research/awesome-vision-language-action) | VLA-модели для робототехники | — |
| [awesome-text-to-speech](https://github.com/ai4s-research/awesome-text-to-speech) | TTS и voice cloning | — |
| [awesome-diffusion-llms](https://github.com/ai4s-research/awesome-diffusion-llms) | Diffusion language models | — |

## Agent Skills (ai4s-skills)

Семь скиллов, которые можно запускать на любом кодинг-агенте:

1. **ai4s-agent** — мета-скилл, запускает 4 основных последовательно
2. **research-explorer** — из broad direction в конкретные темы
3. **literature-survey** — полноценный литературный обзор
4. **experiment-suite** — пакет экспериментов
5. **paper-writer** — написание статьи
6. **mindmap-render** — визуализация mindmap
7. **integrity-auditor** — аудит целостности публикации

## Признание

🏆 **#1 по scored-task average** на ResearchClawBench (Pass@1 leaderboard, 9 июля 2026) — энд-ту-энд бенчмарк автономных научных AI-агентов.

## Ссылки

- **DOI:** [10.5281/zenodo.21351225](https://doi.org/10.5281/zenodo.21351225)
- **Discord:** https://discord.gg/fWNMDKcd5P
- **Бенчмарк:** https://internscience.github.io/ResearchClawBench-Home/
- **Лицензия:** MIT