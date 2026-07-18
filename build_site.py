# -*- coding: utf-8 -*-
"""把三套教程的 Markdown 生成为 GitHub Pages 静态站点(docs/)。
每个 .md → 一个 .html(pandoc 渲染,跨文件 .md 链接改写为 .html),带顶部导航与目录。
"""
import os, re, subprocess, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
FROM = "markdown+raw_html-yaml_metadata_block-simple_tables-multiline_tables"

TUTS = [  # (源文件夹, 输出子目录, 展示名)
    ("python-tutorial", "python", "Python"),
    ("java-tutorial",   "java",   "Java"),
    ("go-tutorial",     "go",     "Go"),
]

def navbar(active):
    links = ['<a class="home" href="{home}">📚 面向 C/C++ 程序员的语言内幕教程</a>']
    for _, sub, disp in TUTS:
        cls = ' style="color:var(--accent-dark);font-weight:700"' if sub == active else ""
        links.append(f'<a href="{{root}}/{sub}/index.html"{cls}>{disp}</a>')
    inner = "\n".join(links)
    return f'<div class="topbar"><div class="wrap">{inner}</div></div>\n<div class="wrap">'

def first_h1(text):
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    return re.sub(r"[`*⭐]", "", m.group(1)).strip() if m else "教程"

def build_page(md_path, out_path, active, depth):
    text = open(md_path, encoding="utf-8").read()
    # 跨文件 .md 链接 → .html
    text = re.sub(r"(\]\([^)\s#]+?)\.md((?:#[^)]*)?\))", r"\1.html\2", text)
    title = first_h1(text)
    root = ".." if depth == 1 else "."
    before = navbar(active).replace("{home}", f"{root}/index.html").replace("{root}", root)
    css = f"{root}/assets/style.css"
    is_index = os.path.basename(md_path) == "index.md"
    cmd = ["pandoc", "-f", FROM, "-t", "html", "--standalone",
           "-c", css, "--metadata", f"pagetitle={title}", "--metadata", "lang=zh-CN",
           "--include-before-body", "/dev/stdin"]
    if not is_index:
        cmd += ["--toc", "--toc-depth=2"]
    # before-body 通过 stdin 传入较麻烦,改用临时文件
    bpath = out_path + ".before"
    open(bpath, "w", encoding="utf-8").write(before)
    cmd[cmd.index("/dev/stdin")] = bpath
    r = subprocess.run(cmd + ["-o", out_path], input=text, capture_output=True, text=True)
    os.remove(bpath)
    if r.returncode != 0:
        raise SystemExit(f"pandoc 失败 {md_path}:\n{r.stderr}")
    # 关闭 before-body 打开的 .wrap div:在 </body> 前插入 </div>
    doc = open(out_path, encoding="utf-8").read()
    doc = doc.replace("</body>", "</div>\n</body>", 1)
    open(out_path, "w", encoding="utf-8").write(doc)

def main():
    for src, sub, _ in TUTS:
        outdir = os.path.join(DOCS, sub)
        os.makedirs(outdir, exist_ok=True)
        for fn in sorted(os.listdir(os.path.join(ROOT, src))):
            if fn.endswith(".md"):
                build_page(os.path.join(ROOT, src, fn),
                           os.path.join(outdir, fn[:-3] + ".html"), sub, depth=1)
        print(f"  {sub}/ 生成 {len([f for f in os.listdir(outdir) if f.endswith('.html')])} 页")
    # 首页
    cards = "\n".join(
        f'<a class="card" href="{sub}/index.html"><h3>{disp} 教程</h3>'
        f'<p>从底层实现视角讲 {disp}:内存模型、对象布局、并发、标准库,处处与 C/C++ 对照。</p></a>'
        for _, sub, disp in TUTS)
    open(os.path.join(DOCS, "_home.md"), "w", encoding="utf-8").write("placeholder")
    home = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>面向 C/C++ 程序员的语言内幕教程</title>
<link rel="stylesheet" href="assets/style.css"></head><body>
<div class="topbar"><div class="wrap"><a class="home" href="index.html">📚 面向 C/C++ 程序员的语言内幕教程</a>
<a href="python/index.html">Python</a><a href="java/index.html">Java</a><a href="go/index.html">Go</a></div></div>
<div class="wrap">
<div class="hero"><h1>面向 C/C++ 程序员的语言内幕教程</h1>
<p>假设你已精通 C/C++——指针、栈/堆、值传递与引用、手动内存管理。<br>
这三套教程不重复基础语法,而是讲清 <b>每个操作在底层到底发生了什么</b>,并处处与 C/C++ 对照。</p></div>
<div class="cards">{cards}</div>
<h2>为什么是这三门</h2>
<ul>
<li><b>Python</b>——一切皆堆上对象、名字即引用、引用计数 + GC、GIL 与 free-threading。</li>
<li><b>Java</b>——基本类型 vs 引用类型、对象头与逃逸分析、JMM 与虚拟线程、GC 演进。</li>
<li><b>Go</b>——一切皆值拷贝、slice/map/channel 的表头结构、逃逸分析、GMP 调度、Swiss Tables。</li>
</ul>
<p class="note">本教程内容在创作过程中借助了 <b>Claude</b> 与 <b>Cursor</b> 辅助撰写与校对,
作者/维护者为 HTZHU(本仓库唯一 contributor)。源码见
<a href="https://github.com/zhtinist/lang-tutorials">GitHub 仓库</a>。</p>
</div></body></html>"""
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(home)
    os.remove(os.path.join(DOCS, "_home.md"))
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("  首页 + .nojekyll 完成")

if __name__ == "__main__":
    main()
    print("站点已生成到 docs/")
