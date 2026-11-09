# Código do case: o resolvedor de nomes

Os blocos de código e a lista das sugestões são cópia do documento do case, sem mudança. As frases entre eles resumem o texto do case. O código é da página do case, em JavaScript, e serve para ler, não para rodar. O `resolvedor.py` dessa pasta faz o mesmo em Python.

## Normalização

```js
const norm = s => String(s||"").normalize("NFD").replace(/[̀-ͯ]/g,"")
  .toLowerCase().replace(/[^a-z0-9]+/g," ").trim();
const STOP = new Set("de da do das dos e a o as os em no na nos nas para por com the of and".split(" "));
const CORP = new Set("s sa ltda me eireli inc llc corp co grupo group holding".split(" "));
```

Para empresas, o case ignora os sufixos societários ("Fornecedor A S.A." = "Fornecedor A").

## Chave fonética para português

```js
function phon(tok, plural){
  if (/^\d+$/.test(tok)) return tok;
  let s = tok;
  if (plural && s.length > 3){                       // singulariza (não para pessoas)
    if (/oes$|aes$/.test(s)) s = s.slice(0,-3) + "ao";
    else if (/ns$/.test(s))  s = s.slice(0,-2) + "m";
    else if (/[^s]s$/.test(s)) s = s.slice(0,-1);
  }
  s = s.replace(/ph/g,"f").replace(/th/g,"t").replace(/[sc]h/g,"x")
       .replace(/lh/g,"li").replace(/nh/g,"ni").replace(/y/g,"i").replace(/w/g,"v")
       .replace(/k/g,"c").replace(/qu(?=[ei])/g,"c").replace(/q/g,"c")
       .replace(/gu(?=[ei])/g,"g").replace(/c(?=[ei])/g,"s").replace(/z/g,"s")
       .replace(/^h/,"").replace(/h/g,"").replace(/(.)\1+/g,"$1");
  if (s.length > 2) s = s.replace(/e$/,"i").replace(/u$/,"o");   // final átono
  return s;
}
```

Com isso, "Valore", "Valori" e "Walori" geram a mesma chave (`valori`), e "Data Hub" = "DataHub" (as chaves também são comparadas sem espaços).

## Siglas

```js
const ABBR_BASE = [
  ["inteligencia artificial","ia"],["artificial intelligence","ia"],["ai","ia"],
  ["genai","ia generativa"],["machine learning","ml"],["aprendizado de maquina","ml"],
  ["large language model","llm"],["modelos de linguagem","llm"],
  ["recursos humanos","rh"],["business intelligence","bi"],
  ["prova de conceito","poc"],["produto minimo viavel","mvp"],
  ["lei geral de protecao de dados","lgpd"],["key performance indicators","kpi"],
  ["processamento de linguagem natural","nlp"],["pln","nlp"], /* … */
];
```

Aprendizado: se existe um rótulo todo em maiúsculas ("CRM") e, do mesmo tipo, uma expressão de 2 a 6 palavras cujas iniciais formam a sigla ("Customer Relationship Management"), o par entra nas substituições.

## Uniões com "não unir"

```js
for (const [a, b] of mergeCfg.pairs || []) union(a, b, "manual");   // 1) manuais
if (mergeCfg.auto !== false){
  // 2) mesma chave fonética/sigla (inclusive sem espaços) ⇒ mesmo nó
  for (const ids of byKey.values()) for (let i = 1; i < ids.length; i++) union(ids[0], ids[i], "auto");
}
// `union` recusa juntar dois grupos se houver qualquer par marcado em `splits`
```

- Rótulo do nó: primeiro a grafia que aparece num convite da agenda, depois a mais frequente, depois a mais longa.
- Os pares de "não unir" valem sempre: nenhuma regra automática ou revisão junta os dois depois.

## Sugestões

Para o que a chave exata não pega, a janela **"Unificar nós"** lista sugestões:

- Similaridade **Jaro-Winkler** entre chaves fonéticas, limiar padrão **0,88** (configurável).
- Caso especial para pessoas: **nome × nome completo** ("Valore" × "Marcos Valore") com score 0,8, se o token único for o primeiro ou último nome e tiver 4+ letras.
- Ignora chaves com menos de 4 caracteres e pares com tamanhos muito diferentes.
- Até 200 sugestões ordenadas por score e frequência; cada uma com **Unir / Não são iguais**.
- Botão **"Revisar com o Claude"**: manda os pares duvidosos com exemplos de contexto e recebe veredictos.
- No painel de cada nó: **unir manualmente** com outro nó e **separar** um membro do cluster.
