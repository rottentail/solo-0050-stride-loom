import {byId} from './transport.js';

export function makeViewport() {
  const canvas = byId('picture');
  const ctx = canvas.getContext('2d');
  let data = null;
  function draw() {
    const {width, height} = canvas.getBoundingClientRect();
    if (width <= 0 || height <= 0) return;
    const dpi = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * dpi);
    canvas.height = Math.round(height * dpi);
    ctx.setTransform(dpi, 0, 0, dpi, 0, 0);
    const horizon = height * .76;
    ctx.fillStyle = '#101a1f';
    ctx.fillRect(0, 0, width, height);
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#263941';
    ctx.beginPath();
    for (let x = 20; x < width; x += 28) { ctx.moveTo(x, 10); ctx.lineTo(x, height - 14); }
    for (let y = horizon % 28; y < height; y += 28) { ctx.moveTo(14, y); ctx.lineTo(width-14, y); }
    ctx.stroke();
    ctx.strokeStyle = '#42545b';
    ctx.beginPath(); ctx.moveTo(14, horizon); ctx.lineTo(width-14, horizon); ctx.stroke();
    if (!data) return;
    const {rows, tick} = data;
    const row = rows[tick];
    const root = rows.map(item => item.world).concat(0);
    const min = Math.min(...root), max = Math.max(...root);
    const xs = world => width * .5 + (world - (max+min)/2) * Math.min(1.45, width*.52/Math.max(1, max-min));
    const unit = Math.min(2.25, width / 155, height / 145);
    const origin = {x:xs(row.world), y:horizon - unit * 55};
    ctx.strokeStyle = '#f4bd78'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(xs(0), horizon);
    for (const item of rows.slice(0,tick+1)) ctx.lineTo(xs(item.world), horizon);
    ctx.stroke();
    ctx.fillStyle = '#ffd396'; ctx.beginPath(); ctx.arc(origin.x, horizon, 3.5, 0, Math.PI*2); ctx.fill();
    const points = new Map(row.pose.map(j => [j.id, [origin.x+j.x*unit/1000, origin.y+j.y*unit/1000]]));
    ctx.setLineDash([4,5]); ctx.strokeStyle = '#7c9b96'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(origin.x, horizon); ctx.lineTo(origin.x, origin.y); ctx.stroke(); ctx.setLineDash([]);
    ctx.lineCap = 'round';
    for (const joint of row.pose) {
      if (!joint.parent) continue;
      ctx.strokeStyle = '#2a5951'; ctx.lineWidth = 11;
      ctx.beginPath(); ctx.moveTo(...points.get(joint.parent)); ctx.lineTo(...points.get(joint.id)); ctx.stroke();
      ctx.strokeStyle = '#a4eed2'; ctx.lineWidth = 2.4; ctx.stroke();
    }
    for (const [id, [x,y]] of points) {
      ctx.fillStyle = id === 'head' ? '#fce0ad' : '#d0f7e9';
      ctx.beginPath(); ctx.arc(x, y, id === 'head' ? 10*unit/1.8 : 3.1, 0, Math.PI*2); ctx.fill();
    }
  }
  new ResizeObserver(draw).observe(canvas);
  return (rows, tick) => { data = rows?.length ? {rows, tick} : null; draw(); };
}
