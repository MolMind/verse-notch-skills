# 星海游鱼与纸上行旅

这两个 v2 示例可直接打包并导入支持 v2 的客户端。它们提取 VerseNotch 内置主题的设计做法，素材和动画为插件示例制作。

| 示例 | 可参考的做法 | 插件实现 |
| --- | --- | --- |
| [星海游鱼](../assets/examples/star-sea/) | 冷色深背景、分散的星点和上下来回游动的鱼。歌词附近降低背景亮度，青色用于逐字高亮。 | 一张 8 列 4 行的序列帧图，4 秒循环，系统圆体设计。 |
| [纸上行旅](../assets/examples/paper-journey/) | 暖色纸面、低对比度纹理和留白。把场景压到歌词区下方，文字采用深墨色和较疏的字距。 | 纸面长卷从左向右匀速循环，系统衬线设计，歌词换行时向上滑入。 |

在技能目录中执行以下命令。生成的包可以在「插件库 → 从文件导入」预览。

```sh
demo_dir=$(mktemp -d)
python3 scripts/vnplugin.py pack assets/examples/star-sea "$demo_dir/star-sea.vnplugin"
python3 scripts/vnplugin.py pack assets/examples/paper-journey "$demo_dir/paper-journey.vnplugin"
```

试看原版时，在客户端的「外观 → 主题歌词」选择对应主题。内置星海游鱼的全息粒子结合了宿主动画时钟和 Metal，内置纸上行旅有专门的纸面场景及排版。制作插件时，可用这些主题参考色彩、留白和节奏，再依据目标客户端的支持能力选择工程方案。
