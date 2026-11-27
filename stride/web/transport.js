const endpoint = '/stride/api/';
export async function request(route, payload) {
  const options = payload === undefined ? {} : {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
  };
  const response = await fetch(endpoint + route, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || '请求未完成');
  return body;
}
export const byId = id => document.getElementById(id);
export function text(tag, content, className) {
  const node = document.createElement(tag);
  node.textContent = content;
  if (className) node.className = className;
  return node;
}
