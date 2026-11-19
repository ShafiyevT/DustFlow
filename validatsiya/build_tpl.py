import copy, re, zipfile, shutil
from docx import Document
from docx.shared import Cm, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
SRC=Document('body.docx'); T=Document('tpl_orig.docx')
TS={s.name:s for s in T.styles}; SID=lambda n: TS[n].style_id
eq_proto=copy.deepcopy(T.tables[2]._tbl); tab_proto_pr=copy.deepcopy(T.tables[1]._tbl.tblPr)
for tag in ('w:bidiVisual','w:tblLayout','w:tblCellMar','w:tblBorders'):
    for e in tab_proto_pr.findall(qn(tag)): tab_proto_pr.remove(e)
for pr in eq_proto.iter(qn('w:tblPr')):
    for e in pr.findall(qn('w:bidiVisual')): pr.remove(e)
mar=OxmlElement('w:tblCellMar')
for side,w in (("top","20"),("left","85"),("bottom","20"),("right","85")):
    e=OxmlElement(f'w:{side}'); e.set(qn('w:w'),w); e.set(qn('w:type'),'dxa'); mar.append(e)
tab_proto_pr.append(mar)
brd=OxmlElement('w:tblBorders')
for side,v in (("top","single"),("bottom","single"),("left","nil"),("right","nil"),("insideH","nil"),("insideV","nil")):
    e=OxmlElement(f'w:{side}'); e.set(qn('w:val'),v)
    if v=="single": e.set(qn('w:sz'),'8'); e.set(qn('w:color'),'000000')
    brd.append(e)
tab_proto_pr.append(brd)
body=T.element.body
for el in list(body):
    if el.tag!=qn('w:sectPr'): body.remove(el)
sect=body.find(qn('w:sectPr'))
for e in sect.findall(qn('w:bidi')): sect.remove(e)
def ins(el): sect.addprevious(el); return el
# qoʻshimcha raqamlash: ikkinchi roʻyxat uchun qayta boshlash
npart=T.part.numbering_part.element
new=OxmlElement('w:num'); new.set(qn('w:numId'),'901'); a=OxmlElement('w:abstractNumId'); a.set(qn('w:val'),'1'); new.append(a)
lo=OxmlElement('w:lvlOverride'); lo.set(qn('w:ilvl'),'0'); so=OxmlElement('w:startOverride'); so.set(qn('w:val'),'1'); lo.append(so); new.append(lo); npart.append(new)
MAP={"Heading 1":"TSP_2.1_heading1","Heading 2":"TSP_2.2_heading2","Heading 3":"TSP_2.3_heading3","Body Text":"TSP_3.1_text","First Paragraph":"TSP_3.1_text",
     "Image Caption":"TSP_5.1_figure_caption","TSP_3.7_itemize_B":"TSP_3.7_itemize","Compact":"TSP_3.1_text"}
figs=[f"fig/Fig{i}.png" for i in range(1,11)]; fi=0; prev_eq=False; n_eq=0; pending=None
def set_style(p_el,name):
    pPr=p_el.find(qn('w:pPr'))
    if pPr is None: pPr=OxmlElement('w:pPr'); p_el.insert(0,pPr)
    ps=pPr.find(qn('w:pStyle'))
    if ps is None: ps=OxmlElement('w:pStyle'); pPr.insert(0,ps)
    ps.set(qn('w:val'),SID(name))
    for tag in ('w:numPr',):   # pandoc raqamlashini olib tashlash
        e=pPr.find(qn(tag))
        if e is not None: pPr.remove(e)
    return pPr
for el in SRC.element.body:
    tag=el.tag
    if tag==qn('w:sectPr'): continue
    if tag==qn('w:tbl'):
        t=copy.deepcopy(el); old=t.find(qn('w:tblPr')); t.remove(old); t.insert(0,copy.deepcopy(tab_proto_pr))
        for i,tr in enumerate(t.findall(qn('w:tr'))):
            for tc in tr.findall(qn('w:tc')):
                for p in tc.findall(qn('w:p')):
                    set_style(p,"TSP_4.2_table_body")
                    if i==0:
                        for r in p.findall('.//'+qn('w:r')):
                            rPr=r.find(qn('w:rPr'))
                            if rPr is None: rPr=OxmlElement('w:rPr'); r.insert(0,rPr)
                            if rPr.find(qn('w:b')) is None: rPr.append(OxmlElement('w:b'))
        # sarlavha qatori ostiga chiziq
        tr0=t.find(qn('w:tr'))
        for tc in tr0.findall(qn('w:tc')):
            tcPr=tc.find(qn('w:tcPr'))
            if tcPr is None: tcPr=OxmlElement('w:tcPr'); tc.insert(0,tcPr)
            b=OxmlElement('w:tcBorders'); e=OxmlElement('w:bottom'); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:color'),'000000'); b.append(e); tcPr.append(b)
        grid=t.find(qn('w:tblGrid')); cols=grid.findall(qn('w:gridCol')); nc=len(cols); TOT=9360
        first=int(TOT*(0.30 if nc>=5 else 0.36 if nc>=3 else 0.5)); rest=(TOT-first)//max(nc-1,1); ws=[first]+[rest]*(nc-1)
        for c,w in zip(cols,ws): c.set(qn('w:w'),str(w))
        for tr in t.findall(qn('w:tr')):
            for tc,w in zip(tr.findall(qn('w:tc')),ws):
                tcPr=tc.find(qn('w:tcPr'))
                if tcPr is None: tcPr=OxmlElement('w:tcPr'); tc.insert(0,tcPr)
                for e in tcPr.findall(qn('w:tcW')): tcPr.remove(e)
                tw=OxmlElement('w:tcW'); tw.set(qn('w:w'),str(w)); tw.set(qn('w:type'),'dxa'); tcPr.insert(0,tw)
        ins(t); prev_eq=False; continue
    if tag!=qn('w:p'): continue
    from docx.text.paragraph import Paragraph
    P=Paragraph(el,SRC); sname=P.style.name; text=P.text
    if el.xpath('.//w:drawing'):
        np_=T.add_paragraph(); np_.style=TS["TSP_5.2_figure"]; np_.alignment=WD_ALIGN_PARAGRAPH.CENTER
        np_.add_run().add_picture(figs[fi],width=Cm(16.0)); fi+=1
        body.remove(np_._p); ins(np_._p); prev_eq=False; continue
    mps=el.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathPara')
    if mps and not text.replace("EQNUM","").strip()[:0]:
        # koʻrgazmali formula: keyingi belgili xatboshini kutamiz
        if not re.sub(r'\s','',text): pending=mps[0]; continue
    m_eq=re.fullmatch(r'\s*EQNUM(.+?)END\s*',text)
    if m_eq and pending is not None:
        num=m_eq.group(1); n_eq+=1
        t=copy.deepcopy(eq_proto); cells=t.findall('.//'+qn('w:tc'))
        c0p=cells[0].find(qn('w:p')); c1p=cells[1].find(qn('w:p'))
        for ch in list(c0p):
            if ch.tag!=qn('w:pPr'): c0p.remove(ch)
        mp=copy.deepcopy(pending); pending=None
        pp=mp.find('{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathParaPr')
        if pp is None: pp=OxmlElement('m:oMathParaPr'); mp.insert(0,pp)
        for x in pp.findall('{http://schemas.openxmlformats.org/officeDocument/2006/math}jc'): pp.remove(x)
        jc=OxmlElement('m:jc'); jc.set(qn('m:val'),'left'); pp.append(jc)
        c0p.append(mp)
        for ch in list(c1p):
            if ch.tag!=qn('w:pPr'): c1p.remove(ch)
        r=OxmlElement('w:r'); tt=OxmlElement('w:t'); tt.text=f"({num})"; r.append(tt); c1p.append(r)
        ins(t); prev_eq=True; continue
    newp=copy.deepcopy(el)
    target=MAP.get(sname,sname)
    if sname=="TSP_1.6_affiliation" and text.startswith("Received"): target="TSP_1.4_history"
    if target not in TS: target="TSP_3.1_text"
    if prev_eq and target=="TSP_3.1_text" and re.match(r'^(where|with|which|evaluated|limited|and)\b',text.strip()): target="TSP_3.2_text_no_indent"
    pPr=set_style(newp,target)
    if sname=="TSP_3.7_itemize_B":
        nP=OxmlElement('w:numPr'); il=OxmlElement('w:ilvl'); il.set(qn('w:val'),'0'); ni=OxmlElement('w:numId'); ni.set(qn('w:val'),'901'); nP.append(il); nP.append(ni); pPr.append(nP)
    # caption prefiksi qalin
    if target in ("TSP_5.1_figure_caption","TSP_4.1_table_caption"):
        m=re.match(r'^((Figure|Table) [A0-9]+:)',text)
        runs=newp.findall(qn('w:r'))
        if m and runs:
            L=len(m.group(1)); acc=0
            for r in runs:
                t_=r.find(qn('w:t'))
                if t_ is None or acc>=L: continue
                s=t_.text or ""
                if acc+len(s)<=L:
                    rPr=r.find(qn('w:rPr'))
                    if rPr is None: rPr=OxmlElement('w:rPr'); r.insert(0,rPr)
                    rPr.append(OxmlElement('w:b')); acc+=len(s)
                else:
                    k=L-acc; r2=copy.deepcopy(r); t_.text=s[:k]; t_.set(qn('xml:space'),'preserve')
                    rPr=r.find(qn('w:rPr'))
                    if rPr is None: rPr=OxmlElement('w:rPr'); r.insert(0,rPr)
                    rPr.append(OxmlElement('w:b')); r2.find(qn('w:t')).text=s[k:]; r2.find(qn('w:t')).set(qn('xml:space'),'preserve'); r.addnext(r2); acc=L
    ins(newp); prev_eq=False
# rasm fayllari soni nazorati
T.core_properties.title="A Coupled Three-Dimensional Model of Dust Emission and Transport under Wind Erosion Accounting for the Physical and Mechanical Properties of Particles"
T.core_properties.author="Madina Bobojonova; Tursun Shafiyev; Normakhmad Ravshanov"
T.save('/mnt/user-data/outputs/CMES_manuscript.docx')
print(f"rasmlar {fi}/10, formulalar {n_eq}/21")
