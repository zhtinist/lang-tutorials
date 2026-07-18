# -*- coding: utf-8 -*-
"""生成 GitHub Pages 双语站点(docs/):zh 与 en 两套镜像,右侧固定语言切换按钮。

- zh 源目录:<X>-tutorial;en 源目录:<X>-tutorial-en(文件名与 zh 完全相同)。
- 输出:docs/zh/<sub>/*.html、docs/en/<sub>/*.html,以及各自 index.html。
- 语言切换:每页右侧中部一个固定按钮,点击把 URL 里的 /zh/ 与 /en/ 互换(并记忆偏好)。
- docs/index.html 是一个按记忆偏好跳转的入口。
- 某语言的源目录不存在时自动跳过该语言。
"""
import os, re, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
FROM = "markdown+raw_html-yaml_metadata_block-simple_tables-multiline_tables"

TUTS = [("python-tutorial", "python", "Python"),
        ("java-tutorial",   "java",   "Java"),
        ("go-tutorial",     "go",     "Go")]
LANGS = ["zh", "en"]

TOGGLE_JS = ("function switchLang(){var p=location.pathname,en=p.indexOf('/en/')>-1,"
             "n=en?p.replace('/en/','/zh/'):p.replace('/zh/','/en/');"
             "try{localStorage.setItem('lang',en?'zh':'en')}catch(e){}location.href=n;}")

HOME_TITLE = {"zh": "面向 C/C++ 程序员的其他语言教程",
              "en": "Other Languages for C/C++ Programmers"}


def src_for(sub_src, lang):
    return sub_src if lang == "zh" else sub_src + "-en"


def toggle_html(lang):
    label = "EN" if lang == "zh" else "中"
    full = "English" if lang == "zh" else "中文"
    return (f'<a class="langtoggle" href="#" onclick="switchLang();return false;" '
            f'title="切换语言 / Switch language"><b>{label}</b><span>{full}</span></a>'
            f'<script>{TOGGLE_JS}</script>')


def navbar(lang, sub_active, lang_root):
    parts = [f'<a class="home" href="{lang_root}/index.html">'
             f'<span class="logo">📚</span><span class="brand">{HOME_TITLE[lang]}</span></a>']
    for _, sub, disp in TUTS:
        cls = ' style="color:var(--accent-dark);font-weight:700"' if sub == sub_active else ""
        parts.append(f'<a href="{lang_root}/{sub}/index.html"{cls}>{disp}</a>')
    lang_label = "🌐 EN" if lang == "zh" else "🌐 中文"
    parts.append(f'<a class="topnav-lang" href="#" onclick="switchLang();return false;" '
                 f'title="切换语言 / Switch language">{lang_label}</a>')
    return ('<div class="topbar"><div class="wrap">' + "\n".join(parts) + '</div></div>'
            + toggle_html(lang) + '\n<div class="wrap">')


def first_h1(text):
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    return re.sub(r"[`*⭐]", "", m.group(1)).strip() if m else "Tutorial"


def build_page(md_path, out_path, lang, sub_active):
    text = open(md_path, encoding="utf-8").read()
    text = re.sub(r"(\]\([^)\s#]+?)\.md((?:#[^)]*)?\))", r"\1.html\2", text)
    title = first_h1(text)
    is_index = os.path.basename(md_path) == "index.md"
    before = navbar(lang, sub_active, "..")          # 章节页:lang_root = ..(docs/<lang>)
    bpath = out_path + ".before"
    open(bpath, "w", encoding="utf-8").write(before)
    cmd = ["pandoc", "-f", FROM, "-t", "html", "--standalone",
           "-c", "../../assets/style.css",          # docs/<lang>/<sub>/x.html → ../../assets
           "--metadata", f"pagetitle={title}",
           "--metadata", f"lang={'zh-CN' if lang == 'zh' else 'en'}",
           "--include-before-body", bpath]
    if not is_index:
        cmd += ["--toc", "--toc-depth=2"]
    r = subprocess.run(cmd + ["-o", out_path], input=text, capture_output=True, text=True)
    os.remove(bpath)
    if r.returncode != 0:
        raise SystemExit(f"pandoc 失败 {md_path}:\n{r.stderr}")
    doc = open(out_path, encoding="utf-8").read().replace("</body>", "</div>\n</body>", 1)
    open(out_path, "w", encoding="utf-8").write(doc)


def badges():
    repo = "zhtinist/lang-tutorials"
    def b(kind, label, path):
        return (f'<a href="https://github.com/{repo}/{path}">'
                f'<img alt="{label}" src="https://img.shields.io/github/{kind}/{repo}'
                f'?style=flat-square&logo=github&label={label}"></a>')
    return ('<p style="text-align:center;margin:8px 0 0">'
            + b("stars", "Stars", "stargazers")
            + b("watchers", "Watchers", "watchers")
            + b("forks", "Forks", "network/members") + '</p>')


def home_html(lang):
    T = HOME_TITLE[lang]
    cards = "\n".join(
        (f'<a class="card" href="{sub}/index.html"><h3>{disp}</h3>'
         f'<p>{("从底层实现视角讲 " + disp + ":内存模型、对象布局、并发、标准库,处处与 C/C++ 对照。") if lang=="zh" else ("Understand " + disp + " from the implementation up: memory model, object layout, concurrency, and the standard library — always contrasted with C/C++.")}</p></a>')
        for _, sub, disp in TUTS)
    if lang == "zh":
        lead = ("假设你已精通 C/C++——指针、栈/堆、值传递与引用、手动内存管理。<br>"
                "这三套教程不重复基础语法,而是讲清 <b>每个操作在底层到底发生了什么</b>,并处处与 C/C++ 对照。")
        why_h = "为什么是这三门"
        why = ("<li><b>Python</b>——一切皆堆上对象、名字即引用、引用计数 + GC、GIL 与 free-threading。</li>"
               "<li><b>Java</b>——基本类型 vs 引用类型、对象头与逃逸分析、JMM 与虚拟线程、GC 演进。</li>"
               "<li><b>Go</b>——一切皆值拷贝、slice/map/channel 的表头结构、逃逸分析、GMP 调度、Swiss Tables。</li>")
        credit = ('本教程内容在创作过程中借助了 <b>Claude</b> 与 <b>Cursor</b> 辅助撰写与校对。'
                  '作者 / 维护者:HTZHU〈<a href="mailto:zhu.h4@northeastern.edu">zhu.h4@northeastern.edu</a>〉。'
                  '源码见 <a href="https://github.com/zhtinist/lang-tutorials">GitHub 仓库</a>。')
    else:
        lead = ("Assuming you already know C/C++ — pointers, stack/heap, pass-by-value vs. reference, manual memory management.<br>"
                "These three tutorials skip the basic syntax and instead explain <b>what actually happens under the hood for every operation</b>, always contrasted with C/C++.")
        why_h = "Why these three"
        why = ("<li><b>Python</b> — everything is a heap object, names are references, reference counting + GC, the GIL and free-threading.</li>"
               "<li><b>Java</b> — primitives vs. references, object headers and escape analysis, the JMM and virtual threads, GC evolution.</li>"
               "<li><b>Go</b> — everything is a value copy, the header structs behind slice/map/channel, escape analysis, the GMP scheduler, Swiss Tables.</li>")
        credit = ('This content was written and proofread with the help of <b>Claude</b> and <b>Cursor</b>. '
                  'Author / maintainer: HTZHU 〈<a href="mailto:zhu.h4@northeastern.edu">zhu.h4@northeastern.edu</a>〉. '
                  'Source on <a href="https://github.com/zhtinist/lang-tutorials">GitHub</a>.')
    nav_items = "".join(f'<a href="{sub}/index.html">{disp}</a>' for _, sub, disp in TUTS)
    lang_label = "🌐 EN" if lang == "zh" else "🌐 中文"
    nav_items += (f'<a class="topnav-lang" href="#" onclick="switchLang();return false;" '
                  f'title="切换语言 / Switch language">{lang_label}</a>')
    return f"""<!doctype html><html lang="{'zh-CN' if lang=='zh' else 'en'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{T}</title>
<link rel="stylesheet" href="../assets/style.css"></head><body>
<div class="topbar"><div class="wrap"><a class="home" href="index.html"><span class="logo">📚</span><span class="brand">{T}</span></a>{nav_items}</div></div>
{toggle_html(lang)}
<div class="wrap">
<div class="hero"><h1>{T}</h1><p>{lead}</p>{badges()}</div>
<div class="cards">{cards}</div>
<h2>{why_h}</h2><ul>{why}</ul>
<p class="note">{credit}</p>
</div></body></html>"""


def main():
    for lang in LANGS:
        available = [t for t in TUTS if os.path.isdir(os.path.join(ROOT, src_for(t[0], lang)))]
        if not available:
            print(f"[跳过] {lang}:无源目录"); continue
        for src, sub, _ in available:
            outdir = os.path.join(DOCS, lang, sub); os.makedirs(outdir, exist_ok=True)
            for fn in sorted(os.listdir(os.path.join(ROOT, src_for(src, lang)))):
                if fn.endswith(".md"):
                    build_page(os.path.join(ROOT, src_for(src, lang), fn),
                               os.path.join(outdir, fn[:-3] + ".html"), lang, sub)
            print(f"  {lang}/{sub}: {len([f for f in os.listdir(outdir) if f.endswith('.html')])} 页")
        with open(os.path.join(DOCS, lang, "index.html"), "w", encoding="utf-8") as f:
            f.write(home_html(lang))
        print(f"  {lang}/ 首页完成")
    # 根入口:按记忆偏好跳转
    root = ('<!doctype html><meta charset="utf-8"><title>lang-tutorials</title>'
            '<script>var l="zh";try{l=localStorage.getItem("lang")||"zh"}catch(e){}'
            'location.replace(l==="en"?"en/index.html":"zh/index.html");</script>'
            '<p style="font-family:sans-serif">Redirecting… '
            '<a href="zh/index.html">中文</a> / <a href="en/index.html">English</a></p>')
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(root)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("  根入口 + .nojekyll 完成")


if __name__ == "__main__":
    main()
    print("站点已生成到 docs/")
