// Builds pdf/*.pdf: one printable workbook per 問題 type per book, answer key at the end.
// Usage: node pdf.js   (needs Playwright + Chromium + curl; fonts are cached in .fonts/)
const fs=require('fs'),path=require('path'),vm=require('vm');
const {execFileSync}=require('child_process');
const {chromium}=require('playwright');

const ctx={D:[],X:{}};vm.createContext(ctx);
const dir=path.join(__dirname,'data');
for(const f of fs.readdirSync(dir).filter(f=>f.endsWith('.js')).sort())vm.runInContext(fs.readFileSync(path.join(dir,f),'utf8'),ctx);
const UNITS=ctx.D.map(u=>({...u,book:u.book||'v'}));

const BOOKN={v:'文字・語彙',g:'文法'},BOOKF={v:'文字語彙',g:'文法'};
const SEC={
 1:{jp:'問題1',nm:'漢字読み',vi:'Cách đọc Kanji',ins:'＿＿の言葉の読み方として最もよいものを、1・2・3・4から一つ選びなさい。'},
 2:{jp:'問題2',nm:'表記',vi:'Viết bằng Kanji',ins:'＿＿の言葉を漢字で書くとき、最もよいものを1・2・3・4から一つ選びなさい。'},
 3:{jp:'問題3',nm:'文脈規定',vi:'Điền từ theo ngữ cảnh',ins:'（　）に入れるのに最もよいものを、1・2・3・4から一つ選びなさい。'},
 4:{jp:'問題4',nm:'語形成',vi:'Cấu tạo từ',ins:'（　）に入れるのに最もよいものを、1・2・3・4から一つ選びなさい。'},
 5:{jp:'問題5',nm:'言い換え類義',vi:'Từ gần nghĩa',ins:'＿＿の言葉に意味が最も近いものを、1・2・3・4から一つ選びなさい。'},
 6:{jp:'問題6',nm:'用法',vi:'Cách dùng từ',ins:'次の言葉の使い方として最もよいものを、1・2・3・4から一つ選びなさい。'},
 7:{jp:'集中',nm:'集中トレーニング',vi:'Luyện tập tập trung',ins:'（　）の中のaとbのうち、文に合うほうを選びましょう。'},
 11:{jp:'問題1',nm:'文法形式の判断',vi:'Chọn mẫu ngữ pháp',ins:'次の文の（　）に入れるのに最もよいものを、1・2・3・4から一つ選びなさい。'},
 12:{jp:'問題2',nm:'文の組み立て',vi:'Sắp xếp câu ★',ins:'次の文の ＿★＿ に入る最もよいものを、1・2・3・4から一つ選びなさい。'},
 13:{jp:'問題3',nm:'文章の文法',vi:'Ngữ pháp đoạn văn',ins:''},
 17:{jp:'集中',nm:'集中トレーニング',vi:'Luyện tập tập trung',ins:'（　）の中のaとbのうち、文に合うほうを選びましょう。'}
};
const FILES=[['v',[1,2,3,4,5,6,7]],['g',[11,12,13,17]]];

const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmtO=t=>esc(t).replace(/\{([^}]*)\}/g,'<u>$1</u>');
const fmtQ=t=>fmtO(t).replace(/（　）/g,'<span class="blank">（　　　）</span>').replace(/\n/g,'<br>');
const label=(t,n)=>t===7||t===17?'ab'[n-1]:String(n);
const fullStar=q=>q.q.replace('〔★〕',q.ord.map(n=>q.o[n-1]).join(''));
const uref=u=>u.title+(u.pages?`<span class="pg">tr. ${esc(u.pages)}</span>`:'');

function optsHTML(q,t){
 const ml=Math.max(...q.o.map(x=>x.replace(/[{}]/g,'').length));
 const lay=t===6?'c1':q.o.length===2?'c2':ml>14?'c1':ml>6?'c2':'c4';
 return `<ol class="opts ${lay}">${q.o.map((o,i)=>`<li><span class="k">${label(t,i+1)}</span><span class="jp">${fmtO(o)}</span></li>`).join('')}</ol>`;}

function starQ(q){const [a,b]=esc(q.q).split('〔★〕');
 const sl=[0,1,2,3].map(i=>`<span class="slot${i===2?' st':''}">${i===2?'★':''}</span>`).join('');
 return (a+sl+(b||'')).replace(/\n/g,'<br>');}

function passage(s){
 const body=s.p.split('\n').filter(x=>x.trim()).map(par=>`<p>${esc(par).replace(/\[(\d)(?:-([abc]))?\]/g,(m,n,l)=>`<span class="pbox">${l?n+'-'+l:n}</span>`)}</p>`).join('');
 return `<div class="passage jp">${body}${s.src?`<div class="src">（${esc(s.src)}）</div>`:''}</div>`;}

function qHTML(q,qi,t){
 let qt;
 if(t===6)qt=`<span class="word">${esc(q.q)}</span>`;
 else if(t===12)qt=starQ(q);
 else if(t===13)qt=`<span class="pbox">${qi+1}</span>`;
 else qt=fmtQ(q.q);
 return `<div class="q"><div class="qn">${qi+1}</div><div class="qb"><div class="qt jp">${qt}</div>${optsHTML(q,t)}</div></div>`;}

function keyLine(q,qi,t){
 const a=label(t,q.a),ans=q.o[q.a-1];
 let main=`<b class="ka">${a}</b> <span class="jp">${fmtO(ans)}</span>`;
 if(t===12)main=`<b class="ka">${a}</b> <span class="jp">★ = ${fmtO(ans)}</span> <span class="ord">thứ tự ${q.ord.join('→')}</span><div class="jp full">${esc(fullStar(q))}</div>`;
 else if(t===6)main=`<b class="ka">${a}</b>`;
 const extra=[];
 if(q.vi&&t!==13)extra.push(`<div class="vi">${esc(q.vi).replace(/\n/g,'<br>')}</div>`);
 if(q.ex)extra.push(`<div class="ex">${esc(q.ex)}</div>`);
 return `<div class="kl"><div class="kn">${qi+1}</div><div>${main}${extra.join('')}</div></div>`;}

function build(book,t){
 const d=SEC[t];
 const units=UNITS.filter(u=>u.book===book).map(u=>({u,secs:u.secs.filter(s=>s.t===t)})).filter(x=>x.secs.length);
 const nq=units.reduce((a,x)=>a+x.secs.reduce((b,s)=>b+s.qs.length,0),0);
 const title=`${BOOKN[book]} ${d.jp==='集中'?'':d.jp+' '}${d.nm}`;
 let h=`<section class="cover"><div class="eyebrow">日本語パワードリル N2 · ${BOOKN[book]}</div>
 <h1 class="jp">${d.jp==='集中'?'':`<span class="mondai">${d.jp}</span>`}${d.nm}</h1><div class="sub">${d.vi}</div>
 <div class="meta">${units.length} bài · ${nq} câu · đáp án và giải thích ngắn ở cuối file</div>
 ${d.ins?`<div class="ins jp">${esc(d.ins)}</div>`:''}</section>`;
 h+='<main class="qs">';
 units.forEach(({u,secs})=>{
  // heading, passage and first question stay on one page so a heading never ends a page alone
  h+=`<section class="unit">`;
  secs.forEach((s,si)=>{
   let head=si?'':`<h2 class="jp">${uref(u)}</h2>`;
   if(t===13)head+=`<div class="ins jp sm">次の文章を読んで、［1］から［${s.qs.length}］の中に入る最もよいものを、1・2・3・4から一つ選びなさい。</div>`+passage(s);
   const qs=s.qs.map((q,qi)=>qHTML(q,qi,t));
   h+=`<div class="keep">${head}${qs.shift()}</div>`+qs.join('');});
  h+=`<div class="score">Điểm: ＿＿ / ${secs.reduce((a,s)=>a+s.qs.length,0)}</div></section>`;});
 h+='</main>';
 // answer key: quick grid, then per-question explanations
 const maxN=Math.max(...units.map(x=>x.secs.reduce((a,s)=>a+s.qs.length,0)));
 h+=`<section class="key"><h1 class="kh">解答 · Đáp án</h1><h3>Bảng đáp án nhanh</h3><table class="grid"><thead><tr><th></th>${Array.from({length:maxN},(_,i)=>`<th>${i+1}</th>`).join('')}</tr></thead><tbody>`;
 units.forEach(({u,secs})=>{const as=secs.flatMap(s=>s.qs.map(q=>label(t,q.a)));
  h+=`<tr><th class="jp">${esc(u.title)}</th>${Array.from({length:maxN},(_,i)=>`<td>${as[i]||''}</td>`).join('')}</tr>`;});
 h+=`</tbody></table><h3 class="nb">Giải thích từng câu</h3>`;
 units.forEach(({u,secs})=>{
  h+=`<div class="kunit">`;
  secs.forEach((s,si)=>{let head=si?'':`<h4 class="jp">${esc(u.title)}</h4>`;
   if(t===13&&s.pvi)head+=`<div class="pvi"><b>Dịch đoạn văn:</b> ${esc(s.pvi).replace(/\n/g,' ')}</div>`;
   const ks=s.qs.map((q,qi)=>keyLine(q,qi,t));
   h+=`<div class="keep">${head}${ks.shift()}</div>`+ks.join('');});
  h+='</div>';});
 h+='</section>';
 return {title,html:page(title,h),file:`${BOOKF[book]}-${d.jp==='集中'?'集中トレーニング':d.jp+'-'+d.nm}.pdf`};}

const CSS=`
@page{size:A4;margin:16mm 15mm 16mm 15mm}
:root{--ink:#1d1b18;--mut:#6b655c;--line:#cfc8bb;--acc:#9b2c1f;--soft:#f4efe6}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;color:var(--ink);font:10.5pt/1.55 "Noto Sans","Noto Sans JP",sans-serif}
.jp{font-family:"Noto Serif JP",serif}
u{text-decoration:underline;text-decoration-thickness:1.2px;text-underline-offset:3px}
.cover{border-bottom:2px solid var(--ink);padding-bottom:10px;margin-bottom:14px}
.eyebrow{font-size:9pt;letter-spacing:.06em;color:var(--mut);text-transform:uppercase}
h1{font-size:22pt;margin:4px 0 0;line-height:1.3;font-weight:700}
.mondai{display:inline-block;background:var(--ink);color:#fff;border-radius:999px;padding:1px 12px;font-size:13pt;margin-right:10px;vertical-align:4px}
.sub{font-size:12pt;color:var(--mut)}
.meta{font-size:9.5pt;color:var(--mut);margin-top:4px}
.ins{margin-top:8px;padding:6px 10px;border:1px solid var(--line);background:var(--soft);font-size:10.5pt}
.ins.sm{margin:6px 0 8px}
.unit{margin:0 0 12px;padding-top:2px}
.keep{break-inside:avoid}
h2{font-size:13pt;margin:10px 0 4px;padding:2px 0 3px;border-bottom:1px solid var(--line);break-after:avoid;display:flex;align-items:baseline;gap:10px}
.pg{font:9pt "Noto Sans",sans-serif;color:var(--mut)}
.q{display:grid;grid-template-columns:22px 1fr;gap:6px;padding:5px 0;break-inside:avoid}
.qn{font-weight:700;font-size:10pt;width:20px;height:20px;border:1.2px solid var(--ink);border-radius:50%;display:flex;align-items:center;justify-content:center;margin-top:2px}
.qt{font-size:11.5pt;line-height:1.75}
.word{font-size:14pt;font-weight:700}
.blank{white-space:nowrap}
.opts{list-style:none;margin:2px 0 0;padding:0;display:grid;gap:1px 14px;font-size:11pt}
.opts.c4{grid-template-columns:repeat(4,1fr)}.opts.c2{grid-template-columns:repeat(2,1fr)}.opts.c1{grid-template-columns:1fr}
.opts li{display:flex;gap:6px;align-items:baseline}
.k{font-weight:700;min-width:12px;color:var(--mut)}
.slot{display:inline-block;width:3.6em;border-bottom:1.2px solid var(--ink);margin:0 3px;text-align:center;font-size:9pt;line-height:1.2;vertical-align:-1px}
.slot.st{color:var(--acc)}
.passage{border:1px solid var(--line);padding:8px 12px;margin:4px 0 6px;font-size:11pt;line-height:1.9;break-inside:avoid}
.passage p{margin:0 0 4px;text-indent:1em}
.pbox{display:inline-block;min-width:22px;padding:0 5px;border:1.2px solid var(--ink);text-align:center;font:700 9.5pt/1.4 "Noto Sans",sans-serif;margin:0 2px;text-indent:0}
.src{text-align:right;font-size:9pt;color:var(--mut)}
.score{text-align:right;font-size:9pt;color:var(--mut);margin-top:2px}
.key{break-before:page}
.kh{border-bottom:2px solid var(--ink);padding-bottom:6px;margin-bottom:6px}
h3{font-size:11.5pt;margin:12px 0 6px;color:var(--acc)}
h3.nb{break-before:page;margin-top:0}
.grid{border-collapse:collapse;font-size:9.5pt;width:100%}
.grid th,.grid td{border:1px solid var(--line);padding:2px 4px;text-align:center}
.grid tbody th{text-align:left;white-space:nowrap;font-weight:600;background:var(--soft)}
.grid thead th{background:var(--soft)}
.grid tr{break-inside:avoid}
.kunit{margin-bottom:8px}
h4{font-size:11pt;margin:8px 0 2px;padding-bottom:2px;border-bottom:1px solid var(--line);break-after:avoid}
.kl{display:grid;grid-template-columns:20px 1fr;gap:6px;padding:3px 0;font-size:9.5pt;line-height:1.5;break-inside:avoid;border-bottom:1px dotted #e3ddd2}
.kn{font-weight:700;color:var(--mut)}
.ka{display:inline-block;min-width:16px;padding:0 4px;background:var(--ink);color:#fff;border-radius:3px;text-align:center;margin-right:4px}
.ord{color:var(--mut);margin-left:6px}
.full{margin-top:1px}
.vi{color:var(--mut)}
.ex{margin-top:1px}
.pvi{font-size:9pt;color:var(--mut);margin:2px 0 4px;padding:4px 8px;background:var(--soft)}
`;
// Google Fonts serves whole TTFs to curl; fetch once and point @font-face at the local copies
function fontFaces(){
 const fd=path.join(__dirname,'.fonts');fs.mkdirSync(fd,{recursive:true});
 const cssFile=path.join(fd,'fonts.css');
 if(!fs.existsSync(cssFile)){
  let css=execFileSync('curl',['-sSf','https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&family=Noto+Sans+JP:wght@400;700&family=Noto+Serif+JP:wght@400;700'],{encoding:'utf8'});
  css=css.replace(/url\((https:[^)]+)\)/g,(m,u)=>{const f=path.join(fd,path.basename(u));
   if(!fs.existsSync(f))execFileSync('curl',['-sSf','-o',f,u]);return `url("file://${f}")`;});
  fs.writeFileSync(cssFile,css);}
 return fs.readFileSync(cssFile,'utf8');}
const FONTS=fontFaces();
const page=(title,body)=>`<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>${esc(title)}</title>
<style>${FONTS}${CSS}</style></head><body>${body}</body></html>`;

(async()=>{
 const out=path.join(__dirname,'pdf');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch(fs.existsSync('/opt/pw-browsers/chromium')?{executablePath:'/opt/pw-browsers/chromium'}:{});
 const pg=await browser.newPage();
 for(const [book,ts] of FILES)for(const t of ts){
  const {title,html,file}=build(book,t);
  if(process.env.HTML)fs.writeFileSync(path.join(out,file.replace(/\.pdf$/,'.html')),html);
  const tmp=path.join(__dirname,'.fonts','print.html');fs.writeFileSync(tmp,html);
  await pg.goto('file://'+tmp,{waitUntil:'load'});await pg.evaluate(()=>document.fonts.ready);
  await pg.pdf({path:path.join(out,file),format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,
   headerTemplate:'<span></span>',
   footerTemplate:`<div style="width:100%;font-size:8px;color:#888;padding:0 15mm;display:flex;justify-content:space-between;font-family:'Noto Sans JP',sans-serif"><span>${esc(title)}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`});
  console.log(file);}
 await browser.close();})();
