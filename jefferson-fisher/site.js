const data=FIELD_NOTES,{timecode,escapeHtml:esc}=FieldNotes,wall=document.querySelector('ol.wall'),cards=[...wall.children],slot=document.querySelector('.slot');
const q=document.querySelector('#q'),spoken=document.querySelector('#spoken'),empty=document.querySelector('#empty');
const markers=data.breaks.map(b=>{let li=document.createElement('li');li.className='break';li.innerHTML=`<span>${esc(b.kind)}</span>${esc(b.label)}`;return li});
let arrangement='score';
function arrange(kind){arrangement=kind;markers.forEach(m=>m.remove());let seq=kind==='time'?[...cards].sort((a,b)=>a.dataset.seconds-b.dataset.seconds):cards;seq.forEach(li=>wall.append(li));
if(kind==='time'&&!q.value.trim())data.breaks.forEach((b,n)=>wall.insertBefore(markers[n],seq.find(li=>+li.dataset.seconds>=b.start)||null));
document.querySelectorAll('[data-order]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.order===kind))}
document.querySelectorAll('[data-order]').forEach(b=>b.onclick=()=>arrange(b.dataset.order));
new IntersectionObserver(entries=>document.body.classList.toggle('docked',!entries.at(-1).isIntersecting)).observe(slot);
let notes;
notes=FieldNotes.mount({video:data.video,lead:data.lead,items:cards.map(li=>({start:+li.dataset.seconds,hash:li.id})),breaks:data.breaks,transcript:data.transcript,playOnSelect:true,mark:i=>cards[i],
readingOrder:()=>[...wall.children].filter(li=>!li.hidden&&!li.classList.contains('break')).map(li=>cards.indexOf(li)),
onFirstPlay:()=>{arrange('time');cards[notes.active()]?.scrollIntoView({block:'center'})},
onBreak:b=>markers.forEach((m,n)=>m.classList.toggle('playing',data.breaks[n]===b)),
activate(i,cause){cards.forEach((li,n)=>li.classList.toggle('current',n===i));let li=cards[i];if(!li)return;
if(li.hidden)clearSearch();
if(cause==='load')li.scrollIntoView({block:'center'});
else if(cause==='history'||cause==='reader'&&!li.matches(':hover')||cause==='video'&&!notes.readerScrolledRecently())li.scrollIntoView({behavior:'smooth',block:'center'})}});
cards.forEach((li,i)=>li.querySelector('.poster').onclick=ev=>{ev.preventDefault();notes.go(i)});
function clearSearch(){q.value='';q.oninput()}
q.oninput=()=>{let found=notes.search(q.value,data.docs);let hits=new Set(found?found.content.map(r=>r.i):cards.keys());cards.forEach((li,i)=>li.hidden=!hits.has(i));arrange(arrangement);
spoken.hidden=!found||!found.transcript.length;empty.hidden=!found||!!found.content.length||!!found.transcript.length;spoken.innerHTML='';if(!found||!found.transcript.length)return;
spoken.append('Spoken in the video');spoken.append(document.createElement('br'));
found.transcript.forEach(h=>{let b=document.createElement('button');b.textContent=h.moments===1?timecode(h.start):`${timecode(h.start)} · ${h.moments}×`;b.onclick=()=>notes.go(Math.max(0,h.item),'reader',h.start);spoken.append(b)})};
q.onkeydown=e=>{if(e.key==='Escape')clearSearch()};
