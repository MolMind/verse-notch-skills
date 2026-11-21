---
name: versenotch-lyric-style
description: 为 VerseNotch 设计、制作、校验与打包可导入的歌词样式 .vnplugin，涵盖逐字高亮、歌词转场、静态背景、循环动画和字体，并按目标客户端版本验收。
---

# 制作 VerseNotch 歌词样式

先从需求明确客户端里应出现的效果。记录目标客户端版本、歌词所在窗口、背景怎样运动，以及字体与高亮的表现。用户指定了人物或视觉参考时，先确定要保留的角色造型、神态、构图与配色，再选择素材。下面的模板只提供字段结构。

## 选择客户端支持的能力

先读[浮窗适配与顶部播放栏](references/viewport-and-header.md)。现有 `.vnplugin` 在展开浮窗的歌词区内绘制。画面延伸到顶部播放栏时，按客户端内置主题或宿主接口开发处理。

- [v3 场景歌词](references/lyric-style-v3.md)用于含 v3 渲染器的 VerseNotch 0.2.3 起的客户端，支持连续场景、前景遮挡、随景锚点及歌词进出场。
- [v2 契约](references/lyric-style-v2.md)用于含 v2 渲染器的 VerseNotch 0.2.2 起的客户端。支持可平铺图片滚动、序列帧循环、系统字形、随包字体和字距。从 [v2 模板](assets/lyric-style-v2/) 或 [星海游鱼与纸上行旅示例](references/examples.md)开始。
- [v1 契约](references/lyric-style-v1.md)用于 VerseNotch 0.2.0 起的客户端。它支持颜色、字号、字重、对齐、逐行或逐字高亮、静态背景与歌词转场。使用 [v1 模板](assets/lyric-style/)。
- 先把用户要求逐项对照目标客户端。如果客户端缺少必要能力，明确指出缺口。可修改客户端的任务应同步实现渲染、导入校验和兼容门槛。目标客户端固定在旧版时，与用户确认可接受的替代效果，再改变交付目标。网页预览可以展示概念，客户端验收仍以实际导入和播放为准。

## 制作与交付

1. 从匹配版本的模板建立独立源目录。更新已有插件时保留 ID。确认作者、版本、许可证和素材的分发权。权利待确认的本地草案使用 `UNLICENSED`。
2. 用 `style.json` 和随包资源实现设计。循环素材检查首尾衔接和长歌词对比度。字体推敲字形、字号、字重和字距，并用实际歌词涉及的语言检查缺字与系统字形回退。
3. 使用 Python 3.10 或以上版本从技能目录运行下面的命令，将版本换成目标客户端的实际版本。

   ```sh
   python3 scripts/vnplugin.py validate /path/to/source --host-version 0.2.3
   python3 scripts/vnplugin.py pack /path/to/source /path/to/example.vnplugin --host-version 0.2.3
   python3 scripts/vnplugin.py validate /path/to/example.vnplugin --host-version 0.2.3
   ```

4. 使用源码构建的客户端时，可用 `VerseNotch --validate-lyric-plugin /path/to/example.vnplugin` 检查原生解码。在兼容客户端用「插件库 → 从文件导入」检查预览。应用到歌词浮窗后，按[尺寸与裁切验收](references/viewport-and-header.md)检查窄宽窗口、长短歌词、逐行与逐字歌词。动态样式检查循环接缝、暂停、跳转和系统的减少动态效果设置。用相同素材对照导入预览与实际播放。
5. 交付源目录、`.vnplugin`、插件 ID、版本和验证结果，注明实际测试的客户端与窗口。市场上架另按目标市场的支持版本办理。
