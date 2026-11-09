# Código do case: sincronização e erros

Trechos copiados do documento do case, sem mudança. São da página do case, em JavaScript, e servem para ler, não para rodar. O case não publica o resto do código.

## A listagem que lê só o que é novo

```js
// Lê do mais recente para o mais antigo e para assim que uma página inteira
// já está no cérebro: uma checagem normal custa 1 ou 2 chamadas.
for (let page = 1; page <= 80; page++){
  const r = await mcp.callTool("Plaud", "list_files", {page, page_size:50}, {cache:false});
  const arr = (parsePayload(r)?.data || []).filter(f => f && f.id);
  const inRange = arr.filter(f => (f.start_at || f.created_at || "") >= SYNC_FROM);
  // … acumula; se todas já existem em `meetings`, para
  if (arr.length < 50 || inRange.length < arr.length) break;
}
```

Gatilhos: abrir a página, botão "Verificar novas", voltar à aba após 2 min, a cada 10 min com a aba aberta.

## A sincronização em lotes

Parâmetros finais: `BATCH = 3`, `WORKERS = 2`, `NOTE_CHARS = 9000`, pausa de 2,5 s entre chamadas.

Fluxo de `startSync()`:
1. Pendentes = gravações sem documento ou com `status === "erro"`, da mais recente para a mais antiga.
2. Divide em lotes de 3.
3. **Primeiro lote sozinho** (para os avisos de permissão aparecerem uma única vez).
4. Dois *workers* consomem a fila, com pausa entre chamadas.
5. Para cada lote: lê as notas (`get_note`), monta um prompt com as 3 reuniões, chama `sample.json(..., {modelTier:"quick"})`, casa as respostas por `id` e salva cada reunião.
6. Se a resposta do lote vier inválida, **reprocessa uma a uma**; se ainda falhar, grava `status: "erro"` para entrar na próxima sincronização.
7. Ao terminar (ou parar), grava `config/sync` com o resultado.

## O que para tudo e o que só pula

```js
function classify(e, where){
  const code = e?.code || "desconhecido", raw = (e?.message || "").slice(0, 200);
  if (where === "plaud") return FATAL_MCP.includes(code)
      ? {stop:true, code, msg: mcpMessage(e)} : {stop:false, code, msg: mcpMessage(e)};
  if (where === "db"){
    if (code === "quota_exceeded")     return {stop:true, code, msg:"Limite de documentos…"};
    if (code === "resource_exhausted") return {stop:true, code, msg:"Desacelere: espere 1 min…"};
    // …
  }
  // Claude
  if (code === "rate_limited"){
    if (/too often|too many|frequen/i.test(raw))
      return {stop:true, code, msg:"Chamadas seguidas demais. Espere 2 ou 3 minutos e clique em Continuar."};
    return {stop:true, code, msg:"Limite de uso do Claude atingido. O que já foi lido está salvo."};
  }
  if (code === "prompt_too_large") return {stop:false, code, msg:"Notas grandes demais para um lote."};
  return {stop:false, code, msg: raw || code};
}
```

**Lição:** `rate_limited` com "too often" é um **freio de frequência da página**, não falta de cota. A resposta certa é pausar e tentar de novo, não dizer ao usuário que a cota acabou.
