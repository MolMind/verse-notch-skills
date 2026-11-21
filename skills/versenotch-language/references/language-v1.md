# VerseNotch 语言插件 v1

`.vnplugin` 是普通 ZIP。根目录包含 UTF-8 的 `manifest.json` 和 `strings.json`。安装包和 `strings.json` 各自最多 256 KiB，清单最多 64 KiB。

清单沿用市场通用 v1 清单。将 `manifestVersion` 和 `pluginAPIVersion` 都设为整数 1，`minAppVersion` 至少为 `0.2.5`，`permissions` 为空数组，`type` 为 `language`，`entry` 为 `strings.json`。在 `name` 填语言自称，例如 `日本語`。清单示例见 [manifest.json](../assets/ja/manifest.json)。

`strings.json` 包含 `locale` 和 `translations`。语言标记使用语言、可选文字和可选地区，例如 `ja`、`zh-Hant` 或 `pt-BR`。翻译是由字符串键和译文组成的数组，键必须来自目标客户端的文案目录且只能出现一次。每条译文应包含实际文本，UTF-8 最长 2048 字节。包含数量的文案可以用「曲目数 {0}」这类表达兼容不同数量。

```json
{
  "locale": "ja",
  "translations": [
    ["plugins.language.title", "言語プラグイン"],
    ["plugins.language.enable", "有効にする"],
    ["deck-view.message-34", "音量 {0}%"]
  ]
}
```

占位符如 `{0}` 和 `{1}` 由宿主填入动态值。保持每个占位符的出现次数，按语序调换位置。字符串键在同一接口版本中保持稳定。更新文案时应同步客户端词条、服务端校验目录和技能中的版本快照。

简体中文为默认语言。缺失的译文按词条回退为简体中文。插件只翻译客户端文案，系统控件采用系统语言，曲名、歌词和用户资料保留原文。LAN 或离线安装时可使用本地包，市场投稿和分发状态见 [语言插件文档](https://versenotch.com/docs/plugins/language)。
