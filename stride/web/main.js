import {byId, request} from './transport.js';
import {choices, fill, readScene} from './scene-form.js';
import {makeViewport} from './canvas-view.js';
import {inspect} from './inspect.js';
import {createTimeline} from './timeline.js';
import {delivery} from './handoff-panel.js';

const state = {head:null, revision:null, doc:null, scene:null, page:'stage'};
const nav = [...document.querySelectorAll('[data-page]')];
const viewport = makeViewport();
let labels = new Map();
let comparison = null, comparisonSide = false;
const timeline = createTimeline((rows, tick) => { viewport(rows, tick); inspect(rows[tick], labels); });
let busy = false;
function notify(copy, failure = false) {
  const notice = byId('notice');
  notice.textContent = copy; notice.hidden = false; notice.toggleAttribute('data-error', failure);
}
function action(fn) {
  return async () => {
    if (busy) return;
    busy = true;
    byId('notice').hidden = true;
    try { await fn(); }
    catch (failure) {
      const copy = failure instanceof SyntaxError ? '源资料不是有效的 JSON' : failure.message;
      notify(copy, true);
    } finally { busy = false; }
  };
}
function page(active) {
  state.page = active;
  if (active !== 'stage') timeline.pause();
  for (const button of nav) {
    const key = button.dataset.page;
    byId(key).hidden = key !== active;
    if (key === active) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  }
}
function use(doc, preferred) {
  state.doc = doc;
  state.scene = doc.scenes.some(item => item.id === preferred) ? preferred : doc.scenes[0].id;
  choices(doc, state.scene);
  fill(current());
  byId('json').value = JSON.stringify(doc, null, 2);
  byId('graph-title').textContent = `${doc.title} · 世界坐标`;
  labels = new Map(doc.clips.map(clip => [clip.id, clip.label]));
}
function current() { return state.doc.scenes.find(item => item.id === state.scene); }
function load(record, preferred = state.scene) {
  state.revision = record.revision;
  byId('revision').textContent = `修订 ${record.revision.slice(0,10)}`;
  use(record.document, preferred);
}
function edited() {
  const scene = readScene(current());
  return {document:{...state.doc, scenes:state.doc.scenes.map(item => item.id === scene.id ? scene : item)}, scene};
}
function show(trace, compared = null) {
  comparison = compared;
  comparisonSide = false;
  timeline.show(trace, labels);
  byId('comparison').hidden = !compared;
  byId('comparison-side').textContent = '查看对照';
  const first = compared?.first;
  const fields = {clip:'动作',frame:'源帧',crossed:'穿越帧',world:'根位置',edge:'转场',target:'目标动作',events:'事件',pose:'姿态',consumed:'消费',length:'轨迹长度'};
  byId('difference').textContent = first ? `首个差异位于第 ${first.tick} 拍 · ${first.fields.map(key => fields[key]).join('、')}` : '两条轨迹的可见结果一致';
}
async function preview() { show(await request('run', edited())); }
const history = delivery(action, state, load, async report => {
  load(report, report.scene.id);
  page('stage'); show(report.trace); notify('通过复验，正在显示包内轨迹');
}, notify);
for (const button of nav) button.onclick = action(async () => {
  const target = button.dataset.page;
  if (target === 'source' && state.page === 'stage') {
    byId('json').value = JSON.stringify(edited().document, null, 2);
  }
  if (target === 'revisions') await history();
  page(target);
});
byId('scene').onchange = action(async () => {
  state.scene = byId('scene').value;
  fill(current()); await preview();
});
byId('run').onclick = action(preview);
byId('compare').onclick = action(async () => {
  const left = edited();
  const right = {document:state.doc, scene:byId('compare-scene').value};
  const compared = await request('compare', {left,right});
  show(compared.left, compared);
});
byId('comparison-side').onclick = () => {
  if (!comparison) return;
  comparisonSide = !comparisonSide;
  timeline.show(comparisonSide ? comparison.right : comparison.left, labels, timeline.position());
  byId('comparison-side').textContent = comparisonSide ? '查看当前' : '查看对照';
};
byId('validate').onclick = action(async () => {
  const result = await request('validate', {document:JSON.parse(byId('json').value)});
  use(result.document, state.scene);
  page('stage'); await preview(); notify('动作图通过预检，草稿已应用');
});
byId('save').onclick = action(async () => {
  const doc = state.page === 'source' ? JSON.parse(byId('json').value) : edited().document;
  const record = await request('save', {document:doc, base:state.head});
  state.head = record.revision;
  load(record);
  if (state.page === 'revisions') await history();
  if (state.page === 'stage') await preview();
  notify('已保存修订');
});
action(async () => {
  const record = await request('graph'); state.head = record.revision;
  load(record); await preview();
})();
