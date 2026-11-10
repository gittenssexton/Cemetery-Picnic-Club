/* CPC direct Drive sync: per-capture JPEG + JSON; no ZIP required.
   Google Identity Services authorization is explicit, tokens exist only in memory.
   Auto uploads run only while the web app is open and connected.
*/
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCDriveSync=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const CONFIG_KEY='cpc-drive-sync-config-v1';
const SCOPE='https://www.googleapis.com/auth/drive.file';
const API='https://www.googleapis.com/drive/v3/files';
const UPLOAD='https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,webViewLink';
const FOLDER_NAME='Cemetery Picnic Club - Camera Uploads';
let token=null,expires=0,client=null,folderId=null,busy=false,config={clientId:'',enabled:false};
function load(){try{const data=JSON.parse(localStorage.getItem(CONFIG_KEY)||'{}');config={clientId:typeof data.clientId==='string'?data.clientId:'',enabled:data.enabled===true};folderId=typeof data.folderId==='string'?data.folderId:null;}catch(e){config={clientId:'',enabled:false};folderId=null}return status();}
function save(){localStorage.setItem(CONFIG_KEY,JSON.stringify({...config,folderId}));return status();}
function configure(clientId,enabled){const id=String(clientId||'').trim();if(!/^[0-9]+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com$/.test(id))throw Error('Enter a valid Google OAuth web client ID.');if(config.clientId!==id){token=null;expires=0;client=null;folderId=null;}config.clientId=id;config.enabled=!!enabled;return save();}
function enabled(value){config.enabled=!!value;return save();}
function status(){return{enabled:config.enabled,clientId:config.clientId,configured:!!config.clientId,authorized:!!token&&Date.now()<expires,folderId,uploading:busy,folderName:FOLDER_NAME};}
function auth(){if(!config.clientId)throw Error('Enter your Google OAuth client ID first.');if(!window.google?.accounts?.oauth2)throw Error('Google sign-in library unavailable; check connectivity.');return new Promise((resolve,reject)=>{
 try{client=window.google.accounts.oauth2.initTokenClient({client_id:config.clientId,scope:SCOPE,callback:(response)=>{
 if(response.error){reject(new Error(response.error));return}
 token=response.access_token;expires=Date.now()+Math.max(30,Number(response.expires_in||3300)-120)*1000;resolve(status());
 },error_callback:e=>reject(new Error(e?.message||'Google authorization cancelled'))});
 client.requestAccessToken({prompt:token?'':'consent'});
 }catch(e){reject(e)}
});}
function makeMetadata(record){const {originalBlob,drive_sync,...rest}=record;const prefix='CPC-'+String(record.id||'unknown').replace(/[^A-Za-z0-9-]/g,'');return {...rest,archive_format:'CPC_CAMERA_RECORD_JSON_V1',image_file:prefix+'-original.jpg',photo_drive_file_id:drive_sync?.photoId||null,private_research_record:true};}
function pending(record){return !!record&&record.originalBlob instanceof Blob&&(!record.drive_sync||record.drive_sync.status!=='uploaded');}
async function fetchGoogle(url,options={}){if(!token||Date.now()>=expires)throw Error('Google authorization expired. Connect Drive again.');
 const response=await fetch(url,{...options,headers:{...(options.headers||{}),Authorization:'Bearer '+token}});
 const data=await response.json().catch(()=>({}));
 if(!response.ok)throw Error('Google Drive '+response.status+': '+(data.error?.message||'Upload failed'));
 return data;
}
async function getFolder(){
 if(folderId)return folderId;
 // Restrict sync to a new app-created folder, so drive.file permissions suffice.
 const d=await fetchGoogle(API+'?fields=files(id,name,mimeType),nextPageToken&pageSize=100&q='+encodeURIComponent("mimeType='application/vnd.google-apps.folder' and name='"+FOLDER_NAME+"' and trashed=false"));
 if(d.files?.length)folderId=d.files[0].id;
 else {const f=await fetchGoogle(API+'?fields=id,name',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:FOLDER_NAME,mimeType:'application/vnd.google-apps.folder'})});folderId=f.id;}
 save();return folderId;
}
async function upload(name,mime,blob,parent){
 // Drive multipart upload: metadata and file bytes in one request.
 const boundary='cpc_'+crypto.randomUUID().replaceAll('-','');
 const head='--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify({name,mimeType:mime,parents:[parent]})+'\r\n--'+boundary+'\r\nContent-Type: '+mime+'\r\n\r\n';
 const body=new Blob([head,blob,'\r\n--'+boundary+'--\r\n'],{type:'multipart/related; boundary='+boundary});
 return await fetchGoogle(UPLOAD,{method:'POST',headers:{'Content-Type':'multipart/related; boundary='+boundary},body});
}
async function uploadRecord(record,saveRecord){
 if(!pending(record))return record;
 const parent=await getFolder(),prefix='CPC-'+String(record.id||crypto.randomUUID()).replace(/[^A-Za-z0-9-]/g,'');
 record.drive_sync=record.drive_sync||{status:'pending'};
 try{
   if(!record.drive_sync.photoId){
     const f=await upload(prefix+'-original.jpg','image/jpeg',record.originalBlob,parent);
     record.drive_sync.photoId=f.id;record.drive_sync.status='partial';
     await saveRecord(record);
   }
   if(!record.drive_sync.recordId){
     const b=new Blob([JSON.stringify(makeMetadata(record),null,2)],{type:'application/json'});
     const f=await upload(prefix+'-record.json','application/json',b,parent);
     record.drive_sync.recordId=f.id;
   }
   record.drive_sync.status='uploaded';record.drive_sync.uploaded_at=new Date().toISOString();record.drive_sync.last_error=null;
   await saveRecord(record);
 }catch(e){
   record.drive_sync.status=record.drive_sync.photoId?'partial':'pending';record.drive_sync.last_error=String(e.message||e).slice(0,220);
   await saveRecord(record);throw e;
 }
 return record;
}
async function sync(records,saveRecord,progress){
 if(busy||!config.enabled||!token||Date.now()>=expires||typeof navigator!=='undefined'&&!navigator.onLine)return{uploaded:0,skipped:true};
 busy=true;let uploaded=0,failed=0;try{
 for(const r of records){
  if(!pending(r))continue;
  try{await uploadRecord(r,saveRecord);uploaded++;progress?.({uploaded,failed,id:r.id,status:'uploaded'})}
  catch(e){failed++;progress?.({uploaded,failed,id:r.id,status:'failed',error:e.message});if(/authorization expired|401|403/.test(e.message))break;}
 }
 return{uploaded,failed};
 }finally{busy=false}
}
load();
return {SCOPE,FOLDER_NAME,load,configure,enabled,status,auth,pending,makeMetadata,uploadRecord,sync};
});
