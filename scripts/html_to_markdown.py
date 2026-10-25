#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將 deep-distill-tw 生成之單書蒸餾 HTML 檔案轉換為結構嚴謹、排版精美的 Markdown 檔案。
可於各類 Markdown 閱讀器（如 Obsidian, Typora, GitHub）完美渲染。

用法:
    python html_to_markdown.py [html_path] [optional_md_path]
"""

import sys
import re
import os
import json
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def convert_html_to_markdown(html_path: str, md_path: str = None) -> str:
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"找不到輸入的 HTML 檔案: {html_path}")

    if not md_path:
        base, _ = os.path.splitext(html_path)
        md_path = base + ".md"

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    lines = []

    def p(s=""):
        lines.append(s)

    # 0. HEADER & BANNER
    banner = soup.find('header', class_='cb-banner')
    hero = soup.find('section', class_='hero')

    title = "書籍精讀蒸餾"
    eng_title = ""
    author = ""
    pub_year = ""

    if soup.title and soup.title.string:
        title = soup.title.string.split('·')[0].strip()

    if banner:
        t_el = banner.find('h1') or banner.find('div', class_='cb-title')
        if t_el:
            title = clean_text(t_el.get_text())
        a_el = banner.find('span', class_='cb-author') or banner.find('div', class_='cb-author')
        if a_el:
            author = clean_text(a_el.get_text())

    p(f"# {title}")
    p()
    if author:
        p(f"> **作者**：{author}  ")
    p("> **格式**：深度讀書蒸餾全景結構化文件  ")
    p()

    if banner:
        intro_el = banner.find('p', class_='cb-intro') or banner.find('div', class_='cb-intro')
        score_el = banner.find('div', class_='cb-score') or banner.find('span', class_='cb-score')
        meta_el = banner.find('div', class_='cb-meta')
        if intro_el:
            p("### 【書籍導讀】")
            p()
            p(clean_text(intro_el.get_text()))
            p()
        if score_el or meta_el:
            meta_items = []
            if score_el:
                meta_items.append(clean_text(score_el.get_text()))
            if meta_el:
                meta_items.append(clean_text(meta_el.get_text()))
            p(f"> *{' | '.join(meta_items)}*")
            p()

    if hero:
        hero_txt = clean_text(hero.get_text())
        if hero_txt:
            p("### 【核心提問與主旨】")
            p()
            p(f"**{hero_txt}**")
            p()

    p("---")
    p()

    # 1. 全書速覽 (GLANCE)
    p("## 壹、 全書速覽：認知極限與體制摩擦的動態重構")
    p()

    napkin = soup.find('div', class_='bd-napkin')
    if napkin:
        p("### 1.1 本質公式與核心直覺")
        p()
        eq = napkin.find('p', class_='formula') or napkin.find('div', class_='napkin-eq')
        read = napkin.find('p', class_='formula-read') or napkin.find('div', class_='napkin-read')
        paras = napkin.find_all('p', class_=lambda c: not c or c not in ['formula', 'formula-read'])
        if eq:
            p(f"> **【本質公式】** `{clean_text(eq.get_text())}`")
            p(">")
        if read:
            p(f"> **【怎麼讀】** {clean_text(read.get_text())}")
            p(">")
        for para in paras:
            txt = clean_text(para.get_text())
            if txt:
                p(f"> {txt}")
                p(">")
        p()

    sketch = soup.find('div', class_='napkin-sketch')
    if sketch:
        p("### 1.2 思維模型流程圖解")
        p()
        script_data = sketch.find('script', id='bd-sketch-data')
        if script_data:
            try:
                s_json = json.loads(script_data.string)
                caption = s_json.get('caption', '模型圖解')
                nodes = s_json.get('nodes', [])
                p(f"**模型圖解**：{caption}")
                p()
                p("```mermaid")
                p("flowchart TD")
                for i in range(len(nodes) - 1):
                    p(f"    {nodes[i]['id']}[\"{nodes[i]['label']}\"] --> {nodes[i+1]['id']}[\"{nodes[i+1]['label']}\"]")
                p("```")
                p()
            except Exception:
                pass

    coreideas = soup.find('div', class_='bd-coreideas')
    if coreideas:
        p("### 1.3 全書核心觀點清單")
        p()
        for group in coreideas.find_all('div', class_='ci-group'):
            g_head = group.find('h4', class_='ci-group-head')
            if g_head:
                p(f"#### {clean_text(g_head.get_text())}")
                p()
            for ci in group.find_all('article', class_='ci'):
                idea = ci.find('p', class_='ci-idea')
                analogy = ci.find('p', class_='ci-analogy')
                explain = ci.find('p', class_='ci-explain') or ci.find('div', class_='ci-body')
                src = ci.get('data-source', '')
                
                i_txt = clean_text(idea.get_text()) if idea else ""
                a_txt = clean_text(analogy.get_text()) if analogy else ""
                e_txt = clean_text(explain.get_text()) if explain else ""
                s_txt = f" *(出處：{src})*" if src else ""
                
                p(f"* **{i_txt}**{s_txt}")
                if a_txt:
                    p(f"  * 💡 *{a_txt}*")
                if e_txt:
                    p(f"  * 📖 **詳細解析**：{e_txt}")
                p()

    soul = soup.find('div', class_='soul-block')
    if soul:
        p("### 1.4 靈魂機制：古典漸進幻覺 vs. 斷續均衡現實")
        p()
        s_title = soul.find('h3', class_='soul-title')
        s_sub = soul.find('p', class_='soul-subtitle')
        s_intro = soul.find('p', class_='soul-intro')
        if s_title:
            p(f"**核心機理**：{clean_text(s_title.get_text())}")
        if s_sub:
            p(f"*{clean_text(s_sub.get_text())}*")
        if s_intro:
            p()
            p(f"> {clean_text(s_intro.get_text())}")
        p()
        for state in soul.find_all('article', class_='soul-state'):
            h = state.find('h4')
            b = state.find('p')
            h_txt = clean_text(h.get_text()) if h else ""
            b_txt = clean_text(b.get_text()) if b else clean_text(state.get_text())
            p(f"* **{h_txt}**")
            p(f"  {b_txt}")
            p()

    p("---")
    p()

    # 2. 關鍵概念與金句牆
    p("## 貳、 關鍵概念解析與全書金句牆")
    p()

    chips = soup.find('div', class_='concept-chips')
    if chips:
        p("### 2.1 本書核心關鍵概念")
        p()
        for btn in chips.find_all(['button', 'div'], class_=re.compile(r'chip|cc-chip')):
            pop = btn.find('span', class_='cc-pop')
            if pop:
                c_name = pop.find('strong')
                c_def = pop.find('em')
                smalls = pop.find_all('small')
                name_txt = clean_text(c_name.get_text()) if c_name else clean_text(btn.get_text())
                def_txt = clean_text(c_def.get_text()) if c_def else ""
                p(f"#### 【概念】{name_txt}")
                if def_txt:
                    p(f"> **核心定義**：{def_txt}")
                    p()
                for sm in smalls:
                    sm_txt = clean_text(sm.get_text())
                    if sm_txt:
                        p(f"* {sm_txt}")
                p()

    qw = soup.find('div', class_='quote-wall')
    if qw:
        p("### 2.2 全書金句牆與核心引言")
        p()
        for card in qw.find_all(['figure', 'article', 'div'], class_=re.compile(r'qw-card|card')):
            bq = card.find('blockquote')
            note = card.find('p', class_='qw-note')
            anchor = card.find('a', class_='qw-anchor') or card.find('span', class_='qw-src')
            q_txt = clean_text(bq.get_text()) if bq else ""
            n_txt = clean_text(note.get_text()) if note else ""
            a_txt = clean_text(anchor.get_text()) if anchor else ""
            if q_txt:
                p(f"> \"{q_txt}\"")
                if a_txt:
                    p(f"> *—— {a_txt}*")
                if n_txt:
                    p(f">")
                    p(f"> 💡 **解讀**：{n_txt}")
                p()

    p("---")
    p()

    # 3. 全書精讀 (FULL CHAPTERS)
    p("## 參、 全書精讀：跨越半世紀的計量政治學實證")
    p()

    full = soup.find('section', id='panel-full')
    if full:
        chapters = full.find_all('section', class_='bd-chapter')
        for ch in chapters:
            eyebrow = ch.find('span', class_='ch-eyebrow')
            eye_txt = clean_text(eyebrow.get_text()) if eyebrow else ""
            title_el = ch.find('h3', class_='ch-title')
            t_txt = clean_text(title_el.get_text()) if title_el else ""
            
            p(f"### {eye_txt}：{t_txt}")
            p()
            
            narrative = ch.find('div', class_='ch-narrative')
            if narrative:
                for child in narrative.children:
                    if child.name == 'p':
                        txt = clean_text(child.get_text())
                        if txt:
                            p(txt)
                            p()
                    elif child.name == 'blockquote':
                        q_p = child.find('p')
                        q_txt = clean_text(q_p.get_text()) if q_p else clean_text(child.get_text())
                        src = child.find('span', class_='src-note')
                        src_txt = f"\n> *—— {clean_text(src.get_text())}*" if src else ""
                        p(f"> \"{q_txt}\"{src_txt}")
                        p()
                    elif child.name in ['ul', 'ol']:
                        for li in child.find_all('li'):
                            p(f"* {clean_text(li.get_text())}")
                        p()
            p()

    p("---")
    p()

    # 4. 批判與判定 (JUDGE)
    p("## 肆、 批判與審判：理論盲區、時代局限與最強反對")
    p()

    judge = soup.find('section', id='panel-judge')
    if judge:
        verdict = judge.find('div', class_='verdict-bar')
        if verdict:
            p("### 4.1 可信度總結判決")
            p()
            p(f"> {clean_text(verdict.get_text())}")
            p()

        arg = judge.find('div', class_='arg-restate')
        if arg:
            p("### 4.2 作者核心論證鏈")
            p()
            ol = arg.find('ol', class_='arg-steps')
            if ol:
                for li in ol.find_all('li'):
                    p(f"1. {clean_text(li.get_text())}")
                p()
            arg_chain = arg.find('p', class_='arg-chain')
            if arg_chain:
                p(f"**【論證因果總結】**：{clean_text(arg_chain.get_text())}")
                p()

        tensions = judge.find('div', class_='tensions')
        if tensions:
            p("### 4.3 書裡自帶的矛盾與體制張力")
            p()
            for card in tensions.find_all('article'):
                h = card.find(['h3', 'h4', 'div', 'strong'])
                b = card.find('p') or card.find('div', class_='tension-desc')
                h_txt = clean_text(h.get_text()) if h else ""
                b_txt = clean_text(b.get_text()) if b else clean_text(card.get_text())
                p(f"* **{h_txt}**：{b_txt}")
                p()

        crit = judge.find('div', class_='crit-quad')
        if crit:
            p("### 4.4 四大批判象限")
            p()
            zones = [
                ("cq-assume", "沒證明的前提 (Unproven Assumptions)"),
                ("cq-blind", "作者盲點 (Blind Spots)"),
                ("cq-era", "時代局限 (Era Limits)"),
                ("cq-object", "最強反對意見 (Strongest Objection)")
            ]
            for z_cls, z_title in zones:
                sec = crit.find('section', class_=z_cls)
                if sec:
                    p(f"#### {z_title}")
                    p()
                    for li in sec.find_all(['li', 'p']):
                        txt = clean_text(li.get_text())
                        if txt:
                            p(f"* {txt}")
                    p()

        reviews = judge.find('div', class_='reviews')
        if reviews:
            p("### 4.5 學界權威書評反響")
            p()
            for r in reviews.find_all('article', class_='rev-card'):
                rev_reviewer = r.find('strong', class_='rev-reviewer')
                rev_verdict = r.find('span', class_='rev-verdict')
                rev_quote = r.find('blockquote', class_='rev-quote')
                rv_txt = clean_text(rev_reviewer.get_text()) if rev_reviewer else ""
                vd_txt = f" —— *{clean_text(rev_verdict.get_text())}*" if rev_verdict else ""
                qt_txt = clean_text(rev_quote.get_text()) if rev_quote else ""
                p(f"* **{rv_txt}**{vd_txt}")
                if qt_txt:
                    p(f"  > {qt_txt}")
                p()

    p("---")
    p()

    # 5. 行動指南與自檢 (ACTION)
    p("## 伍、 實戰指南：決策規則、心智模型與自檢問卷")
    p()

    action = soup.find('section', id='panel-action')
    if action:
        chain = action.find('div', class_='chain')
        if chain:
            p("### 5.1 五環行動路線圖")
            p()
            for step in chain.find_all('div', class_='chain-step'):
                no_el = step.find('span', class_='cs-no')
                label_el = step.find('span', class_='cs-label')
                exp_el = step.find('p', class_='chain-explain')
                det_el = step.find('div', class_='chain-detail')
                
                no_txt = clean_text(no_el.get_text()) if no_el else ""
                l_txt = clean_text(label_el.get_text()) if label_el else ""
                e_txt = clean_text(exp_el.get_text()) if exp_el else ""
                d_txt = clean_text(det_el.get_text()) if det_el else ""
                
                p(f"#### 步驟 {no_txt}：{l_txt}")
                if e_txt:
                    p(f"> **目標**：{e_txt}")
                    p(">")
                if d_txt:
                    p(f"{d_txt}")
                p()

        rules = action.find('div', class_='rules')
        if rules:
            p("### 5.2 七條實戰決策法則 (If-Then Rules)")
            p()
            p("| 情境 (當...) | 決策行動 (做...) | 理論依據 (因為...) | 出處 |")
            p("| :--- | :--- | :--- | :--- |")
            for r in rules.find_all('article', class_='rule-card'):
                when_el = r.find('div', class_='rc-when')
                do_el = r.find('div', class_='rc-do')
                why_el = r.find('div', class_='rc-because')
                anchor_el = r.find('a', class_='rc-anchor')
                
                w_txt = clean_text(when_el.get_text()).replace("當", "", 1).strip() if when_el else ""
                d_txt = clean_text(do_el.get_text()).replace("做", "", 1).strip() if do_el else ""
                y_txt = clean_text(why_el.get_text()).replace("因為", "", 1).strip() if why_el else ""
                a_txt = clean_text(anchor_el.get_text()) if anchor_el else ""
                
                w_txt = w_txt.replace("|", "｜")
                d_txt = d_txt.replace("|", "｜")
                y_txt = y_txt.replace("|", "｜")
                p(f"| {w_txt} | {d_txt} | {y_txt} | {a_txt} |")
            p()

        models = action.find('div', class_='models')
        if models:
            p("### 5.3 五大心智模型")
            p()
            for m in models.find_all('article', class_='model-drawer'):
                name_el = m.find('span', class_='md-name')
                bound_el = m.find('p', class_='md-boundary')
                apply_el = m.find('p', class_='md-apply')
                meta_el = m.find('div', class_='md-meta')
                
                n_txt = clean_text(name_el.get_text()) if name_el else ""
                b_txt = clean_text(bound_el.get_text()) if bound_el else ""
                a_txt = clean_text(apply_el.get_text()) if apply_el else ""
                m_txt = clean_text(meta_el.get_text()) if meta_el else ""
                
                p(f"#### 【心智模型】{n_txt}")
                if m_txt:
                    p(f"> *{m_txt}*")
                    p()
                if b_txt:
                    p(f"* {b_txt}")
                if a_txt:
                    p(f"* {a_txt}")
                p()

        qw = action.find('div', class_='questions-wrap')
        if qw:
            p("### 5.4 讀完自檢問卷")
            p()
            for i, q in enumerate(qw.find_all('article', class_='question')):
                paras = q.find_all('p')
                if len(paras) >= 2:
                    q_txt = clean_text(paras[0].get_text())
                    follow = clean_text(paras[1].get_text())
                else:
                    raw = q.get_text(separator='\n').split('\n')
                    raw = [clean_text(x) for x in raw if clean_text(x)]
                    q_txt = raw[0] if len(raw) > 0 else ""
                    follow = " ".join(raw[1:]) if len(raw) > 1 else ""
                p(f"**Q{i+1}：{q_txt}**")
                if follow:
                    p(f"> 💡 *{follow}*")
                p()

    p("---")
    p()

    # 6. 跨界延伸 (EXTEND)
    p("## 陸、 跨界延伸與主題對讀")
    p()

    extend = soup.find('section', id='panel-extend')
    if extend:
        sim = extend.find('div', class_='similar-books')
        if sim:
            p("### 6.1 同主題經典著作對讀")
            p()
            for b in sim.find_all('article'):
                h = b.find(['h3', 'h4', 'div', 'strong'])
                desc = b.find('p') or b.find('div', class_='book-desc')
                h_txt = clean_text(h.get_text()) if h else ""
                d_txt = clean_text(desc.get_text()) if desc else clean_text(b.get_text())
                p(f"* **{h_txt}**")
                p(f"  {d_txt}")
                p()

        rp = extend.find('div', class_='reading-path')
        if rp:
            p("### 6.2 推薦研讀路徑")
            p()
            p(f"> {clean_text(rp.get_text())}")
            p()

        shelf = extend.find('div', class_='shelf-recommend')
        if shelf:
            p("### 6.3 延伸書架推薦")
            p()
            for row in shelf.find_all(['p', 'li', 'article']):
                txt = clean_text(row.get_text())
                if txt:
                    p(f"* {txt}")
            p()

        cd = extend.find('div', class_='cross-domain')
        if cd:
            p("### 6.4 跨領域模型遷移")
            p()
            for item in cd.find_all('article'):
                h = item.find(['h3', 'h4', 'div', 'strong'])
                b = item.find('p') or item.find('div', class_='cd-desc')
                h_txt = clean_text(h.get_text()) if h else ""
                b_txt = clean_text(b.get_text()) if b else clean_text(item.get_text())
                p(f"* **{h_txt}**：{b_txt}")
                p()

        cb = extend.find('div', class_='cross-book')
        if cb:
            p("### 6.5 作者前後思想脈絡串聯")
            p()
            for item in cb.find_all('article', class_='cb-card'):
                h = item.find(['h4', 'h3', 'div', 'strong'])
                b = item.find('p', class_='cb-conn') or item.find('p')
                h_txt = clean_text(h.get_text()) if h else ""
                b_txt = clean_text(b.get_text()) if b else clean_text(item.get_text())
                p(f"* **{h_txt}**：{b_txt}")
                p()

        ft = extend.find('div', class_='final-takeaway')
        if ft:
            p("### 6.6 終局心法")
            p()
            p(f"> {clean_text(ft.get_text())}")
            p()

    p("---")
    p()

    # 7. 作者檔案 (SUB-AUTHOR)
    sub_author = soup.find('section', id='sub-author')
    if sub_author:
        p("## 柒、 作者專題檔案：布萊恩·瓊斯與法蘭克·鮑姆加特納")
        p()
        for sec in sub_author.find_all('section', class_='au-sec'):
            h = sec.find(['h2', 'h3', 'h4'])
            h_txt = clean_text(h.get_text()) if h else ""
            p(f"### {h_txt}")
            p()
            for p_elem in sec.find_all('p'):
                txt = clean_text(p_elem.get_text())
                if txt:
                    p(txt)
                    p()
            for li in sec.find_all('li'):
                p(f"* {clean_text(li.get_text())}")
            p()

    p("---")
    p()

    # 8. 學派爭鳴 (SUB-VIEWS)
    sub_views = soup.find('section', id='sub-views')
    if sub_views:
        p("## 捌、 學派爭鳴與觀點對照")
        p()
        for card in sub_views.find_all(['div', 'article'], class_=re.compile(r'debate|card|view')):
            h = card.find(['h2', 'h3', 'h4', 'div', 'strong'])
            h_txt = clean_text(h.get_text()) if h else ""
            if h_txt and not any(ign in h_txt for ign in ['學派爭鳴與觀點對照 · 專題檔案']):
                p(f"### {h_txt}")
                p()
                for p_elem in card.find_all('p'):
                    txt = clean_text(p_elem.get_text())
                    if txt:
                        p(txt)
                        p()

    full_md = "\n".join(lines)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_md)

    return md_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python html_to_markdown.py <html_path> [output_md_path]")
        sys.exit(1)
    in_html = sys.argv[1]
    out_md = sys.argv[2] if len(sys.argv) > 2 else None
    res = convert_html_to_markdown(in_html, out_md)
    print(f"轉換完成: {res}")
