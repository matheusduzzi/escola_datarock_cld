# Código do case: agenda e auditoria

Os blocos de código e o prompt são cópia do documento do case, sem mudança. As listas seguem o texto do case, com uma palavra trocada. O código é da página do case, em JavaScript, e serve para ler, não para rodar. O `ligador.py` dessa pasta faz a mesma ligação e a mesma correção em Python, sobre os arquivos do kit. Onde o case não dá o detalhe, o `ligador.py` diz a escolha que fez.

## Ligar a gravação ao evento

A evolução foi: (1) só sobreposição de horário ≥ 30%; (2) + tolerância de 15 min de atraso; (3) + preferência por convidados citados; (4) versão final abaixo, depois da auditoria.

```js
function eventForTimes(rs, re, spoken, text){
  // candidatos: eventos de 60 min antes a 30 min depois da gravação
  for (const x of calEvSorted){
    const ov = Math.max(0, Math.min(re, x.e) - Math.max(rs, x.s));
    const covRec = ov / (re - rs), covEv = ov / (x.e - x.s);
    const hits = quantasPessoasCitadasEstaoNoConvite(x.ev);
    let ok = covRec >= 0.3 || covEv >= 0.5;                 // bate no horário
    if (!ok && hits) ok = ov >= 5min                        // pouca sobreposição, mas gente certa
                        || (gravação começou até 60 min após o fim)
                        || (gravação terminou até 30 min antes do início);
    if (!ok && !hits && começou até 15 min após o fim) ok = true;  // reunião que atrasou
    if (ok) cands.push({ev, time: ov / max(duração), hits, ts: similaridadeTítulo×Assunto});
  }
  // pontuação
  score = time × (há candidatos com pessoas e este não tem ? 0.6 : 1)
        + 0.8 × (hits / citados) + (hits ? 0.1 : 0) + 0.5 × ts;
  return melhor;
}
```

Regras complementares:
- **Gravação longa** (> 50 min) que cobre **duas reuniões seguidas** (ex.: Status Report + Daily) é ligada às duas, se a sobreposição com a segunda passar de 15 min.
- **Eventos sem convidados** (workshop, palestra) não trazem pessoas, mas dão **título e contexto** à gravação (`soloEventFor`, cobertura ≥ 50%).
- **Ligação manual** em `config/callinks` sempre vence ("Evento errado?" no painel).

## Quem estava na reunião e a correção de nomes

```js
const nameOf = a => emailNames[a?.e] || a?.n || "";   // e-mail confirmado vence o nome do convite

function entitiesOf(m, ty){
  if (ty !== "pessoa") return m.entities[FIELD[ty]] || [];
  // 1) tira "Speaker 1", "Falante 2"…  2) aplica a correção DESTA reunião
  const ren  = new Map((spokenMatch.get(m.fid) || []).map(p => [norm(p[0]), p[1]]));
  const base = raw.filter(p => !SPEAKER_RE.test(p)).map(p => ren.get(norm(p)) || p);
  // 3) acrescenta convidados: todos se a reunião tem até 10 pessoas;
  //    nas maiores, só os convidados que a gravação citou
  const add = ev.n > ATT_MAX ? convidadosCitados : todosConvidados;
  return unicos([...base, ...add]);
}
```

**Correção por reunião (decisão-chave da auditoria):** o nome falado é trocado pelo nome do convite **daquela reunião**. "Bruno" numa reunião vira o Bruno daquele convite; em outra, pode ser outro Bruno. Uma correção global teria fundido pessoas diferentes.

Fontes de correção, em ordem:
1. **Regra automática** (`fuzzyInviteHits`): o nome falado bate foneticamente com **exatamente um** convidado (token único: igual ou Jaro-Winkler ≥ 0,9 com 4+ letras; vários tokens: todos ≥ 0,92).
2. **Apelidos** conhecidos (`NICK`: Léo → Leonardo/Leandro, Juju → Juliana/Juliano/Júlia, Rafa, Gabi, Nando…).
3. **Revisão com o Claude** (`aiFixNames`, botão "Corrigir nomes com a agenda"), em lotes de 12 reuniões, guardada em `config/renames`, sem refazer reuniões já revistas:
   ```text
   Transcrições automáticas erram nomes próprios. Para cada reunião abaixo há
   os nomes citados na transcrição e a lista de convidados (grafia correta).
   Para cada nome citado, diga qual convidado ele é, SOMENTE se for claramente
   a mesma pessoa (erro de grafia, apelido, diminutivo, só o primeiro nome ou
   só o sobrenome). Se não estiver entre os convidados, não inclua.
   Responda somente com JSON: {"mapa":[{"i":0,"citado":"","convidado":""}]}
   ```
4. **E-mails de função confirmados** pelo dono (`config/emailnames`).

## Auditoria do ano inteiro: método

1. **Baixar tudo para arquivos** (nunca ler 800 reuniões dentro da conversa):
   ```text
   ArtifactData action=list collection=meetings out_dir=/…/dbdump query={limit:1000}
   ArtifactData action=list collection=cal      out_dir=/…/dbdump
   ArtifactData action=list collection=config   out_dir=/…/dbdump
   ```
2. **Rodar o mesmo código da página em Node** (um *harness* que extrai as funções do HTML e as executa sobre os arquivos), para que auditoria e página nunca divirjam.
3. Gerar **categorias de problema** com contagens e exemplos: gravações sem evento, eventos com convidados sem nome, gravações ligadas "talvez" ao evento errado, gravações longas sobre dois eventos, nomes falados sem correspondência.
4. Corrigir a lógica, **rodar de novo** e comparar antes × depois.
5. Gravar as correções com `batch` e `if_version` (concorrência otimista), publicar a página e reabrir.

## Auditoria: princípios de segurança

- Somente leitura até a lógica estar validada.
- **Nunca sobrescrever separações manuais** do dono.
- Correções duvidosas ficam de fora e são listadas para o dono decidir.
- Correções por reunião, nunca globais.
