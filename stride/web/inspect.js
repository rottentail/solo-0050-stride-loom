import {byId, text} from './transport.js';

const gateStates = {blocked:'未满足', deferred:'顺位在后', chosen:'采用'};
const missing = {command:'缺命令', age:'停留未足', mark:'事件未到'};
function fact(label, value) {
  const row = text('p', '', 'fact'); row.append(text('span', label), text('b', value)); return row;
}
function chips(id, values, type = '') {
  byId(id).replaceChildren(...(values.length ? values.map(value => text('span', value, `chip ${type}`)) : [text('p', '本拍无记录')]));
}
export function inspect(row, names) {
  const title = names.get(row.clip) ?? row.clip;
  byId('pose-tag').textContent = `${title} · 源帧 ${row.frame}`;
  byId('world').textContent = `根位置 ${row.world}（${row.delta >= 0 ? '+' : ''}${row.delta}）`;
  byId('facts').replaceChildren(fact('来源动作', title), fact('穿越源帧', row.crossed.join('、') || '尾端停留'),
    fact('动作内拍数', row.age), fact('下一动作', names.get(row.target) ?? '保持'));
  chips('marks', row.events.map(event => `${event.at} · ${event.tag}`), 'event');
  chips('pending', row.pending.map(press => `#${press.id} ${press.command}`));
  byId('gates').replaceChildren(...(row.gates.length ? row.gates.map(gate => {
    const line = text('div', `${gateStates[gate.verdict]} · ${gate.id}`, `gate ${gate.verdict}`);
    if (gate.missing.length) line.append(text('small', gate.missing.map(item => missing[item]).join('、')));
    return line;
  }) : [text('p', '来源动作无候选')])) ;
}
