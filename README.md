# BBC 6 Minute English Batch Downloader

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
