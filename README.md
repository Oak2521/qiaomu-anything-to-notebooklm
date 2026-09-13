# qiaomu-anything-to-notebooklm

多源内容提取及按请求上传 NotebookLM 的工作流。完整技能路由见 [SKILL.md](SKILL.md)，依赖列表见 [requirements.txt](requirements.txt)。仅加载技能不运行安装脚本、不使用账号、不创建外部对象。

## 默认读取

普通 URL 只直接请求公开正文；本地 TXT/Markdown 直接读取，EPUB 使用已安装的 ebooklib/BeautifulSoup 提取。其他类型交由已安装的专用提取工具。微信文章优先 Moore 微信技能；YouTube、播客的外部转写服务需要单独覆盖该服务与内容的授权。

```bash
python main.py https://example.com/article
python main.py ./notes.md
python main.py ./book.epub
```

公开读取不使用代理级联、爬虫身份伪装或付费墙绕过。遇到登录、订阅、验证码或拒绝访问即停止；HTTP 成功和文本提取不证明文章完整，仍需核对正文首尾。

## 已授权的外部工作流

只有用户明确要求上传，或已有覆盖相同内容、服务、目标笔记本的有效授权时，才使用 `--upload`。执行前核实 NotebookLM 当前目标；文件流程会新建笔记本，URL 流程使用当前目标。普通摘要请求不授权上传、新建笔记本、Get笔记对象或飞书文档。需要新目标时先确认目标。

```bash
python main.py ./book.epub --upload
python main.py ./book.epub --upload --deep-analysis
```

深度分析会调用 NotebookLM 问答；`--to-feishu` 还会创建飞书文档，须另有对应发布授权。账号登录、费用与安装沿用宿主明确门禁，不使用真实资料进行默认测试。Get笔记播客转写还须独立服务授权与 `--allow-getnote`。`--upload` 是显式执行开关，不替代宿主对授权范围的判断。

运行环境按所选流程配置；可先阅读 `check_env.py`、`install.sh` 与依赖清单，再按已批准范围安装。默认读取无需安装整套外部服务。

## 验证

```bash
python -m unittest test_main_scope
python scripts/test_fetch_url.py
```

以上为离线作用域和公开读取边界测试，不代表 NotebookLM、Get笔记、飞书账号集成或所有来源格式均已实测。

## 致谢与许可证

感谢 [Google NotebookLM](https://notebooklm.google.com/)、[Microsoft markitdown](https://github.com/microsoft/markitdown)、[wexin-read-mcp](https://github.com/Bwkyd/wexin-read-mcp) 和 [notebooklm-py](https://github.com/teng-lin/notebooklm-py)。

保留上游声明：[MIT License](LICENSE) — 仅限个人学习研究使用。该仓库说明与许可证正文的适用范围须分别核对，本次修改不授予新的使用权。

Made by [Joe](https://github.com/joeseesun) · [Twitter @vista8](https://x.com/vista8) · 微信公众号「向阳乔木推荐看」
