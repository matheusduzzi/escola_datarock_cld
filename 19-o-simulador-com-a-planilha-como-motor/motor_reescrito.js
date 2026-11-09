function buildEngine(HF) {
  var hf = HF.buildEmpty({ licenseKey: 'gpl-v3' });
  var NAMES = ['Calculadora', 'Simulação de lote', 'Taxas', 'Curva'];
  NAMES.forEach(function (n) { hf.addSheet(n); });

  // Converte "B17" em {sheet, row, col} (base 0) para a API da HyperFormula
  function colIdx(s) { var n = 0; for (var i = 0; i < s.length; i++) n = n * 26 + (s.charCodeAt(i) - 64); return n - 1; }
  function addr(sheet, a1) {
    var m = /^([A-Z]+)(\d+)$/.exec(a1);
    return { sheet: hf.getSheetId(sheet), row: +m[2] - 1, col: colIdx(m[1]) };
  }
  function set(sheet, a1, v) { hf.setCellContents(addr(sheet, a1), [[v]]); }
  function get(sheet, a1) { return hf.getCellValue(addr(sheet, a1)); }

  // Renda do pedido para o preço que está na célula p (mesma fórmula do .xlsx)
  function renda(p) {
    return '=' + p + '-ROUND(' + p + '*INDEX(Taxas!$B$4:$B$7,MATCH(' + p + ',Taxas!$A$4:$A$7,1)),2)' +
      '-ROUND(IF(' + p + '<Taxas!$B$10,' + p + '/2,INDEX(Taxas!$C$4:$C$7,MATCH(' + p + ',Taxas!$A$4:$A$7,1))),2)' +
      '-ROUND(' + p + '*Taxas!$B$11,2)';
  }

  hf.batch(function () {
    // ----- Taxas -----
    [[0, 0.20, 4.5], [80, 0.14, 16], [100, 0.14, 20], [200, 0.14, 26]].forEach(function (r, i) {
      set('Taxas', 'A' + (4 + i), r[0]); set('Taxas', 'B' + (4 + i), r[1]); set('Taxas', 'C' + (4 + i), r[2]);
    });
    set('Taxas', 'B10', 8);
    set('Taxas', 'B11', 0.02);

    // ----- Calculadora -----
    set('Calculadora', 'B5', 3);
    set('Calculadora', 'B6', 29.9);
    set('Calculadora', 'B9', '=INDEX(Taxas!$B$4:$B$7,MATCH($B$6,Taxas!$A$4:$A$7,1))');
    set('Calculadora', 'B10', '=-ROUND($B$6*B9,2)');
    set('Calculadora', 'B11', '=-ROUND(IF($B$6<Taxas!$B$10,$B$6/2,INDEX(Taxas!$C$4:$C$7,MATCH($B$6,Taxas!$A$4:$A$7,1))),2)');
    set('Calculadora', 'B12', '=-$B$6*Taxas!$B$11');
    set('Calculadora', 'B13', '=SUM(B10:B12)');
    set('Calculadora', 'B14', '=IF($B$6=0,0,-B13/$B$6)');
    set('Calculadora', 'B17', '=$B$6+B13');

    // ----- Simulação de lote -----
    set('Simulação de lote', 'B5', 1000);
    set('Simulação de lote', 'B6', 0.97);
    set('Simulação de lote', 'B7', '=Calculadora!B5');
    set('Simulação de lote', 'B8', 5);
    set('Simulação de lote', 'B9', 50);
    set('Simulação de lote', 'B12', '=IF($B$7=0,0,INT($B$5/$B$7))');
    set('Simulação de lote', 'B13', '=$B$5-$B$12*$B$7');
    set('Simulação de lote', 'B14', '=$B$12*$B$7*$B$6');
    set('Simulação de lote', 'B15', '=$B$12*$B$8');
    set('Simulação de lote', 'B16', '=$B$9');
    set('Simulação de lote', 'B17', '=SUM(B14:B16)');
    set('Simulação de lote', 'B18', '=IF($B$12=0,0,B17/$B$12)');
    set('Simulação de lote', 'B21', '=Calculadora!B6');
    set('Simulação de lote', 'B22', '=Calculadora!B17');
    set('Simulação de lote', 'B23', '=B22-B18');
    set('Simulação de lote', 'B24', '=B23*B12');
    set('Simulação de lote', 'B25', '=IF($B$17=0,0,B24/$B$17)');
    set('Simulação de lote', 'B26', '=(Taxas!C4+B18)/(1-Taxas!B4-Taxas!B11)');
    [19.9, 24.9, 29.9, 34.9, 39.9, 49.9].forEach(function (p, i) {
      var r = 30 + i;
      set('Simulação de lote', 'A' + r, p);
      set('Simulação de lote', 'B' + r, renda('A' + r));
      set('Simulação de lote', 'C' + r, '=B' + r + '-$B$18');
      set('Simulação de lote', 'D' + r, '=C' + r + '*$B$12');
      set('Simulação de lote', 'E' + r, '=IF($B$17=0,0,D' + r + '/$B$17)');
    });

    // ----- Curva (lucro final do lote por preço, para o gráfico) -----
    var prices = [];
    for (var p = 10; p <= 150; p += 0.5) prices.push(Math.round(p * 100) / 100);
    prices.push(79.99, 99.99);                       // pontos extras para o degrau aparecer nítido
    prices.sort(function (a, b) { return a - b; });
    prices.forEach(function (p, i) {
      var r = i + 1;
      set('Curva', 'A' + r, p);
      set('Curva', 'B' + r, renda('A' + r));
      set('Curva', 'C' + r, "=(B" + r + "-'Simulação de lote'!$B$18)*'Simulação de lote'!$B$12");
    });
    hf.__curvaN = prices.length;
  });

  return { hf: hf, set: set, get: get, curvaN: hf.__curvaN };
}
if (typeof module !== 'undefined') module.exports = buildEngine;
