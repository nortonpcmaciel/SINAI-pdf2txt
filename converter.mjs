import {getDocument, GlobalWorkerOptions} from './pdf.mjs';
GlobalWorkerOptions.workerSrc = new URL('./pdf.worker.mjs', import.meta.url).href;

export async function convertPDF(file, normalize, progress = () => {}) {
  if (!file.size || file.size > 30 * 1024 * 1024) throw Error('Selecione um PDF de até 30 MB.');
  const task = getDocument({data: new Uint8Array(await file.arrayBuffer()), useSystemFonts: true, isEvalSupported: false});
  const doc = await task.promise;
  const clients = new Map();
  let current = null, column = 0, endColumn = 0;
  try {
    for (let pageNumber = 1; pageNumber <= doc.numPages; pageNumber++) {
      progress(pageNumber, doc.numPages);
      const page = await doc.getPage(pageNumber);
      const content = await page.getTextContent();
      const lines = [];
      for (const item of content.items.filter(i => i.str?.trim()).sort((a,b) => b.transform[5]-a.transform[5])) {
        let line = lines.find(l => Math.abs(l.y-item.transform[5]) < 1.5);
        if (!line) {line = {y:item.transform[5], items:[]}; lines.push(line);}
        line.items.push(item);
      }
      for (const line of lines) {
        const items = line.items.sort((a,b) => a.transform[4]-b.transform[4]);
        const text = items.map(i => i.str).join(' ');
        if (/^Contrato\b/.test(text)) current = null;
        const celular = items.find(i => i.str.trim() === 'Celular');
        if (text.includes('Compradores') && celular) {
          const left = items.filter(i => i.transform[4] < celular.transform[4]).map(i=>i.str).join(' ');
          const match = left.match(/Compradores\s+(\d+)\s*-\s*(.+)/);
          if (!match) throw Error('Não foi possível identificar um comprador. Confira o modelo do relatório.');
          const [,id,rawName] = match;
          const name = rawName.split(/\s+-\s*(?=\d|$)/)[0].trim();
          if (!clients.has(id)) clients.set(id,{id,name,phones:new Set(),invalid:new Set()});
          current = clients.get(id);
          column = celular.transform[4] + celular.width;
          endColumn = items.find(i => i.str.trim() === 'Cidade')?.transform[4] ?? column+120;
        } else if (current) {
          if (/Usuário|Emissão:|SINAI E MORIA/.test(text)) continue;
          if (/Ref\.|Parcela|Totais/.test(text)) {current=null;continue;}
        }
        if (!current) continue;
        const field = items.filter(i => i.transform[4] >= column-1 && i.transform[4] < endColumn-2).map(i=>i.str).join(' ').split(/Cidade|CEP/)[0].trim();
        if (field.replace(/\D/g,'').length < 7 || !/^[\d\s().+\-/;]+$/.test(field)) continue;
        for (const raw of field.split(/\s*[/;]\s*/)) {
          const phone = normalize(raw);
          if (phone) current.phones.add(phone); else current.invalid.add(raw);
        }
      }
      page.cleanup();
    }
    if (!clients.size) throw Error('Nenhum comprador encontrado. Use um PDF com texto no modelo Relação das Inadimplências do IMOBSOFT. PDFs digitalizados precisam de OCR.');
    const rows=[],issues=[];
    for (const client of clients.values()) {
      for (const phone of [...client.phones].sort()) rows.push({id:client.id,name:client.name.split(/\s+/)[0],phone});
      if (client.invalid.size || !client.phones.size) issues.push({id:client.id,name:client.name,reason:client.invalid.size ? 'Número inválido: '+[...client.invalid].sort().join(', ') : 'Sem celular válido no cadastro'});
    }
    return {pages:doc.numPages,clients:clients.size,rows,issues};
  } finally {await doc.destroy();}
}
