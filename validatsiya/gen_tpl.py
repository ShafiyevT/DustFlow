import re
exec(open('refs.py',encoding='utf-8').read())
txt="".join(open(f,encoding='utf-8').read()+"\n\n" for f in ["m1.md","m2.md","m3.md"])
CIT=r'\[@[A-Za-z0-9]+(?:;@[A-Za-z0-9]+)*\]'
order=[]
for g in re.findall(CIT,txt):
    for k in re.findall(r'@([A-Za-z0-9]+)',g):
        if k not in order: order.append(k)
miss=[k for k in order if k not in R]; unused=[k for k in R if k not in order]
assert not miss, miss
num={k:i+1 for i,k in enumerate(order)}
def grp(m):
    ns=sorted(num[k] for k in re.findall(r'@([A-Za-z0-9]+)',m.group(0))); out=[];i=0
    while i<len(ns):
        j=i
        while j+1<len(ns) and ns[j+1]==ns[j]+1: j+=1
        out.append(f"{ns[i]}–{ns[j]}" if j-i>=2 else (f"{ns[i]},{ns[j]}" if j==i+1 else f"{ns[i]}")); i=j+1
    return "["+",".join(out)+"]"
txt=re.sub(CIT,grp,txt)
txt=re.sub(r'\$\$(.*?)\s*\\qquad \((\d+)\)\$\$',lambda m:f"$${m.group(1)}$$ EQNUM{m.group(2)}END",txt,flags=re.S)
def lst(block,style):
    items=re.findall(r'^\d+\. (.*)$',block,re.M); return f'::: {{custom-style="{style}"}}\n'+"\n\n".join(items)+"\n:::\n"
L1=re.search(r'(^1\. Emission and transport are combined.*?)(?=\n\nThe paper is organized)',txt,re.S|re.M).group(1); txt=txt.replace(L1,lst(L1,"TSP_3.7_itemize"))
L2=re.search(r'(^1\. Air is treated as an incompressible medium.*?)(?=\n\nThese assumptions)',txt,re.S|re.M).group(1); txt=txt.replace(L2,lst(L2,"TSP_3.7_itemize_B"))
for a,b in [("title","TSP_1.2_title"),("authors","TSP_1.3_authornames"),("affil","TSP_1.6_affiliation"),("abstract","TSP_1.7_abstract"),("keywords","TSP_1.8_keywords"),("tablecaption","TSP_4.1_table_caption"),("backmatter","TSP_6.2_BackMatter")]:
    txt=txt.replace(f"::: {a}\n",f'::: {{custom-style="{b}"}}\n')
txt=re.sub(r'^Note: (.*)$',r'::: {custom-style="TSP_4.3_table_footer"}\nNote: \1\n:::',txt,flags=re.M)
txt='::: {custom-style="TSP_1.0_doinum"}\nhttps://doi.org/10.32604/cmes.2026.000000\n:::\n\n::: {custom-style="TSP_1.1_article_type"}\nARTICLE\n:::\n\n'+txt
txt+="\n# References {-}\n\n::: {custom-style=\"TSP_7.1_References\"}\n"+"\n\n".join(R[k] for k in order)+"\n:::\n"
open('manuscript_tpl.md','w',encoding='utf-8').write(txt)
body=txt.split("# References")[0]
fo=[];[fo.append(int(f)) for f in re.findall(r'Figs?\. (\d+)',body) if int(f) not in fo]
to=[];[to.append(t) for t in re.findall(r'Tables? ([0-9A]+)',body) if t not in to]
print(f"adabiyotlar {len(order)} (ishlatilmagan: {unused}) | formulalar {txt.count('EQNUM')} | rasm tartibi {fo} | jadval tartibi {to}")
