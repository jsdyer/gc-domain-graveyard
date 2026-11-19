export function filterRecords(records,query,group,state){
  const q=query.trim().toLowerCase();
  return records.filter(r=>(!group||r.group===group)&&(!state||r.response.label===state)&&[r.title,r.host,r.original].some(x=>x.toLowerCase().includes(q)));
}
