// Testa o motor do simulador com a HyperFormula de verdade, antes de montar a página.
//
// Uso, dentro da pasta dessa aula:
//   npm init -y
//   npm install hyperformula@2.7.1
//   node testar_motor.js                    (usa engine.js e casos.json)
//   node testar_motor.js meu_motor.js meus_casos.json
//
// Para cada caso de casos.json, parte das entradas com que o motor abre, grava as do caso,
// pede o valor das células esperadas e compara ao centavo. Depois, para cada preço da aba
// Curva (a do gráfico), põe o preço na Calculadora e compara a renda das duas.
// Sai com 0 quando tudo bate, 1 quando algo falhou e 2 quando falta a HyperFormula ou o motor.

var fs = require('fs');
var path = require('path');

function brl(v) {
  var neg = v < 0, x = Math.abs(v);
  var cent = Math.abs(x * 100 - Math.round(x * 100)) < 1e-6;
  var s = x.toFixed(cent ? 2 : 4).split('.');
  return (neg ? '-' : '') + s[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ',' + s[1];
}

function separa(ref) {
  var i = ref.lastIndexOf('!');
  return [ref.slice(0, i).replace(/^'|'$/g, ''), ref.slice(i + 1).replace(/\$/g, '').toUpperCase()];
}

function numero(v) {
  return typeof v === 'number' && isFinite(v);
}

// E é o que o buildEngine retorna: { set(aba, célula, valor), get(aba, célula), curvaN }.
function testar(E, casos, escrever) {
  var falhas = 0, total = 0, originais = {};
  casos.forEach(function (caso) {
    // cada caso começa das entradas com que o motor abre
    Object.keys(originais).forEach(function (ref) {
      var c = separa(ref);
      E.set(c[0], c[1], originais[ref]);
    });
    Object.keys(caso.entradas).forEach(function (ref) {
      var c = separa(ref);
      if (!(ref in originais)) originais[ref] = E.get(c[0], c[1]);
      E.set(c[0], c[1], caso.entradas[ref]);
    });
    Object.keys(caso.esperado).forEach(function (ref) {
      var c = separa(ref), v = E.get(c[0], c[1]), esp = caso.esperado[ref];
      total += 1;
      if (!numero(v)) {
        falhas += 1;
        escrever('ERRO  ' + caso.nome + ' · ' + ref + ': o motor retornou ' + JSON.stringify(v && v.value !== undefined ? v.value : v));
      } else if (Math.abs(v - esp) >= 0.005) {
        falhas += 1;
        escrever('ERRO  ' + caso.nome + ' · ' + ref + ': motor ' + brl(v) + ', esperado ' + brl(esp));
      } else {
        escrever('ok    ' + caso.nome + ' · ' + ref + ': ' + (Number.isInteger(esp) && Number.isInteger(v) ? String(v) : brl(v)));
      }
    });
  });
  if (E.curvaN) {
    var diferentes = [];
    for (var r = 1; r <= E.curvaN; r++) {
      var p = E.get('Curva', 'A' + r);
      E.set('Calculadora', 'B6', p);
      var a = E.get('Calculadora', 'B17'), b = E.get('Curva', 'B' + r);
      if (!numero(a) || !numero(b) || Math.abs(a - b) >= 0.005) diferentes.push(p);
    }
    total += 1;
    if (diferentes.length) {
      falhas += 1;
      escrever('ERRO  curva do gráfico: ' + diferentes.length + ' de ' + E.curvaN + ' preços com renda diferente da Calculadora, o primeiro em R$ ' + brl(diferentes[0]));
    } else {
      escrever('ok    curva do gráfico: ' + E.curvaN + ' preços com a mesma renda da Calculadora');
    }
  }
  escrever(falhas ? 'resultado: ' + falhas + ' ERRO em ' + total + ' testes. Não publique.' : 'resultado: tudo ok (' + total + ' testes)');
  return falhas;
}

module.exports = { testar: testar };

if (require.main === module) {
  var HF;
  try {
    HF = require('hyperformula').HyperFormula;
  } catch (e) {
    console.error('ERRO não achei a HyperFormula. Rode, nessa pasta: npm init -y e depois npm install hyperformula@2.7.1');
    process.exit(2);
  }
  var arquivo = path.resolve(process.argv[2] || 'engine.js');
  var casos = JSON.parse(fs.readFileSync(process.argv[3] || 'casos.json', 'utf8')).casos;
  var buildEngine = require(arquivo);
  if (typeof buildEngine !== 'function') {
    console.error('ERRO ' + arquivo + ' não exporta a função buildEngine');
    process.exit(2);
  }
  console.log('HyperFormula ' + (HF.version || '?') + ' · motor: ' + path.basename(arquivo));
  process.exit(testar(buildEngine(HF), casos, console.log) ? 1 : 0);
}
