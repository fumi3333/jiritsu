import fitz,json,os,sys
sys.stdout.reconfigure(encoding='utf8')
OUT=r'C:\zax-portfolio\jiritsu\form\nd'
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
def r(s): return [round(v,1) for v in s['b']]+[round(s['s'],1)]
def nth(d,t,n=0):
  c=sorted([x for x in d if x['t']==t],key=lambda x:(x['b'][1],x['b'][0]))
  return c[n] if len(c)>n else None
def seq(d,st):
  # 1文字ずつ並ぶ行から、文字列に一致する並びを探す
  rows={}
  for x in d:
    if len(x['t'])==1 and (x['t'].isdigit()): rows.setdefault(round(x['b'][1]/2),[]).append(x)
  merged={}
  for k,v in rows.items(): merged.setdefault(k,[]).extend(v)
  for k in sorted(merged):
    L=sorted(merged[k]+merged.get(k+1,[]),key=lambda x:x['b'][0])
    s=''.join(x['t'] for x in L)
    i=s.find(st)
    if i>=0: return L[i:i+len(st)]
  return None
out={}
def put(k,pg,v):
  out.setdefault(k,{})[pg]=r(v) if v else None
names=['区市町村国保','組合国保','健保','船保','各種共済','後期高齢者','生保','その他']
codes={'区市町村国保':'6','組合国保':'M','健保':'１','船保':'Ⅾ','各種共済':'G','後期高齢者':'K','生保':'８','その他':'９'}
ins={n:{'box':[],'sub':[]} for n in names}; p2ins={}
P2={}
for pg in (1,2,3,4):
  d=diff(f'tpl{pg}.pdf',f'smp{pg}.pdf')
  S={'year':nth(d,'令和08'),'month':nth(d,'11'),'day':nth(d,'06'),'notify':nth(d,'有'),'name1':nth(d,'氏甲'),'name2':nth(d,'名乙'),'kigo':nth(d,'KIGO'),'num':nth(d,'9876543'),'zip1':nth(d,'144',0),'zip2':nth(d,'0052'),'tel1':nth(d,'03'),'tel2':nth(d,'1111'),'tel3':nth(d,'2222')}
  S['addr']=next((x for x in d if '住所丙' in x['t']),None)
  if pg!=2:
    S.update({'type':nth(d,'継続（更新）',0),'subsidy':nth(d,'継続（更新）',1),'kana1':nth(d,'アイ'),'kana2':nth(d,'ウエ'),'age':nth(d,'28歳'),'era':nth(d,'平成'),'same':nth(d,'同一丁'),'income':nth(d,'低Ⅱ'),'severe':nth(d,'非該当'),
      'hzip1':nth(d,'144',1),'hzip2':nth(d,'0053'),'hname':nth(d,'病名己'),'htel1':nth(d,'04'),'htel2':nth(d,'3333'),'htel3':nth(d,'4444'),'pzip1':nth(d,'144',2),'pzip2':nth(d,'0054'),'pname':nth(d,'薬名辛'),'ptel1':nth(d,'05'),'ptel2':nth(d,'5555'),'ptel3':nth(d,'6666')})
    S['haddr']=next((x for x in d if '病住戊' in x['t']),None); S['paddr']=next((x for x in d if '薬住庚' in x['t']),None)
  else:
    S['sub2']=next((x for x in d if x['t'].startswith('（') and '継続' in x['t']),None); S['era']=nth(d,'4H')
    a,b,u,e=nth(d,'ア'),nth(d,'イ'),nth(d,'ウ'),nth(d,'エ')
    for i in range(12):
      d1=b['b'][0]-a['b'][0]; d2=e['b'][0]-u['b'][0]
      S[f'k1_{i}']=dict(a,b=(a['b'][0]+d1*i,a['b'][1],a['b'][2]+d1*i,a['b'][3])); S[f'k2_{i}']=dict(u,b=(u['b'][0]+d2*i,u['b'][1],u['b'][2]+d2*i,u['b'][3]))
  for k,st in (('birth','100520'),('insurer','06138015'),('hcode','7654321'),('pcode','1234560'),('ncode','2468013')):
    L=seq(d,st)
    if not L: print('NOSEQ',pg,k); continue
    for i,x in enumerate(L): S[f'{k}{i}']=x
  miss=[k for k,v in S.items() if v is None]
  if miss: print('missing',pg,miss)
  if pg==2:
    P2={k:r(v) for k,v in S.items() if v}
  else:
    for k,v in S.items(): put(k,pg,v)
  for i,n in enumerate(names):
    dd=diff(f'tpl{pg}.pdf',f'ins{i}_{pg}.pdf')
    if pg==2:
      c=[x for x in dd if codes[n] in x['t'] and 270<x['b'][1]<400 and len(x['t'])<5]
      p2ins[n]=r(c[0]) if c else None
      if not c: print('nocode',n)
    else:
      bx=next(x for x in dd if '■' in x['t'])
      if bx['t']!='■': bx=dict(bx,b=(bx['b'][2]-bx['s'],bx['b'][1],bx['b'][2],bx['b'][3]))
      subs=[x for x in dd if x['t'] in('本人','福祉戊','内容甲') and abs(x['b'][1]-bx['b'][1])<14]
      ins[n]['box'].append(r(bx)); ins[n]['sub'].append(r(subs[0]) if subs else None)
res={k:[v.get(1),v.get(3),v.get(4)] for k,v in out.items()}
res['ins']=ins;res['p2']=P2;res['p2ins']=p2ins
json.dump(res,open(os.path.join(OUT,'pos.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
for pg in range(1,5):
  d=fitz.open(f'tpl{pg}.pdf'); p=d[0]
  fill={(s['t'],tuple(round(v,1) for v in s['b'])) for s in sp(f'smp{pg}.pdf')}
  for s in sp(f'tpl{pg}.pdf'):
    if ((s['t'],tuple(round(v,1) for v in s['b'])) not in fill and s['t']=='0') or s['t'].endswith('/5'):
      R=fitz.Rect(s['b'])
      if len(s['t'])>3: R.x0=R.x1-16
      p.add_redact_annot(R,fill=(1,1,1))
  p.apply_redactions()
  p.get_pixmap(dpi=170,colorspace=fitz.csGRAY).save(os.path.join(OUT,f'p{pg}.png'))
print('ok',len(res))
