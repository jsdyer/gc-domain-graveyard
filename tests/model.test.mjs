import test from 'node:test';import assert from 'node:assert/strict';import {filterRecords} from '../web/model.mjs';
test('Search matches original address and combines collection and response',()=>{
 const r={title:'National Council of Welfare',host:'www.ncw.gc.ca',original:'http://www.ncw.gc.ca/example',group:'Defunct resources',response:{label:'Check inconclusive'}};
 assert.equal(filterRecords([r],'NCW','Defunct resources','').length,1);assert.equal(filterRecords([r],'','Commission records','').length,0);
});
