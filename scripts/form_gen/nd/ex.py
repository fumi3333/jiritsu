import sys,os,shutil
sys.stdout.reconfigure(encoding='utf8')
import win32com.client as w

import openpyxl,warnings
warnings.simplefilter('ignore')
_o=openpyxl.load_workbook(r'..\t.xlsx',read_only=False).worksheets[0]; _n=openpyxl.load_workbook('nd.xlsx',read_only=False).worksheets[0]
_lab={ _n[f'B{r}'].value:r for r in range(5,100) if _n[f'B{r}'].value}
MAP={r:_lab.get(_o[f'B{r}'].value) for r in range(5,100)}
print({k:v for k,v in MAP.items() if v is None and _o[f'B{k}'].value})
sp=os.path.dirname(os.path.abspath(__file__))
dst=os.path.join(sp,'t3.xlsx'); shutil.copy(r'C:\Users\hrfmt\AppData\Local\Temp\claude\18349e3646149b7c\6176077c-bfeb-4cb5-91ac-913fea59e554\scratchpad\form\nd\nd.xlsx',dst)
V={8:'08',9:'11',10:'06',11:'有',12:'継続（更新）',20:'継続（更新）',23:'アイ',24:'ウエ',25:'氏甲',26:'名乙',27:'平成',28:'10',29:'05',30:'20',31:'1440052',33:'住所丙',34:'03-1111-2222',
52:'健保',54:'本人',59:'KIGO',60:'9876543',61:'06138015',62:'同一丁',64:'非該当',65:'低Ⅱ',68:'1440053',70:'病住戊',71:'病名己',72:'04-3333-4444',73:'7654321',74:'1440054',76:'薬住庚',77:'薬名辛',78:'05-5555-6666',79:'1234560',80:'1440055',82:'看住壬',83:'看名癸',84:'06-7777-8888',85:'2468013'}
x=w.DispatchEx('Excel.Application'); x.Visible=False; x.DisplayAlerts=False
b=x.Workbooks.Open(dst)
try:
  b.Unprotect(); i=b.Worksheets(1)
  p=b.Worksheets(2)
  print('prot',p.ProtectContents)
  def exp(tag):
    for n in range(5,9):
      s=b.Worksheets(n); s.Visible=-1
      s.PageSetup.Zoom=False; s.PageSetup.FitToPagesWide=1; s.PageSetup.FitToPagesTall=1
      s.ExportAsFixedFormat(0,os.path.join(sp,f'{tag}{n-4}.pdf'))
  exp('tpl')
  for r,v in V.items():
    if MAP[r]: i.Range(f'C{MAP[r]}').Value="'"+v
  x.CalculateFull(); print([i.Range(f'B{r}').Value for r in range(7,99) if i.Range(f'E{r}').Value=='NG'])
  exp('smp')
finally:
  b.Close(False); x.Quit()
