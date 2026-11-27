import {byId, text} from './transport.js';

const clock = tick => String(tick).padStart(2, '0');
export function createTimeline(paint) {
  let rows = [], tick = 0, timer;
  function seek(value, scroll = false) {
    if (!rows.length) return;
    tick = Math.min(rows.length-1, Math.max(0, value));
    const container = byId('beats');
    container.querySelector('[aria-current]')?.removeAttribute('aria-current');
    const selected = container.children[tick];
    selected.setAttribute('aria-current', 'step');
    if (scroll) {
      const left = selected.offsetLeft - container.offsetLeft;
      if (left < container.scrollLeft || left + selected.offsetWidth > container.scrollLeft + container.clientWidth) {
        container.scrollLeft = left - container.clientWidth / 3;
      }
    }
    byId('playhead').value = tick;
    byId('beat').textContent = `${clock(tick)} / ${clock(rows.length - 1)}`;
    paint(rows, tick);
  }
  function pause() {
    clearInterval(timer);
    timer = undefined;
    byId('play').textContent = '播放';
    byId('play').setAttribute('aria-label', '播放');
  }
  byId('play').onclick = () => {
    if (timer) { pause(); return; }
    if (!rows.length) return;
    if (tick === rows.length - 1) seek(0, true);
    byId('play').textContent = '暂停';
    byId('play').setAttribute('aria-label', '暂停');
    timer = setInterval(() => {
      if (tick >= rows.length-1) pause();
      else seek(tick+1,true);
    }, 150);
  };
  byId('prev').onclick = () => { pause(); seek(tick-1,true); };
  byId('next').onclick = () => { pause(); seek(tick+1,true); };
  byId('playhead').oninput = event => { pause(); seek(Number(event.currentTarget.value), true); };
  return {pause, position: () => tick, show(trace, names, initial = 0) {
    pause(); rows = trace.rows;
    byId('playhead').max = rows.length-1;
    byId('beats').replaceChildren(...rows.map(row => {
      const node = text('button', clock(row.tick), 'beat-cell');
      node.append(text('span', names.get(row.clip) ?? row.clip));
      if (row.events.length) node.dataset.event = '';
      if (row.edge) node.dataset.edge = '';
      node.onclick = () => { pause(); seek(row.tick); };
      return node;
    }));
    seek(initial,true);
  }};
}
