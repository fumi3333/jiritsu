import sys,os,shutil,json
sys.stdout.reconfigure(encoding='utf8')
import win32com.client as w

import openpyxl,warnings
warnings.simplefilter('ignore')
_o=openpyxl.load_workbook(r'..\t.xlsx',read_only=False).worksheets[0]; _n=openpyxl.load_workbook('nd.xlsx' ,read_only=False).worksheets[0]
_lab={ _n[f'B{r}'].value:r for r in range(5,100) if _n[f'B{r}'].value}
MAP={r:_lab.get(_o[f'B{r}'].value) for r in range(5,100)}
print({k:v for k,v in MAP.items() if v is None and _o[f'B{k}'].value})
sp=os.path.dirname(os.path.abspath(__file__))
dst=os.path.join(sp,'t4.xlsx'); shutil.copy(r'C:\Users\hrfmt\AppData\Local\Temp\claude\18349e3646149b7c\6176077c-bfeb-4cb5-91ac-913fea59e554\scratchpad\form\nd\nd.xlsx',dst)
base={8:'08',9:'11',10:'06',11:'有',12:'継続（更新）',23:'アイ',24:'ウエ',25:'氏甲',26:'名乙',27:'平成',28:'10',29:'05',30:'20',31:'1440052',33:'住所丙',34:'03-1111-2222',59:'KIGO',60:'9876543',61:'06138015',64:'非該当'}
S={'区市町村国保':{}, '組合国保':{53:'本人'}, '健保':{54:'本人'},'船保':{55:'本人'},'各種共済':{56:'本人'},'後期高齢者':{59:''},'生保':{57:'福祉戊'},'その他':{58:'内容甲'}}
x=w.DispatchEx('Excel.Application'); x.Visible=False; x.DisplayAlerts=False
b=x.Workbooks.Open(dst)
try:
  b.Unprotect(); i=b.Worksheets(1)
  for n in range(5,9):
    s=b.Worksheets(n); s.Visible=-1; s.PageSetup.Zoom=False; s.PageSetup.FitToPagesWide=1; s.PageSetup.FitToPagesTall=1
  for r,v in base.items(): i.Range(f'C{MAP[r]}').Value="'"+v
  for k,(name,ex) in enumerate(S.items()):
    for r in [53,54,55,56,57,58]: i.Range(f'C{MAP[r]}').Value=''
    i.Range(f'C{MAP[59]}').Value="'KIGO"
    i.Range(f'C{MAP[52]}').Value=name
    for r,v in ex.items(): i.Range(f'C{MAP[r]}').Value=("'"+v) if v else ''
    x.CalculateFull()
    print(name)
    for n in range(5,9): b.Worksheets(n).ExportAsFixedFormat(0,os.path.join(sp,f'ins{k}_{n-4}.pdf'))
finally:
  b.Close(False); x.Quit()
