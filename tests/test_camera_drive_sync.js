// Run with: node tests/test_camera_drive_sync.js
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const src=fs.readFileSync(path.join(__dirname,'../web/camera/drive-sync.js'),'utf8');
const memory=new Map(),uploads=[];
const clientID='1234567890-camera.apps.googleusercontent.com';
let fetchCount=0;
const env={
 module:{exports:{}},Blob,Date,JSON,Promise,Math,String,Number,Error,
 localStorage:{getItem:key=>memory.get(key)||null,setItem:(key,value)=>memory.set(key,value)},
 crypto:{randomUUID:()=> 'abc-123'},
 navigator:{onLine:true},
 window:{google:{accounts:{oauth2:{initTokenClient:opts=>({requestAccessToken:()=>opts.callback({access_token:'test-token',expires_in:3600})})}}}},
 fetch:async(url,options={})=>{
  fetchCount++;
  if(!options.method||options.method==='GET')return{ok:true,json:async()=>({files:[]})};
  if(url.includes('uploadType=multipart')){uploads.push(options.body);return{ok:true,json:async()=>({id:'uploaded-'+uploads.length})}};
  return{ok:true,json:async()=>({id:'folder-1'})};
 }
};
vm.runInNewContext(src,env);
const d=env.module.exports;
(async()=>{
 assert.equal(d.status().configured,false);
 assert.equal(d.status().enabled,false);
 assert.throws(()=>d.configure('not-a-client',true));
 d.configure(clientID,true);
 assert.equal(d.load().clientId,clientID);
 assert.equal(d.status().authorized,false);
 await d.auth();
 assert.equal(d.status().authorized,true);
 const sample={id:'CPC-abc',captured_at:'2026-11-10T12:00:00Z',cemetery:'Test Site',originalBlob:new Blob(['JPEG'],{type:'image/jpeg'}),location:{latitude:42.1,longitude:-72.1}};
 assert.ok(d.pending(sample));
 const meta=d.makeMetadata(sample);
 assert.equal(meta.originalBlob,undefined);
 assert.equal(meta.image_file,'CPC-CPC-abc-original.jpg');
 assert.equal(meta.location.latitude,42.1);
 let saves=0;
 const result=await d.sync([sample],async()=>{saves++});
 assert.equal(result.uploaded,1);
 assert.equal(result.failed,0);
 assert.equal(uploads.length,2);
 assert.equal(sample.drive_sync.status,'uploaded');
 assert.equal(sample.drive_sync.photoId,'uploaded-1');
 assert.equal(sample.drive_sync.recordId,'uploaded-2');
 assert.equal(saves,2);
 assert.equal(d.pending(sample),false);
 assert.equal((await d.sync([sample],async()=>{})).uploaded,0);
 assert.equal(uploads.length,2,'Should not duplicate completed records');
 const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
 for(const item of ['drive-sync.js','id="driveConnectBtn"','id="driveAuto"','id="driveSyncBtn"','queueDriveSync();','Drive backup']){
  assert.ok(html.includes(item),'Missing '+item);
 }
 assert.ok(html.includes('async function queueDriveSync()'));
 new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
 console.log('Drive sync mocked auth, folder, individual photo/JSON upload and no-duplicate checks passed.');
})().catch(e=>{console.error(e);process.exitCode=1;});
