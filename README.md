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

## 🚀 启动指北 / Usage

只需要在终端控制台（包含本项目源码的根目录）下运行该脚本即可：

```bash
python bbc_6min_downloader.py
```

启动后，您可以喝一杯咖啡，所有的多媒体数据将全自动落入 `downloads/` 目录中。

---

*(English documentation)*

An automated Python script designed to batch download materials from BBC's "6 Minute English" episodes. It systematically scans the BBC archives from 2024 to the present, extracting the episode titles, publication dates, and parsing the page to safely download the corresponding files into an organized directory structure.

## Features

- **Automated Directory Structuring**: Saves downloads automatically into cleanly separated folders, like `downloads/YYYY/MM/DD_EpisodeTitle/`.
- **Full Scope Downloads**: Fetches the podcast Audio (`audio.mp3`), Transcript (`transcript.pdf`), and Worksheet (`worksheet.pdf`) effortlessly.
- **Smart Incremental Updates**: Saves a record of completed downloads in `downloaded_episodes.json` avoiding any duplicate fetching upon subsequent runs. Simply run it periodically to sync newly emitted episodes!
- **Error Resistant**: Automatically bypasses episodes where assets are intentionally bundled by BBC (e.g., transcripts bundled inside worksheets for vintage episodes) without halting.

## Requirements

- Python 3.10+
- Dependencies: `requests`, `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```

## Usage

Simply run the script in your terminal inside the root directory:

```bash
python bbc_6min_downloader.py
```

Sit back and watch your `downloads/` directory populate.
