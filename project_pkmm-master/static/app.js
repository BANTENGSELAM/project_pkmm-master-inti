const $ = id => document.getElementById(id);
const map = L.map('map',{minZoom:4,maxZoom:17}).setView([-2.4,118],5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',maxZoom:19}).addTo(map);
const hotspots=L.layerGroup().addTo(map), selected=L.layerGroup().addTo(map);
let boundaryLayer=null;
let records=[];
const escapeHTML=v=>String(v??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeNum=(v,d=0)=>Number.isFinite(Number(v))?Number(v).toFixed(d):'—';
async function api(url,options){const r=await fetch(url,options);const data=await r.json();if(!r.ok)throw Error(data.error||'Layanan tidak tersedia.');return data;}

function formatAnalysisError(msg){
  let title='Analisis Belum Berhasil';
  let cause=msg||'Tidak ada pesan kesalahan spesifik.';
  let suggestion='Periksa koordinat titik atau coba kembali beberapa saat lagi.';
  if(msg.includes('awan scene <40%')||msg.includes('awan')||msg.includes('piksel layak')||msg.includes('SCL')){
    title='Citra Sentinel-2 Bebas Awan Tidak Ditemukan';
    suggestion='Coba memperluas rentang tanggal analisis atau memilih lokasi lain yang memiliki tutupan awan lebih rendah.';
  } else if(msg.includes('wilayah Indonesia')||msg.includes('daratan')){
    title='Lokasi di Luar Daratan Indonesia';
    suggestion='Pastikan titik koordinat berada di dalam batas daratan kepulauan Indonesia (bukan di laut atau perairan terbuka).';
  } else if(msg.includes('Rentang tanggal')){
    title='Parameter Rentang Tanggal Tidak Sesuai';
    suggestion='Tentukan rentang tanggal antara 0 hingga maksimal 90 hari, dan tidak boleh melewati tanggal hari ini.';
  } else if(msg.includes('batas waktu')||msg.includes('timeout')){
    title='Layanan Citra Melewati Batas Waktu';
    suggestion='Koneksi ke katalog AWS STAC / Copernicus mengalami jeda waktu. Silakan coba kembali dalam beberapa saat.';
  }
  return `<div class="error-box"><strong class="error-title">${escapeHTML(title)}</strong><p class="error-cause">${escapeHTML(cause)}</p><p class="error-suggestion"><strong>Saran tindakan:</strong> ${escapeHTML(suggestion)}</p></div>`;
}

function switchTab(tabId){
  const isGrid=tabId==='grid';
  const btnGrid=$('tabBtnGrid'), btnManual=$('tabBtnManual');
  const paneGrid=$('tabPaneGrid'), paneManual=$('tabPaneManual');
  if(btnGrid)btnGrid.classList.toggle('active',isGrid);
  if(btnManual)btnManual.classList.toggle('active',!isGrid);
  if(paneGrid)paneGrid.classList.toggle('active',isGrid);
  if(paneManual)paneManual.classList.toggle('active',!isGrid);
  if(btnGrid&&typeof btnGrid.setAttribute==='function')btnGrid.setAttribute('aria-selected',isGrid?'true':'false');
  if(btnManual&&typeof btnManual.setAttribute==='function')btnManual.setAttribute('aria-selected',isGrid?'false':'true');
}

function mark(lat,lon){
  selected.clearLayers();
  L.circleMarker([lat,lon],{radius:8,color:'#fff',weight:3,fillColor:'#147c76',fillOpacity:1}).addTo(selected);
  $('lat').value=lat.toFixed(5);
  $('lon').value=lon.toFixed(5);
  switchTab('manual');
  const manualDetails=document.querySelector('.manual-analysis');
  if(manualDetails)manualDetails.open=true;
}

map.on('click',e=>{if(pickingArea)pickCorner(e.latlng);else mark(e.latlng.lat,e.latlng.lng);});
$('reset').onclick=()=>map.fitBounds([[-11.2,94.5],[6.2,141.5]]);
function filtered(){return records.filter(p=>!$('highOnly').checked||p.confidence==='h');}
function render(){
  hotspots.clearLayers();
  const data=filtered();
  for(const p of data){
    const color=p.confidence==='h'?'#c23920':'#d96328';
    L.circleMarker([p.lat,p.lon],{radius:p.confidence==='h'?6:4,weight:1,color:'#fff',fillColor:color,fillOpacity:.85}).bindPopup(`<b>Anomali termal VIIRS</b><br>${p.lat.toFixed(4)}, ${p.lon.toFixed(4)}<br>${escapeHTML(p.date)} ${escapeHTML(p.time)} UTC<br>Keyakinan: ${escapeHTML(p.confidence)} · FRP ${safeNum(p.frp,1)} MW<br><small>Belum merupakan konfirmasi kebakaran.</small>`).addTo(hotspots);
  }
  $('count').textContent=data.length.toLocaleString('id-ID');
  $('high').textContent=data.filter(p=>p.confidence==='h').length.toLocaleString('id-ID');
  $('frp').textContent=data.length?Math.max(...data.map(p=>p.frp)).toFixed(1):'0.0';
  $('download').disabled=!data.length;
  const latest=[...data].sort((a,b)=>(b.date+b.time).localeCompare(a.date+a.time));
  const LIMIT=300;
  $('rows').innerHTML=latest.slice(0,LIMIT).map(p=>`<tr><td class="coord-cell">${safeNum(p.lat,4)}, ${safeNum(p.lon,4)}</td><td class="time-cell">${escapeHTML(p.date)} ${escapeHTML(p.time.slice(0,2)+':'+p.time.slice(2))}</td><td><span class="badge ${p.confidence==='h'?'high':'nominal'}">${escapeHTML(({h:'Tinggi',n:'Nominal',l:'Rendah'})[p.confidence]||p.confidence)}</span></td><td class="frp-cell">${safeNum(p.frp,1)} MW</td><td>${escapeHTML(p.satellite)}</td></tr>`).join('')||'<tr><td colspan="5" class="empty-cell">Tidak ada deteksi pada filter yang dipilih. Kondisi ini tidak menjamin nihilnya kebakaran di lapangan.</td></tr>';
  const notice=$('tableNotice');
  if(!data.length){notice.textContent='';notice.className='fine table-notice';}
  else if(data.length>LIMIT){notice.textContent=`Menampilkan ${LIMIT} dari ${data.length} titik terdeteksi. Unduh CSV untuk data lengkap.`;notice.className='fine table-notice highlight';}
  else{notice.textContent=`Menampilkan seluruh ${data.length} titik terdeteksi.`;notice.className='fine table-notice';}
}

async function refresh(){
  const button=$('refresh');button.disabled=true;
  $('feedStatus').textContent='Mengambil deteksi NASA FIRMS…';
  try{
    const d=await api('/api/hotspots?days='+$('days').value);
    records=d.points;render();
    if(d.points.length===0){
      $('period').textContent=`VIIRS S-NPP · 0 anomali (${d.days} hari)`;
    } else {
      $('period').textContent=`VIIRS S-NPP · ${d.days} hari akuisisi`;
    }
    $('feedStatus').textContent=`Diperbarui ${new Date(d.retrieved_at).toLocaleString('id-ID')} · ${d.source} · cache 5 menit`;
    $('feedStatus').className='';
  }catch(e){
    $('feedStatus').textContent=e.message+' Data sebelumnya, bila ada, tetap ditampilkan.';
    $('feedStatus').className='status-error';
  }finally{button.disabled=false;}
}
$('refresh').onclick=refresh;
$('days').onchange=refresh;
$('highOnly').onchange=render;

$('download').onclick=()=>{
  const rows=[['latitude','longitude','date_utc','time_utc','confidence','frp_mw','satellite'],...filtered().map(p=>[p.lat,p.lon,p.date,p.time,p.confidence,p.frp,p.satellite])];
  const blob=new Blob([rows.map(r=>r.map(v=>'"'+String(v??'').replace(/"/g,'""')+'"').join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='firms_indonesia.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};

const today=new Date(),month=new Date(today);
month.setUTCDate(month.getUTCDate()-30);
$('end').value=today.toISOString().slice(0,10);
$('start').value=month.toISOString().slice(0,10);
$('start').max=$('end').max=$('end').value;

$('prediction').onsubmit=async e=>{
  e.preventDefault();
  const button=$('analyze');button.disabled=true;
  $('result').className='result';
  $('result').textContent='Mencari citra, memeriksa awan, membaca kanal Sentinel-2, lalu menjalankan model…';
  try{
    const d=await api('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lat:Number($('lat').value),lon:Number($('lon').value),start:$('start').value,end:$('end').value})});
    mark(d.lat,d.lon);
    const probabilities=d.probabilities?d.classes.map((c,i)=>`Kelas ${escapeHTML(c)}: ${(d.probabilities[i]*100).toFixed(1)}%`).join(' · '):'Tidak tersedia';
    $('result').innerHTML=`<span class="eyebrow">HASIL XGBOOST</span><strong>${d.label==='1'?'Berpotensi terbakar':'Aman menurut model'}</strong><p>${probabilities}</p><dl><dt>Citra analisis</dt><dd>${escapeHTML(d.scene.datetime)}<br>${escapeHTML(d.scene.id)}</dd>${d.baseline?`<dt>Citra pembanding dNBR</dt><dd>${escapeHTML(d.baseline.datetime)}</dd>`:''}<dt>Fitur masukan</dt><dd>${Object.entries(d.features).map(([k,v])=>`${escapeHTML(k)}: ${safeNum(v,4)}`).join(' · ')}</dd></dl><p class="fine">${escapeHTML(d.warning)}</p>`;
  }catch(err){
    $('result').className='result error';
    $('result').innerHTML=formatAnalysisError(err.message);
  }finally{button.disabled=false;}
};

async function init(){
  try{
    const d=await api('/api/status');
    $('modelStatus').textContent=`Model lokal siap · ${d.features.length} fitur`;
    $('modelDot').style.color='#1e6d49';
    if(d.firms_configured)refresh();
    else {
      $('feedStatus').textContent='MAP_KEY belum dikonfigurasi. Buka PETUNJUK.md → isi .env → restart server. Tidak ada data simulasi yang ditampilkan.';
      $('period').textContent='MAP_KEY belum diisi';
    }
  }catch(e){$('modelStatus').textContent=e.message;}
  try{
    boundaryLayer=L.geoJSON(await api('/api/boundary'),{style:{color:'#507b64',weight:1,fillOpacity:.015},interactive:false}).addTo(map);
  }catch(e){$('feedStatus').textContent+=' Batas wilayah belum dapat dimuat.';}
}

$('clock').textContent=new Date().toLocaleDateString('id-ID',{day:'numeric',month:'long',year:'numeric'});
init();
setInterval(()=>{if(!document.hidden)api('/api/status').then(s=>s.firms_configured&&refresh()).catch(()=>{});},300000);

const gridLayer=L.layerGroup().addTo(map), areaLayer=L.layerGroup().addTo(map), draftLayer=L.layerGroup().addTo(map);
let pickingArea=false, firstCorner=null, draftBox=null, monitorState=null, monitorLoading=false, prioritiesLoading=false, lastMonitorSignature='', monitorInitialized=false;
const localTime=v=>v?new Date(v).toLocaleString('id-ID',{dateStyle:'medium',timeStyle:'short'}):'—';

function chooseArea(){
  pickingArea=!pickingArea;firstCorner=null;draftBox=null;$('saveArea').disabled=true;draftLayer.clearLayers();
  $('pickArea').classList.toggle('selecting',pickingArea);
  $('map').classList.toggle('map-selecting',pickingArea);
  $('pickArea').textContent=pickingArea?'Batal memilih area':'▧ Pilih area di peta (2 sudut)';
  $('areaHint').textContent=pickingArea?'Klik sudut pertama pada peta, lalu sudut seberangnya.':'Pemilihan dibatalkan. Area tersimpan tetap dipantau.';
}

function pickCorner(location){
  if(!firstCorner){
    firstCorner=location;
    L.circleMarker(location,{radius:5,color:'#147c76'}).addTo(draftLayer);
    $('areaHint').textContent='Sudut pertama dipilih. Klik sudut seberangnya (maksimal 2 derajat).';
    return;
  }
  const bounds=L.latLngBounds(firstCorner,location);
  draftBox=[bounds.getWest(),bounds.getSouth(),bounds.getEast(),bounds.getNorth()];
  draftLayer.clearLayers();
  L.rectangle(bounds,{color:'#147c76',weight:2,dashArray:'6 4',fillOpacity:.08,interactive:false}).addTo(draftLayer);
  pickingArea=false;firstCorner=null;
  $('pickArea').classList.remove('selecting');
  $('map').classList.remove('map-selecting');
  $('pickArea').textContent='▧ Pilih ulang area (2 sudut)';
  $('areaHint').textContent=`Area pilihan: ${draftBox.map(v=>v.toFixed(3)).join(', ')}. Klik simpan untuk mengganti grid.`;
  $('saveArea').disabled=Boolean(monitorState?.busy);
}
$('pickArea').onclick=chooseArea;

async function monitorAction(action){
  try{
    const data=await api('/api/monitor',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(action==='configure'?{action,bbox:draftBox,interval_minutes:Number($('interval').value)}:{action})});
    if(action==='configure'){draftBox=null;draftLayer.clearLayers();$('areaHint').textContent='Area disimpan. Titik daratan akan dianalisis bergiliran.';}
    renderMonitor(data);
    await loadPriorities();
  }catch(e){
    $('monitorStatus').className='monitor-status status-error';
    $('monitorStatus').textContent=e.message;
  }
}
$('saveArea').onclick=()=>monitorAction('configure');
$('runNow').onclick=()=>monitorAction('run');
$('pauseMonitor').onclick=()=>monitorAction(monitorState?.enabled?'pause':'start');

function renderMonitor(state){
  monitorState=state;
  if(!monitorInitialized){$('interval').value=String(state.interval_minutes);monitorInitialized=true;}
  $('saveArea').disabled=!draftBox||state.busy;
  $('runNow').disabled=state.busy||!state.points.length;
  $('pauseMonitor').disabled=!state.points.length;
  $('pauseMonitor').textContent=state.enabled?'Jeda':'Lanjutkan';
  const completed=state.points.filter(p=>p.checked_at).length;
  const failed=state.points.filter(p=>p.status==='error').length;
  const okCount=state.points.filter(p=>p.status==='ok').length;
  const pendingCount=state.points.filter(p=>p.status==='pending'||p.status==='running').length;
  const currentEscaped=escapeHTML(state.current||'…');
  const headline=state.busy?`Menganalisis grid ${currentEscaped} · satu per satu`:state.enabled?'Pemantauan otomatis aktif':'Pemantauan dijeda';
  $('monitorStatus').className='monitor-status';
  $('monitorStatus').innerHTML=`<b>${headline}</b>${safeNum(completed,0)}/${safeNum(state.points.length,0)} titik pernah diperiksa · ${safeNum(failed,0)} gagal saat pemeriksaan terakhir<br>Maksimal ${safeNum(state.batch_size,0)} titik per ${safeNum(state.interval_minutes,0)} menit<br>Terakhir: ${localTime(state.last_run)}<br>Berikutnya: ${state.busy?'setelah siklus selesai':state.next_run?localTime(state.next_run):state.enabled?'segera':'—'}`;
  
  if(!state.points.length){
    $('gridSummary').textContent='Belum ada grid';
  } else {
    $('gridSummary').textContent=`${state.points.length} sampel · ${okCount} sukses · ${failed} gagal · ${pendingCount} menunggu`;
  }

  areaLayer.clearLayers();gridLayer.clearLayers();
  if(state.bbox){const [w,s,e,n]=state.bbox;L.rectangle([[s,w],[n,e]],{color:'#587455',weight:1,fillOpacity:.03,interactive:false}).addTo(areaLayer);}
  $('gridRows').innerHTML=state.points.map(p=>{
    const d=p.result,ok=p.status==='ok',isPotential=ok&&d?.label==='1',age=d?(Date.now()-new Date(d.scene?.datetime))/86400000:null;
    let label=({pending:'Menunggu giliran',running:'Menganalisis…',error:'Belum dapat dianalisis'})[p.status]||(isPotential?'Berpotensi terbakar':'Aman menurut model');
    if(ok&&age>14)label+=' · citra lama';
    const score=ok&&d?.probabilities?(d.probabilities[d.classes.indexOf('1')]*100).toFixed(1)+'%':'—';
    const color=p.status==='error'?'#9c9c8a':isPotential?'#b26a15':ok?'#1e6d49':'#6b9b96';
    L.circleMarker([p.lat,p.lon],{radius:7,color:'#fff',weight:2,fillColor:color,fillOpacity:.9}).bindPopup(`<b>Grid ${escapeHTML(p.id)}</b><br>${escapeHTML(label)}<br>Skor kelas 1: ${score}<br>Citra: ${d?localTime(d.scene?.datetime):'—'}<br>${escapeHTML(p.error||'')}`).addTo(gridLayer);
    
    let badgeClass = ok ? (isPotential ? 'potential' : 'safe') : p.status;
    let errorDetail = '';
    if(p.error){
      const isCloud = p.error.includes('awan') || p.error.includes('piksel') || p.error.includes('SCL');
      const isService = p.error.includes('layanan') || p.error.includes('timeout') || p.error.includes('koneksi');
      const errorCategory = isCloud ? 'Kualitas Citra' : isService ? 'Gangguan Layanan' : 'Kendala Analisis';
      errorDetail = `<div class="grid-error-msg"><span class="grid-error-tag">${errorCategory}:</span> ${escapeHTML(p.error)}</div>`;
    }
    return `<tr><td><b>${escapeHTML(p.id)}</b></td><td class="coord-cell">${safeNum(p.lat,4)}, ${safeNum(p.lon,4)}</td><td class="${p.error?'error-cell':''}"><span class="grid-badge ${badgeClass}">${escapeHTML(label)}</span>${errorDetail}</td><td class="score-cell">${score}</td><td class="time-cell">${ok?localTime(d.scene?.datetime):'—'}</td><td class="time-cell">${localTime(p.checked_at)}</td></tr>`;
  }).join('')||'<tr><td colspan="6" class="empty-cell">Pilih area untuk membentuk grid sampel daratan Indonesia.</td></tr>';
}

async function loadMonitor(){
  if(monitorLoading)return;
  monitorLoading=true;
  try{
    const state=await api('/api/monitor'),signature=JSON.stringify(state);
    renderMonitor(state);
    if(signature!==lastMonitorSignature){
      lastMonitorSignature=signature;
      if(!document.hidden)loadPriorities();
    }
  }catch(e){
    $('monitorStatus').className='monitor-status status-error';
    $('monitorStatus').textContent='Pemantauan belum tersedia: '+e.message+' Restart server untuk memuat versi terbaru.';
  }finally{monitorLoading=false;}
}

function priorityItem(p,i){
  const details=p.tier===1?`Keyakinan ${escapeHTML(({h:'tinggi',n:'nominal',l:'rendah'})[p.confidence]||p.confidence)} · FRP ${safeNum(p.frp,1)} MW`:`Skor kelas 1 ${(p.score*100).toFixed(1)}% · kelas 1`;
  return `<div class="priority-item"><span class="rank">${i+1}</span><div class="item-body"><b>${safeNum(p.lat,4)}, ${safeNum(p.lon,4)}</b><small>${details}</small><small>${localTime(p.observed_at)}</small></div><button class="quiet locate-priority" data-lat="${p.lat}" data-lon="${p.lon}" aria-label="Lihat lokasi di peta">↗ Peta</button></div>`;
}

async function loadPriorities(){
  if(prioritiesLoading)return;
  prioritiesLoading=true;
  const priorityNote=$('priorityNote');
  try{
    const data=await api('/api/priorities');
    if(!Array.isArray(data.rows))throw Error('Respons prioritas tidak valid.');
    const active=data.rows.filter(p=>p.tier===1),potential=data.rows.filter(p=>p.tier===2),historical=data.historical_potential||[];
    $('activeTotal').textContent=active.length.toLocaleString('id-ID');
    $('potentialTotal').textContent=historical.length?`${potential.length} terbaru / ${historical.length} lama`:potential.length;
    
    $('activeList').innerHTML=active.slice(0,50).map(priorityItem).join('')||'<div class="empty-priority"><p class="empty-title">Tidak ada indikasi termal aktif (24 jam)</p><p class="fine">Tidak ditemukan anomali panas inframerah satelit VIIRS dalam 24 jam terakhir pada data yang tersedia.</p></div>';
    
    $('potentialList').innerHTML=potential.map(priorityItem).join('')||'<div class="empty-priority"><p class="empty-title">Tidak ada titik potensi kelas 1 aktif (≤14 hari)</p><p class="fine">Belum ada titik grid terdeteksi rawan terbakar dengan citra berumur ≤14 hari. Kondisi ini bukan jaminan seluruh area aman.</p></div>';
    
    if(historical.length){
      $('potentialList').innerHTML+=`<div class="history-heading"><b>${historical.length} hasil kelas 1 · citra lama</b><p>Hasil model tetap tersedia, tetapi citra berumur lebih dari 14 hari. Perlu analisis ulang; belum masuk prioritas terbaru.</p></div>`+historical.map(priorityItem).join('');
    }
    priorityNote.className='priority-note';
    priorityNote.textContent=(data.warning?data.warning+' ':'')+data.note+` Menampilkan maksimal 50 deteksi aktif teratas. FIRMS diperiksa: ${localTime(data.firms_updated_at)}.`;
  }catch(e){
    priorityNote.className='priority-note status-error';
    priorityNote.textContent='Prioritas belum dapat diperbarui: '+e.message;
  }finally{prioritiesLoading=false;}
}
$('priorityRefresh').onclick=loadPriorities;

document.querySelector('.priorities').addEventListener('click',e=>{
  const button=e.target.closest('.locate-priority');
  if(button){
    map.setView([Number(button.dataset.lat),Number(button.dataset.lon)],12);
    $('map').scrollIntoView({behavior:'smooth',block:'center'});
  }
});

if($('tabBtnGrid'))$('tabBtnGrid').onclick=()=>switchTab('grid');
if($('tabBtnManual'))$('tabBtnManual').onclick=()=>switchTab('manual');

if($('toggleHotspots'))$('toggleHotspots').onchange=e=>{
  if(e.target.checked)map.addLayer?.(hotspots);
  else map.removeLayer?.(hotspots);
};
if($('toggleGrid'))$('toggleGrid').onchange=e=>{
  if(e.target.checked){map.addLayer?.(gridLayer);map.addLayer?.(areaLayer);}
  else {map.removeLayer?.(gridLayer);map.removeLayer?.(areaLayer);}
};
if($('toggleBoundary'))$('toggleBoundary').onchange=e=>{
  if(boundaryLayer){
    if(e.target.checked)map.addLayer?.(boundaryLayer);
    else map.removeLayer?.(boundaryLayer);
  }
};

document.addEventListener('visibilitychange',()=>{if(!document.hidden){loadMonitor();loadPriorities();}});
loadMonitor();
setInterval(()=>{if(!document.hidden)loadMonitor();},10000);
setInterval(()=>{if(!document.hidden)loadPriorities();},60000);
