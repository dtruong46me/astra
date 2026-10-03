// Builds dist/index.html: app.html with every data/*.js inlined.
const fs=require('fs'),path=require('path');
const dir=path.join(__dirname,'data');
const data=fs.readdirSync(dir).filter(f=>f.endsWith('.js')).sort().map(f=>fs.readFileSync(path.join(dir,f),'utf8')).join('\n');
const html=fs.readFileSync(path.join(__dirname,'app.html'),'utf8').replace('/*DATA*/',()=>data);
fs.mkdirSync(path.join(__dirname,'dist'),{recursive:true});
fs.writeFileSync(path.join(__dirname,'dist','index.html'),html);
console.log('dist/index.html',(html.length/1024).toFixed(0)+'KB');
