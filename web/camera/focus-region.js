/* CPC field camera contextual region of interest.
   Taps are local research commands: target the tracked stone and inspect the
   tapped surface feature. Regions stay attached to the stone's normalized box.
   No semantic interpretation, autofocus API, or destructive photo edits. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCFocusRegion=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_FOCUS_REGION_V1';
const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
function fromTap(stone,tapX,tapY){
 if(!stone?.box||![tapX,tapY].every(Number.isFinite))return null;
 const b=stone.box;
 if(tapX<b.x-.02||tapX>b.x+b.w+.02||tapY<b.y-.02||tapY>b.y+b.h+.02)return null;
 const u=clamp((tapX-b.x)/b.w,0,1),v=clamp((tapY-b.y)/b.h,0,1);
 return{schema_version:VERSION,kind:'tapped_surface_region_unverified',u,v,stone_id:stone.persistent_lock_id??null,created_at:Date.now()};
}
function resolve(stone,focus){
 if(!stone?.box)return null;
 if(!focus)return{...stone.box,kind:'full_stone_region',is_detail:false};
 if(focus.stone_id!=null&&stone.persistent_lock_id!==focus.stone_id)return null;
 const b=stone.box;
 // Roughly 44% of the stone face on each axis; 17% minimum viewport extent
 // for sufficient pixels to evaluate strokes without claiming letter identity.
 const rw=Math.min(b.w,Math.max(Math.min(.17,b.w),Math.min(.55,b.w*.44))),rh=Math.min(b.h,Math.max(Math.min(.16,b.h),Math.min(.52,b.h*.38)));
 const cx=b.x+b.w*focus.u,cy=b.y+b.h*focus.v;
 const x=clamp(cx-rw/2,b.x,b.x+b.w-rw),y=clamp(cy-rh/2,b.y,b.y+b.h-rh);
 return{x,y,w:rw,h:rh,kind:'tapped_surface_region_unverified',is_detail:true};
}
return{VERSION,fromTap,resolve};
});
