import {byId, text} from './transport.js';

export function choices(doc, id) {
  for (const select of [byId('scene'), byId('compare-scene')]) {
    select.replaceChildren(...doc.scenes.map(scene => {
      const option = text('option', scene.label);
      option.value = scene.id;
      return option;
    }));
  }
  byId('scene').value = id;
  byId('compare-scene').value = doc.scenes.find(scene => scene.id !== id)?.id ?? id;
  byId('command-hint').textContent = `每行写拍号和命令，用空格分隔。${doc.commands.join('、')}`;
}
export function fill(scene) {
  byId('ticks').value = scene.ticks;
  byId('speed').value = scene.speed;
  byId('mirror').checked = scene.mirror;
  byId('inputs').value = scene.inputs.map(press => `${press.at} ${press.command}`).join('\n');
}
export function readScene(model) {
  const inputs = [];
  for (const [line, raw] of byId('inputs').value.split('\n').entries()) {
    if (!raw.trim()) continue;
    const match = raw.trim().match(/^(\d+)\s+([a-z][a-z0-9_-]{0,31})$/);
    if (!match) throw new Error(`输入轨第 ${line + 1} 行需要拍号和命令`);
    inputs.push({at: Number(match[1]), command: match[2]});
  }
  return {...model, ticks:Number(byId('ticks').value), speed:Number(byId('speed').value),
    mirror:byId('mirror').checked, inputs};
}
