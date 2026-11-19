import {el,node,link,option,source,fail,download} from './dom.mjs';
import {filterRecords} from './model.mjs';
let data,shown=[];
function card(row){
 const c=node('article'); c.append(node('small',row.group,'kicker'),node('h3',row.title),node('p',row.original,'wrap'),link('Open LAC copy · '+row.date+' ↗',row.lac));
 const response=node('p',row.response.label+(row.response.code?' · HTTP '+row.response.code:''),'fine');c.append(response);
 const details=node('details'), years=Object.entries(row.years).sort(([a],[b])=>a.localeCompare(b));
 details.append(node('summary',years.length+' years with additional captures'));
 if(years.length){const ul=node('ul');for(const [year,r] of years){const li=node('li');li.append(link(r.date+' ↗',r.url));ul.append(li)}details.append(ul)}
 else details.append(node('p',row.cdx_checked?'No matching successful capture was returned for this exact URL.':'The extra archive index could not be checked.'));
 if(row.cdx_checked)details.append(node('small','Additional captures checked '+row.cdx_checked));
 c.append(details);return c;
}
function render(){
 shown=filterRecords(data.records,el('q').value,el('group').value,el('state').value);
 el('summary').textContent=shown.length+' of '+data.records.length+' historic resources.';
 el('cards').replaceChildren(...(shown.length?shown.map(card):[node('p','No resources match these filters.','empty')]));
 const u=new URL(location.href);for(const id of ['q','group','state'])u.searchParams.set(id,el(id).value);history.replaceState(null,'',u);
}
async function start(){
 data=await source();
 for(const name of [...new Set(data.records.map(r=>r.response.label))].sort())option('state',name,name);
 const p=new URLSearchParams(location.search);el('q').value=p.get('q')??'';
 for(const id of ['group','state'])if([...el(id).options].some(o=>o.value===p.get(id)))el(id).value=p.get(id);
 for(const id of ['q','group','state'])el(id).addEventListener(id==='q'?'input':'change',render);
 el('status').textContent='Catalogue checked '+data.retrieved+' · '+data.captures+' additional URL-years';
 el('csv').onclick=()=>download('archived-web-addresses.csv',['Resource','Collection','Original URL','LAC capture date','LAC replay','Current response','Additional years'],shown.map(r=>[r.title,r.group,r.original,r.date,r.lac,r.response.label,Object.keys(r.years).sort().join(' ')]));
 render();
}
start().catch(fail);
