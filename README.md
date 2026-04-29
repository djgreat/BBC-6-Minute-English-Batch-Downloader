# BBC 6 Minute English Batch Downloader

*(English documentation below | 英文文档在下方)*

一款自动化 Python 脚本，专门用于批量下载 BBC "6 Minute English"（6分钟英语）栏目的相关学习资料。它会自动抓取 2024 年至今发布的归档列表页面，提取对应的播客标题及发布日期，并自动将每个独立的音频与其对应的 PDF 讲义结构化保存到本地文件夹中。

## ✨ 核心特性 / Features

- **📂 自动目录整理 (Automated Structuring)**：按照清晰的时间轴创建对应文件夹（格式如 `downloads/YYYY/MM/DD_EpisodeTitle/`）。
- **🎧 全面捕获 (Full Scope Downloads)**：自动无缝提取原始并高速下载 MP3 (`audio.mp3`)、音频读物文本 (`transcript.pdf`) 以及官方配套练习册 (`worksheet.pdf`)。
- **⚡ 实时增量更新 (Smart Incremental Updates)**：脚本能智能且高效地管理在 `downloaded_episodes.json` 的下载历史，只要运行一遍，以后再启动就会瞬间跳过已有内容，实现零延迟增量拉取最新的每周单集。
- **🛡️ 超强容错 (Error Resistant)**：兼容各个年代与旧页面的细微差别特征（例如：早期部分剧集没有独立分离 Transcript，脚本也能成功收录），就算断网也能断点记录、防止死机。

## 🛠️ 运行环境 / Requirements

- Python 3.10+
- 核心依赖: `requests`, `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```

## 🚀 启动指南 / Usage

该脚本现在支持多种运行模式：

```bash
# 1. 增量同步（默认）：同步所有 2024-2026 的新集
python bbc_6min_downloader.py

# 2. 仅下载最新一期
python bbc_6min_downloader.py --latest

# 3. 下载指定年份
python bbc_6min_downloader.py --year 2025

# 4. 通过 URL 下载指定单期
python bbc_6min_downloader.py --url https://www.bbc.co.uk/learningenglish/english/features/6-minute-english/ep-240425

# 5. 自动化模式：静默运行并输出结果到 JSON
python bbc_6min_downloader.py --latest --quiet --json-output results.json
```

详细的技能定义请参考 [skill_bbc_downloader.md](./skill_bbc_downloader.md)。

---

*(English documentation)*

An automated Python script designed to batch download materials from BBC's "6 Minute English" episodes. It systematically scans the BBC archives from 2024 to the present.

## Features

- **Automated Directory Structuring**: Saves downloads automatically into folders like `downloads/YYYY/MM/DD_EpisodeTitle/`.
- **Full Scope Downloads**: Fetches the podcast Audio (`audio.mp3`), Transcript (`transcript.pdf`), and Worksheet (`worksheet.pdf`).
- **Smart Incremental Updates**: Tracks history in `downloaded_episodes.json` to avoid duplicates.
- **Error Resistant**: Handles different page structures and bundles gracefully.

## Requirements

- Python 3.10+
- Dependencies: `requests`, `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```

## Usage

The script now supports various running modes:

```bash
# 1. Incremental Sync (Default): Sync all new episodes from 2024-2026
python bbc_6min_downloader.py

# 2. Download only the latest episode
python bbc_6min_downloader.py --latest

# 3. Sync a specific year
python bbc_6min_downloader.py --year 2025

# 4. Download a specific episode by URL
python bbc_6min_downloader.py --url <BBC_URL>

# 5. Automation Mode: Run quietly and output results to JSON
python bbc_6min_downloader.py --latest --quiet --json-output results.json
```

For more details, see the [Skill Definition](./skill_bbc_downloader.md).
