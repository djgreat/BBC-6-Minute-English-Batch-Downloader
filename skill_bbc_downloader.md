# Skill: BBC 6 Minute English Downloader (BBC 6分钟英语下载器)

## Description / 描述
Automated tool to download BBC 6 Minute English episodes, including audio (MP3), transcripts (PDF), and worksheets (PDF).
自动下载 BBC 6分钟英语节目的工具，包括音频 (MP3)、讲义 (PDF) 和练习册 (PDF)。

## Capabilities / 功能
- **Incremental Sync / 增量同步**: Only downloads new episodes by tracking history in `downloaded_episodes.json`.
- **Targeted Download / 指定下载**: Support for downloading specific years, the latest episode, or a specific URL.
- **Auto-Organization / 自动整理**: Files are saved in `downloads/YYYY/MM/DD_Title/`.

## Usage / 使用方法

### CLI Commands / 命令行指令
Run the script with the following flags:

| Flag / 标志 | Description / 描述 | Example / 示例 |
| :--- | :--- | :--- |
| (None) | Sync all available episodes (incremental). / 全量增量同步。 | `python bbc_6min_downloader.py` |
| `--latest` | Download only the newest episode. / 仅下载最新一期。 | `python bbc_6min_downloader.py --latest` |
| `--year YYYY` | Sync a specific year (2024-2026). / 同步指定年份。 | `python bbc_6min_downloader.py --year 2025` |
| `--url URL` | Download a specific episode by URL. / 通过 URL 下载指定单期。 | `python bbc_6min_downloader.py --url https://www.bbc.co.uk/...` |
| `--quiet` | Suppress non-error logs (for automation). / 静默模式（仅输出错误）。 | `python bbc_6min_downloader.py --quiet` |
| `--json-output FILE` | Save sync results to a JSON file. / 将结果保存为 JSON。 | `python bbc_6min_downloader.py --json-output results.json` |

### Environment Variables / 环境变量
- `BBC_DOWNLOADS_DIR`: Override the default downloads directory. / 自定义下载目录。

### Output Structure / 输出结构
```text
downloads/
└── 2024/
    └── 01/
        └── 01_Episode_Title/
            ├── audio.mp3
            ├── transcript.pdf
            └── worksheet.pdf
```

## Integration Tips / 集成建议
- **For AI Agents**: When asked to "get the latest BBC English", use `python bbc_6min_downloader.py --latest`.
- **For Developers**: Use the `downloads/` directory as a source for word extraction or transcript parsing tasks.
