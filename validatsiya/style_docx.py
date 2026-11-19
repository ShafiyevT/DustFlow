from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re, sys
d=Document(sys.argv[1])
for s in d.sections:
    s.page_width=Cm(21.0); s.page_height=Cm(29.7); s.left_margin=s.right_margin=Cm(2.2); s.top_margin=s.bottom_margin=Cm(2.5)
S={s.name:s for s in d.styles}
def font(st,size,bold=None,italic=None,name="Times New Roman"):
    f=st.font; f.name=name; f.size=Pt(size); f.color.rgb=RGBColor(0,0,0)
    rpr=st.element.get_or_add_rPr(); rf=rpr.find(qn('w:rFonts'))
    if rf is None: rf=OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii','w:hAnsi','w:eastAsia','w:cs'): rf.set(qn(a),name)
    for a in ('w:asciiTheme','w:hAnsiTheme','w:eastAsiaTheme','w:cstheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    if bold is not None: f.bold=bold
    if italic is not None: f.italic=italic
for n in ["Normal","Body Text","First Paragraph","Compact"]:
    font(S[n],11); pf=S[n].paragraph_format; pf.space_after=Pt(4); pf.line_spacing=1.08
    if n!="Compact": pf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for n,sz in [("Heading 1",12),("Heading 2",11)]:
    font(S[n],sz,bold=True,italic=False); S[n].paragraph_format.space_before=Pt(10); S[n].paragraph_format.space_after=Pt(5)
for n in ["Image Caption","Captioned Figure","Figure"]:
    font(S[n],10,italic=False); S[n].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER; S[n].paragraph_format.space_after=Pt(8)
cs={"TSP Title":(16,True,WD_ALIGN_PARAGRAPH.CENTER),"TSP Authors":(12,False,WD_ALIGN_PARAGRAPH.CENTER),"TSP Affiliation":(9.5,False,WD_ALIGN_PARAGRAPH.CENTER),
    "TSP Abstract":(10,False,WD_ALIGN_PARAGRAPH.JUSTIFY),"TSP Keywords":(10,False,WD_ALIGN_PARAGRAPH.JUSTIFY),"TSP Table Caption":(10,False,WD_ALIGN_PARAGRAPH.CENTER),
    "TSP Back Matter":(10,False,WD_ALIGN_PARAGRAPH.JUSTIFY)}
for n,(sz,b,al) in cs.items():
    if n in S:
        font(S[n],sz,bold=b); S[n].paragraph_format.alignment=al; S[n].paragraph_format.space_after=Pt(6 if n!="TSP Table Caption" else 3)
        if n=="TSP Table Caption": S[n].paragraph_format.keep_with_next=True; S[n].paragraph_format.space_before=Pt(6)
def chegara(p,top,bottom):
    pPr=p._p.get_or_add_pPr(); b=OxmlElement('w:pBdr')
    for side,on in (("top",top),("bottom",bottom)):
        if on:
            e=OxmlElement(f'w:{side}'); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'6'); e.set(qn('w:space'),'4'); e.set(qn('w:color'),'000000'); b.append(e)
    pPr.append(b)
for p in d.paragraphs:
    sn=p.style.name
    if sn=="TSP Abstract": chegara(p,True,False)
    if sn=="TSP Keywords": chegara(p,False,True)
    if sn in ("Image Caption","TSP Table Caption") and p.runs:
        full="".join(r.text for r in p.runs); m=re.match(r'^(Figure|Table) \d+:',full)
        if m:
            # formatlangan run'larni saqlab, faqat prefiksni qalin qilamiz
            acc=0; L=len(m.group(0))
            for r in p.runs:
                if acc>=L: break
                t=r.text
                if acc+len(t)<=L: r.bold=True; acc+=len(t)
                else:
                    k=L-acc; head,tail=t[:k],t[k:]; r.text=head; r.bold=True
                    nr=OxmlElement('w:r'); nr.append(__import__('copy').deepcopy(r._r.rPr)) if r._r.rPr is not None else None
                    tt=OxmlElement('w:t'); tt.set(qn('xml:space'),'preserve'); tt.text=tail; nr.append(tt); r._r.addnext(nr)
                    rp=nr.find(qn('w:rPr'))
                    if rp is not None:
                        bb=rp.find(qn('w:b'))
                        if bb is not None: rp.remove(bb)
                    acc=L
for tb in d.tables:
    tblPr=tb._tbl.tblPr; borders=OxmlElement('w:tblBorders')
    for side in ("top","bottom"):
        e=OxmlElement(f'w:{side}'); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'10'); e.set(qn('w:color'),'000000'); borders.append(e)
    for side in ("left","right","insideH","insideV"):
        e=OxmlElement(f'w:{side}'); e.set(qn('w:val'),'nil'); borders.append(e)
    old=tblPr.find(qn('w:tblBorders'))
    if old is not None: tblPr.remove(old)
    tblPr.append(borders)
    for c in tb.rows[0].cells:
        tcPr=c._tc.get_or_add_tcPr(); tb_=OxmlElement('w:tcBorders'); e=OxmlElement('w:bottom'); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'6'); e.set(qn('w:color'),'000000'); tb_.append(e); tcPr.append(tb_)
        for p in c.paragraphs:
            for r in p.runs: r.bold=True
    for row in tb.rows:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT; p.paragraph_format.space_after=Pt(1)
                for r in p.runs: r.font.size=Pt(9.5); r.font.name="Times New Roman"
d.save(sys.argv[2]); print("saqlandi:",sys.argv[2])
