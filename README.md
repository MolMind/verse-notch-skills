# VerseNotch 插件技能

为 VerseNotch 制作、校验和打包插件。每个技能目录包含独立的 `SKILL.md` 和运行所需的文件。

[VerseNotch 官网](https://versenotch.com/) · [插件文档](https://versenotch.com/docs) · [插件广场](https://versenotch.com/plugins)

| 技能 | 交付内容 | 兼容版本 |
| --- | --- | --- |
| [歌词样式制作](skills/versenotch-lyric-style/SKILL.md) | 声明式样式配置、离线验证和 `.vnplugin` 打包 | 契约 `lyric-style` v1，VerseNotch 0.2.0 起支持本地导入 |

## 快速开始

将 [`lyric-style-v1.0.0`](https://github.com/MolMind/verse-notch-skills/tree/lyric-style-v1.0.0/skills/versenotch-lyric-style) 中的整个 `skills/versenotch-lyric-style` 目录复制到所用 Agent 的技能目录。在支持项目技能的工作区，也可以将它放在 `.agents/skills/` 下。目录内的模板、校验器与规范应一起保留。

在 Agent 中调用：

> $versenotch-lyric-style 帮我做一个深蓝渐变、薄荷绿逐字高亮的歌词样式，校验并打包。

也可以用 Python 3.10 或以上版本直接运行校验打包。以下命令在本仓库根目录执行，将示例包保存到临时目录。

```sh
demo_dir=$(mktemp -d)
skill_dir=skills/versenotch-lyric-style
python3 "$skill_dir/scripts/vnplugin.py" pack "$skill_dir/assets/lyric-style" "$demo_dir/aurora.vnplugin"
python3 "$skill_dir/scripts/vnplugin.py" validate "$demo_dir/aurora.vnplugin"
```

打开兼容的 VerseNotch，在「插件库 → 从文件导入」选择生成的包，预览后应用。发布自己的样式时，按 [歌词样式文档](https://versenotch.com/docs/plugins/lyric-style) 检查兼容性和投稿要求。
