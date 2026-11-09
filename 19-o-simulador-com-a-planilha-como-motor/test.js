const HF = require('hyperformula').HyperFormula;
const E = require('./engine.js')(HF);
const g = (s, a) => E.get(s, a);

// Caso do extrato real: 3 itens, R$ 10,90, recarga 2%  → renda esperada R$ 4,00
E.set('Calculadora', 'B6', 10.9);
console.log('renda 10,90:', g('Calculadora', 'B17'), 'taxas', g('Calculadora', 'B13'));

// Lote a R$ 29,90 → lucro do lote esperado R$ 3.583,03
E.set('Calculadora', 'B6', 29.9);
['B12','B13','B17','B18','B21','B22','B23','B24','B25','B26']
  .forEach(a => console.log('Sim', a, g('Simulação de lote', a)));

// Tabela de 6 preços
for (let r = 30; r < 36; r++)
  console.log(['A','B','C','D','E'].map(c => g('Simulação de lote', c + r)).join(' | '));

// Degrau de R$ 80 → 79,99 deve render mais que 80,00
E.set('Calculadora', 'B6', 79.99); console.log('79.99', g('Calculadora', 'B17'));
E.set('Calculadora', 'B6', 80);    console.log('80',    g('Calculadora', 'B17'));

console.log('curva n', E.curvaN, g('Curva', 'A1'), g('Curva', 'C1'));
