import {byId, request, text} from './transport.js';

export function delivery(action, state, load, replay, notify) {
  async function history() {
    const revisions = await request('revisions');
    state.head = revisions[0].revision;
    byId('history').replaceChildren(...revisions.map(item => {
      const button = text('button', '', 'revision-row');
      button.append(text('span', item.title), text('code', item.revision.slice(0, 10)));
      button.onclick = action(async () => {
        load(await request('graph?revision=' + encodeURIComponent(item.revision)));
        notify('已载入指定修订');
      });
      return button;
    }));
  }
  async function selectedPack() {
    const file = byId('upload').files[0];
    if (!file) throw new Error('请先选择本地交接包');
    if (file.size > 16*1024*1024) throw new Error('交接包超出大小上限');
    try { return JSON.parse(await file.text()); }
    catch { throw new Error('交接包不是有效的 JSON 文件'); }
  }
  byId('refresh').onclick = action(history);
  byId('download').onclick = action(async () => {
    if (!state.revision) throw new Error('请先保存可交接的修订');
    const params = new URLSearchParams({revision:state.revision, scene:state.scene});
    const pack = await request('pack?' + params);
    const url = URL.createObjectURL(new Blob([JSON.stringify(pack)], {type:'application/json'}));
    const link = document.createElement('a'); link.href = url;
    link.download = `stride-${state.scene}-${state.revision.slice(0,10)}.json`;
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    notify('已生成指定修订的交接包');
  });
  byId('verify').onclick = action(async () => {
    const report = await request('verify', {pack:await selectedPack()});
    notify(`复验通过 · ${report.ticks} 拍 · ${report.revision.slice(0,10)}`);
  });
  byId('rehearse').onclick = action(async () => replay(await request('rehearse', {pack:await selectedPack()})));
  return history;
}
