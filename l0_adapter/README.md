# L0 Adapter

异构数据源 → 统一转写格式。将访谈字幕、股东信、推文、邮件、传记等异构来源转化为 3+1 Pipeline L1 阶段可消费的统一格式。

## 核心原则

- **零 LLM 依赖**：只做物理格式转换，不做语义理解
- **利用源数据结构拆分**：按 Q&A 对 / 段落 / thread / 章节
- **行级说话人标注**：`[speaker_name]: content`
- **幂等**：同输入 → 同输出，自动去重

## 数据源分类

| 类型代号 | 沟通模式 | 适用来源 |
|---------|---------|---------|
| `DLG` | 对话型 | 访谈字幕、播客转写、邮件讨论 |
| `MON` | 独白型 | 股东信、演讲稿、博客文章 |
| `MIC` | 微言型 | 推文、微博 |
| `ATT` | 转述型 | 传记、新闻报道 |

## 使用方法

```bash
# 访谈字幕 → 对话型
python -m l0_adapter --type DLG \
  --input /data/lex_musk_podcast.srt \
  --output /bloggers/musk/transcripts/ \
  --target-speaker "Elon Musk" \
  --date 2024-03-14

# 股东信 → 独白型
python -m l0_adapter --type MON \
  --input "/data/buffett_letters/*.pdf" \
  --output /bloggers/buffett/transcripts/ \
  --target-speaker "Warren Buffett"

# 推文 → 微言型（按线索聚合）
python -m l0_adapter --type MIC \
  --input /data/musk_tweets.json \
  --output /bloggers/musk/transcripts/ \
  --target-speaker "Elon Musk" \
  --group-by thread

# 推文 → 微言型（按时间窗口聚合）
python -m l0_adapter --type MIC \
  --input /data/musk_tweets.json \
  --output /bloggers/musk/transcripts/ \
  --target-speaker "Elon Musk" \
  --group-by time-window --window 15m

# 传记 → 转述型
python -m l0_adapter --type ATT \
  --input /data/musk_biography.txt \
  --output /bloggers/musk/transcripts/ \
  --target-speaker "Elon Musk"

# 预览（不写文件）
python -m l0_adapter --type DLG --input ... --output ... --target-speaker ... --dry-run
```

## 输出格式

```
001_2024-03-14_第一性原理与火箭回收.txt
```

文件内容：
```
[来源: lex_musk_podcast.srt]
[日期: 2024-03-14]
[类型: DLG]
---
[Lex Fridman]: 你怎么看待第一性原理？
[Elon Musk]: 我认为第一性原理是解决问题的最基本方法...
```

## 与 3+1 Pipeline 的关系

```
L0 adapter → transcripts/*.txt → L1 知识提取 → L1.5 聚合 → L2 人设提取 → +1 Prompt
```

L0 是可选前置层。对已有抖音转写的博主，直接从 L1 开始。
