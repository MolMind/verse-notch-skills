# VerseNotch 插件技能

为 VerseNotch 制作歌词样式，或设计其他类别的插件。每个技能目录包含独立的 `SKILL.md` 和运行所需的文件。

[VerseNotch 官网](https://versenotch.com/) · [插件文档](https://versenotch.com/docs) · [插件广场](https://versenotch.com/plugins)

| 技能 | 交付内容 | 当前阶段 |
| --- | --- | --- |
| [歌词样式制作](skills/versenotch-lyric-style/SKILL.md) | 声明式样式配置、离线验证和 `.vnplugin` 打包 | 契约 `lyric-style` v1，VerseNotch 0.2.0 起支持本地导入 |
| [平台登录设计](skills/versenotch-music-provider/SKILL.md) | 单平台的授权、会话和宿主适配提案 | 设计 |
| [歌词与封面获取设计](skills/versenotch-metadata-provider/SKILL.md) | 独立的歌词或封面来源、匹配和缓存提案 | 设计 |
| [浮窗样式设计](skills/versenotch-window-style/SKILL.md) | 宽高、材质、共振预设和预览矩阵 | 设计 |
| [播放顺序设计](skills/versenotch-playback-order/SKILL.md) | 排序规则、回退和可复现队列样例 | 设计 |
| [音质调节设计](skills/versenotch-audio-preset/SKILL.md) | 音频信号链、参数和试听验收计划 | 设计 |

## 使用设计技能

从 [design-skills-v0.1.0](https://github.com/MolMind/verse-notch-skills/tree/design-skills-v0.1.0/skills) 选择一个完整技能目录，复制到所用 Agent 的技能目录。设计技能交付 Markdown 提案与针对该类型的验收用例，对应的安装与投稿契约尚未开放。

例如：

> $versenotch-playback-order 设计一个按艺人轮换的播放顺序，保留手动指定下一首，并给出队列样例。

## 歌词样式快速开始

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

## 生成测试市场安装包

开发与测试环境开放预览类型时，可用 Python 3.10 或以上版本生成测试包。预览包用于验证投稿、审核和安装登记，安装后仅可查看配置。

```sh
demo_dir=$(mktemp -d)
python3 scripts/pack-preview.py window-style "$demo_dir/window.vnplugin" \
  --id app.example.window-preview --name "浮窗示例" --author Example --license UNLICENSED
```

命令支持五种预览类型。默认使用对应示例配置，可用 `--config` 指定其他 JSON 配置。投稿时按清单填写相同的类型、ID、名称、版本和许可证。服务器和客户端分别校验契约。
