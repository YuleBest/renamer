# renamer

renamer 是一个轻量的 Python 脚本，可以修改所有 css 和 js 文件的文件名，为它们加上哈希值，并修改 html 里的引用。

renamer 旨在解决原生 Web 开发的缓存更新问题。

## 功能

1. 执行脚本后，会自动搜寻脚本所在目录下所有的 css 和 js 文件，然后对它们求 SHA1 哈希值并截取前 8 位，最后将它们重命名为 `原名_哈希值.后缀名` 的格式（比如 `app_1a2b3c4d.js`）
2. 程序还会搜寻目录下所有的 html 文件，并将里面的 css 和 js 引用更新为新的文件名
3. 程序会在更新完成后生成日志和备份的文件，保存在 `.rename/` 目录下

## 使用方法

1. 把 `renamer.py` 放在你项目的根目录
2. 执行 `python renamer.py`

* 在使用 `git` 之前别忘了在 `.gitignore` 里添加下面的内容：

```text
.rename/
renamer.py
```