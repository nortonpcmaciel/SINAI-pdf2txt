import io
import json
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pypdf import PdfReader

ROOT = Path(__file__).parent
DDDS = set('11 12 13 14 15 16 17 18 19 21 22 24 27 28 31 32 33 34 35 37 38 41 42 43 44 45 46 47 48 49 51 53 54 55 61 62 63 64 65 66 67 68 69 71 73 74 75 77 79 81 82 83 84 85 86 87 88 89 91 92 93 94 95 96 97 98 99'.split())

def normalize(raw):
    n = re.sub(r'\D', '', raw)
    if len(n) in (12, 13) and n.startswith('55'):
        n = n[2:]
    if len(n) == 10 and n[2] in '6789':
        n = n[:2] + '9' + n[2:]
    if len(n) != 11 or n[:2] not in DDDS or n[2] != '9':
        return None
    return n

def convert(data):
    reader = PdfReader(io.BytesIO(data))
    clients = {}
    current = None
    column = 0
    for page in reader.pages:
        for line in (page.extract_text(extraction_mode='layout') or '').splitlines():
            if re.match(r'\s*Contrato\b', line):
                current = None
            if 'Compradores' in line and 'Celular' in line:
                left, right = line.split('Celular', 1)
                match = re.search(r'Compradores\s+(\d+)\s*-\s*(.+)', left)
                if not match:
                    raise ValueError('Não foi possível identificar um comprador. Confira o modelo do relatório.')
                code, name = match.groups()
                name = re.split(r'\s+-\s*(?:\d|$)', name.strip())[0].strip()
                current = clients.setdefault(code, {'id': code, 'name': name, 'phones': set(), 'invalid': set()})
                column = line.index('Celular') + len('Celular')
                field = re.split(r'Cidade|CEP', right)[0].strip()
            elif current:
                if re.search(r'Usuário|Usu.rio|Emiss.o:|SINAI E MORIA', line):
                    continue
                if re.search(r'Ref\.|Parcela|Totais', line):
                    current = None
                    continue
                field = re.split(r'Cidade|CEP', line[column:column+47])[0].strip()
            else:
                continue
            # Only the phone column is read; addresses and personal references are excluded.
            if field and len(re.sub(r'\D', '', field)) >= 7 and re.fullmatch(r'[\d\s().+\-/]+', field):
                for raw in re.split(r'\s{2,}|\s*/\s*|\s*;\s*', field):
                    if not raw.strip():
                        continue
                    phone = normalize(raw)
                    if phone:
                        current['phones'].add(phone)
                    else:
                        current['invalid'].add(raw)
    if not clients:
        raise ValueError('Nenhum comprador encontrado. Use um PDF com texto no modelo Relação das Inadimplências do IMOBSOFT. PDFs digitalizados precisam de OCR.')
    rows, issues = [], []
    for client in clients.values():
        for phone in sorted(client['phones']):
            rows.append({'id': client['id'], 'name': client['name'].split()[0], 'phone': phone})
        if client['invalid'] or not client['phones']:
            issues.append({'id': client['id'], 'name': client['name'], 'reason': 'Número inválido: ' + ', '.join(sorted(client['invalid'])) if client['invalid'] else 'Sem celular válido no cadastro'})
    return {'pages': len(reader.pages), 'clients': len(clients), 'rows': rows, 'issues': issues,
            'text': '\r\n'.join(f"{r['name']},{r['phone']}" for r in rows) + ('\r\n' if rows else '')}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path not in ('/', '/index.html', '/logo_sinai-transparente.png'):
            self.send_error(404)
            return
        is_logo = path == '/logo_sinai-transparente.png'
        body = (ROOT / ('logo_sinai-transparente.png' if is_logo else 'index.html')).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'image/png' if is_logo else 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != '/convert':
            self.send_error(404)
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 30 * 1024 * 1024:
                raise ValueError('Selecione um PDF de até 30 MB.')
            data = self.rfile.read(size)
            if not data.startswith(b'%PDF-'):
                raise ValueError('O arquivo selecionado não é um PDF válido.')
            result = convert(data)
            status = 200
        except Exception as exc:
            result = {'error': str(exc)}
            status = 400
        body = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

if __name__ == '__main__':
    print('Conversor local: http://127.0.0.1:8765', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
