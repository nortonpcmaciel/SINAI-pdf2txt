# SINAI-pdf2txt

Página web de funcionamento local para converter relatórios de inadimplência do IMOBSOFT em listas de nomes e celulares para envio de SMS em massa.

## Acessar online

Abra https://nortonpcmaciel.github.io/SINAI-pdf2txt/ em um navegador atualizado. A conversão usa a distribuição de compatibilidade (legacy) do PDF.js 5.4.296 e acontece inteiramente no navegador, sem upload dos PDFs. Não exige Python para uso online.

## Executar no Windows

1. Instale o Python 3 com a opção de adicioná-lo ao PATH.
2. Baixe ou clone este repositório.
3. Execute `iniciar.bat` e mantenha a janela aberta.
4. Acesse http://127.0.0.1:8765 no navegador.

A primeira execução pode precisar de internet para instalar a dependência `pypdf`.

Para executar manualmente:

```sh
python -m pip install -r requirements.txt
python app.py
```

## Converter

Selecione o PDF e clique em **Converter relatório**. Quando houver números ausentes ou inválidos, a janela **Conferir cadastros** permite corrigir o celular ou ignorar a pendência antes de gerar a prévia. Clique em **Baixar TXT** para salvar a lista.

Formato de saída, sem cabeçalho, em UTF-8 com quebras de linha Windows:

```text
MARIA,94987654321
```

- Extrai o primeiro nome e os celulares da coluna **Celular**.
- Consolida o mesmo cadastro entre contratos e páginas.
- Remove números repetidos do mesmo cliente, mantendo os celulares diferentes.
- Remove o prefixo internacional 55 e inclui o nono dígito em celulares antigos com DDD.
- Ignora referências pessoais e sinaliza números inválidos para conferência.
- As correções afetam apenas a conversão atual, sem modificar o PDF original.

## Compatibilidade e privacidade

Compatível com PDFs com texto no modelo **Relação das Inadimplências** do IMOBSOFT. Outros layouts precisam de adaptação. PDFs de imagens devem passar por OCR antes da importação; o aplicativo não realiza OCR.

Na versão online, os PDFs são processados na memória do navegador e não são enviados a serviços externos. Na execução local, o servidor escuta apenas em `127.0.0.1`. Relatórios e listas de clientes estão excluídos do controle de versão pelo `.gitignore`.

## Arquivos

- `app.py`: servidor local e extração do PDF.
- `index.html`: interface e conferência dos telefones.
- `logo_sinai-transparente.png`: logotipo usado no cabeçalho.
- `iniciar.bat`: iniciador para Windows.
- `requirements.txt`: dependência Python.

## Dependência de terceiros

PDF.js (Mozilla), versão 5.4.296, distribuição legacy com suporte a APIs ausentes em navegadores anteriores, incluído nos arquivos `pdf.mjs` e `pdf.worker.mjs`, sob licença Apache 2.0 disponível em `PDFJS-LICENSE`. O arquivo `converter.mjs` adapta a extração ao modelo do relatório.
