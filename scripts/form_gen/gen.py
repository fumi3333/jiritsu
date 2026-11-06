import fitz,json,csv,glob,sys,os
sys.stdout.reconfigure(encoding='utf8')
OUT=r'C:\zax-portfolio\jiritsu\form'
def sp(f):
  o=[]
  for b in fitz.open(f)[0].get_text('dict')['blocks']:
    for l in b.get('lines',[]):
      for s in l['spans']:
        if s['text'].strip(): o.append(dict(t=s['text'].strip(),b=s['bbox'],s=s['size']))
  return o
def diff(a,b):
  A={(x['t'],tuple(round(v,1) for v in x['b'])) for x in sp(a)}
  return [x for x in sp(b) if (x['t'],tuple(round(v,1) for v in x['b'])) not in A]
P={}
# page 1 selectors: (text, y approx, x approx)
def pick(sl,t,y=None,x=None):
  c=[s for s in sl if s['t']==t and (y is None or abs(s['b'][1]-y)<6) and (x is None or abs(s['b'][0]-x)<8)]
  assert c,(t,y,x); return c[0]
sel={'year':('令和08',),'month':('11',44.7),'day':('06',44.7),'notify':('有',),'type':('継続（更新）',140.3),'subsidy':('継続（更新）',182),'chg1':('医療機関',150.7),'chg2':('薬局',150.7),
'kana1':('アイ',),'kana2':('ウエ',),'name1':('氏甲',),'name2':('名乙',),'age':('28歳',),'era':('平成',),
'zip1':('144',255),'zip2':('0052',),'addr':('東京都大田区蒲田住所丙',),'tel1':('03',255),'tel2':('1111',),'tel3':('2222',),
'kigo':('KIGO',),'num':('9876543',),'same':('同一丁',),'income':('低Ⅱ',),'severe':('非該当',),
'hzip1':('144',441.6),'hzip2':('0053',),'haddr':('東京都大田区蒲田本町病住戊',),'hname':('病名己',),'htel1':('04',),'htel2':('3333',),'htel3':('4444',),
'pzip1':('144',486),'pzip2':('0054',),'paddr':('東京都大田区新蒲田薬住庚',),'pname':('薬名辛',),'ptel1':('05',),'ptel2':('5555',),'ptel3':('6666',),'nzip1':('144',531),'nzip2':('0055',),'naddr':('東京都大田区仲六郷看住壬',),'nname':('看名癸',),'ntel1':('06',562.5),'ntel2':('7777',),'ntel3':('8888',)}
digits={'birth':(238.6,[497.4,508.2,525.5,536.3,553.5,564.4]),'insurer':(403.2,[468.1,482.1,496.2,510.2,524.3,538.3,552.3,566.4]),'hcode':(450,[482.1,496.2,510.2,524.3,538.3,552.3,566.4]),'pcode':(494.6,[482.1,496.2,510.2,524.3,538.3,552.3,566.4]),'ncode':(539.5,[482.1,496.2,510.2,524.3,538.3,552.3,566.4])}
refs=diff('tpl1.pdf','smp1.pdf')
out={k:[] for k in list(sel)+[f'{k}{i}' for k,(y,xs) in digits.items() for i in range(len(xs))]}
def r(s): return [round(v,1) for v in s['b']]+[round(s['s'],1)]
base={}
for k,a in sel.items(): base[k]=pick(refs,a[0],a[1] if len(a)>1 else None)
for k,(y,xs) in digits.items():
  for i,x in enumerate(xs):
    c=[s for s in refs if abs(s['b'][1]-y)<2 and abs(s['b'][0]-x)<2]; assert c,(k,i); base[f'{k}{i}']=c[0]
ins={}
names=['区市町村国保','組合国保','健保','船保','各種共済','後期高齢者','生保','その他']
for pg in (1,3,4):
  cur=diff(f'tpl{pg}.pdf',f'smp{pg}.pdf') if pg>1 else refs
  def order(L):
    L=sorted(L,key=lambda c:c['b'][1]); rows=[]
    for c in L:
      if rows and c['b'][1]-rows[-1][0]['b'][1]<4: rows[-1].append(c)
      else: rows.append([c])
    return [c for row in rows for c in sorted(row,key=lambda c:c['b'][0])]
  from collections import defaultdict
  gb=defaultdict(list)
  for k,s in base.items(): gb[s['t']].append((k,s))
  for t,items in gb.items():
    cs=order([c for c in cur if c['t']==t])
    ks=order([dict(s,k=k) for k,s in items])
    assert len(cs)==len(ks),(pg,t,len(cs),len(ks))
    for kk,c in zip(ks,cs): out[kk['k']].append(r(c))
  for i,n in enumerate(names):
    d=diff(f'tpl{pg}.pdf',f'ins{i}_{pg}.pdf')
    if False: pass
    bx=[c for c in d if '■' in c['t']][0]
    if bx['t']!='■': bx=dict(bx,b=(bx['b'][2]-bx['s'],bx['b'][1],bx['b'][2],bx['b'][3]),t='■')
    subs=[c for c in d if c['t'] in('本人','福祉戊','内容甲') and abs(c['b'][1]-bx['b'][1])<14]
    # 候補のうち、基本シナリオに無いもの
    ins.setdefault(n,{'box':[],'sub':[]})
    ins[n]['box'].append(r(bx)); ins[n]['sub'].append(r(subs[0]) if subs else None)
out['ins']=ins
# sheet 2
c2=sp('smp2.pdf'); d2=diff('tpl2.pdf','smp2.pdf')
def q(t,y=None,x=None): return r(pick(d2,t,y,x))
P2={'year':q('令和08'),'month':q('11',39.8),'day':q('06',39.8),'notify':q('有'),'sub2':q('（　継続（更新））'),'name1':q('氏甲'),'name2':q('名乙'),'era':q('4H'),
'zip1':q('144'),'zip2':q('0052'),'tel1':q('03'),'tel2':q('1111'),'tel3':q('2222'),'addr':q('東京都大田区蒲田住所丙'),'kigo':q('KIGO'),'num':q('9876543')}
for i,x in enumerate([492.8,503.0,525.5,535.7,558.1,568.3]): P2[f'birth{i}']=r([c for c in d2 if abs(c['b'][1]-216.7)<2 and abs(c['b'][0]-x)<2][0])
X8=[458.0,474.3,490.7,507.0,523.3,539.6,555.9,572.3]
for i,x in enumerate(X8): P2[f'insurer{i}']=r([c for c in d2 if abs(c['b'][1]-364.4)<2 and abs(c['b'][0]-x)<2][0])
for k,y in (('hcode',402.7),('pcode',443.7),('ncode',487.3)):
  for i,x in enumerate(X8[1:]): P2[f'{k}{i}']=r([c for c in d2 if abs(c['b'][1]-y)<2 and abs(c['b'][0]-x)<2][0])
a=q('ア');bb=q('イ');u=q('ウ');e=q('エ')
for i in range(12):
  d1=bb[0]-a[0]; d2_=e[0]-u[0]
  P2[f'k1_{i}']=[round(a[0]+d1*i,1),a[1],round(a[2]+d1*i,1),a[3],a[4]]
  P2[f'k2_{i}']=[round(u[0]+d2_*i,1),u[1],round(u[2]+d2_*i,1),u[3],u[4]]
out['p2']=P2
codes={}
for i,n in enumerate(names):
  d=diff('tpl2.pdf',f'ins{i}_2.pdf'); base2={(c['t'],round(c['b'][0])) for c in d2}
  cand=[c for c in d if c['t'] in '6M１Ⅾ8G K８9９ ' or c['t'] in('Ⅾ','K','８','  ９','９','G','M','6','１')]
  cand=[c for c in cand if c['b'][1]>290 and c['b'][1]<362]
  assert cand,n
  codes[n]=r(cand[0]); print(n,cand[0]['t'],r(cand[0]))
out['p2ins']=codes
json.dump(out,open(os.path.join(OUT,'pos.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
# templates: remove placeholders
R=[]
for pg in range(1,5):
  d=fitz.open(f'tpl{pg}.pdf'); p=d[0]
  fill={ (s['t'],tuple(round(v,1) for v in s['b'])) for s in sp(f'smp{pg}.pdf')}
  for s in sp(f'tpl{pg}.pdf'):
    if (s['t'],tuple(round(v,1) for v in s['b'])) not in fill and s['t']=='0':
      p.add_redact_annot(fitz.Rect(s['b']),fill=(1,1,1))
  p.apply_redactions()
  p.get_pixmap(dpi=170,colorspace=fitz.csGRAY).save(os.path.join(OUT,f'p{pg}.png'))
# postal map
M={}
for f in sorted(glob.glob(r'C:\shinsei\data\tokyo\2026-10\*.csv')):
  for x in csv.DictReader(open(f,encoding='utf8')):
    M[x['kind'][0]+x['code'].zfill(7)]=x['postal_code'].replace('-','')
json.dump(M,open(os.path.join(OUT,'postal.json'),'w'),separators=(',',':'))
print(len(M),[ (n,ins[n]['sub'][0]) for n in ins])
