import sys, zipfile, re, html
def paras(path):
    z=zipfile.ZipFile(path); x=z.read('word/document.xml').decode('utf8')
    out=[]
    for p in re.findall(r'<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>', x, re.S):
        if p.startswith('<w:tbl>'):
            for row in re.findall(r'<w:tr[ >].*?</w:tr>', p, re.S):
                cells=[]
                for c in re.findall(r'<w:tc>.*?</w:tc>', row, re.S):
                    cells.append(' '.join(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', pp)) for pp in re.findall(r'<w:p[ >].*?</w:p>', c, re.S)).strip())
                out.append('| '+' | '.join(cells)+' |')
        else:
            sty=re.search(r'<w:pStyle w:val="([^"]+)"',p)
            t=''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',p))
            if t.strip():
                pre='#'*int(sty.group(1)[-1])+' ' if sty and re.match(r'Heading\d',sty.group(1)) else ''
                out.append(pre+html.unescape(t))
    return out
for f in sys.argv[1:]:
    ps=paras(f); open(f[:-5]+'.txt','w').write('\n'.join(ps))
    print(f, len(ps), sum(len(p.split()) for p in ps))
