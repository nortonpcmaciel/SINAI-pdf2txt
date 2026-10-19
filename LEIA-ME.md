# Conversor local de PDF para SMS

No Windows, abra `iniciar.bat`. Mantenha a janela aberta enquanto usa a página em http://127.0.0.1:8765.

Selecione o PDF e clique em **Converter relatório**. Se houver pendências, a janela **Conferir cadastros** abrirá antes da prévia: corrija o celular ou marque **Ignorar** e confirme. Depois, confira a prévia e clique em **Baixar TXT**. As correções valem para o TXT desta conversão e não alteram o PDF original. O TXT usa UTF-8, quebras de linha Windows e não tem cabeçalho: `PRIMEIRONOME,DDD9XXXXXXXX`.

Compatível com o relatório textual **Relação das Inadimplências** do IMOBSOFT no modelo do PDF fornecido. Não realiza OCR. Outros modelos precisam de adaptação do extrator.

Cada cadastro de comprador é consolidado entre contratos e páginas. Telefones iguais do mesmo cadastro são removidos; clientes diferentes com o mesmo primeiro nome são mantidos. O código internacional 55 é removido. Celulares antigos com DDD e oito dígitos iniciados em 6, 7, 8 ou 9 recebem o nono dígito. Números sem DDD, fixos ou malformados não são inventados: aparecem nas pendências. Confira as pendências antes do envio. Pessoas jurídicas seguem a mesma regra literal de primeiro nome, podendo exigir revisão.

Somente a coluna Celular e suas continuações são lidas; os números de referências pessoais são ignorados. Os arquivos não são enviados para serviços externos. O servidor escuta apenas neste computador e não salva os PDFs enviados.

Requer Python 3 e pypdf. O iniciador usa o Python disponível neste computador; em outro computador, usa o Python instalado e instala a dependência de requirements.txt (internet necessária apenas para essa instalação inicial).
