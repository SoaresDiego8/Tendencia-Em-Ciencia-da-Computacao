/**
 * Formata a planilha da Central de Dúvidas como um painel legível.
 *
 * Como usar: na planilha, Extensões → Apps Script → cole este arquivo → salve →
 * escolha a função "formatarPlanilha" → Executar (autorize na primeira vez).
 * Depois disso, o menu "Central de Dúvidas" aparece na própria planilha.
 *
 * O script NÃO altera os nomes das colunas nem a ordem delas: o n8n depende deles.
 * Pode ser executado de novo sempre que quiser reaplicar a formatação.
 */

var COLUNAS = [
  'protocolo', 'data_abertura', 'nome', 'email', 'curso', 'duvida', 'categoria', 'urgencia',
  'resumo', 'resposta_ia', 'classificado_por_ia', 'status', 'responsavel', 'ultima_atualizacao',
  'informacoes_aluno', 'data_ultima_interacao'
];

// Larguras em pixels, na mesma ordem das colunas.
var LARGURAS = [150, 120, 160, 210, 170, 320, 120, 90, 260, 340, 110, 130, 140, 260, 320, 140];

// Colunas com texto longo (quebra de linha automática).
var TEXTO_LONGO = ['duvida', 'resumo', 'resposta_ia', 'ultima_atualizacao', 'informacoes_aluno'];

// Colunas curtas, centralizadas.
var CENTRALIZADAS = ['protocolo', 'data_abertura', 'categoria', 'urgencia', 'classificado_por_ia', 'status', 'data_ultima_interacao'];

var STATUS = ['Respondida', 'Em revisão', 'Aguardando aluno', 'Resolvida'];
var LINHAS = 500;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Central de Dúvidas')
    .addItem('Formatar planilha', 'formatarPlanilha')
    .addToUi();
}

function formatarPlanilha() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('Página1') || ss.getSheets()[0];
  var n = COLUNAS.length;

  // 1. Confere o cabeçalho antes de mexer em qualquer coisa.
  var atual = sh.getRange(1, 1, 1, n).getValues()[0];
  for (var i = 0; i < n; i++) {
    if (String(atual[i]).trim() !== COLUNAS[i]) {
      throw new Error('A coluna ' + (i + 1) + ' deveria se chamar "' + COLUNAS[i] + '", mas está "' + atual[i] +
        '". Corrija o cabeçalho antes de formatar (o n8n depende desses nomes).');
    }
  }

  // 2. Garante linhas suficientes e limpa formatações antigas (sem apagar dados).
  if (sh.getMaxRows() < LINHAS) sh.insertRowsAfter(sh.getMaxRows(), LINHAS - sh.getMaxRows());
  var tudo = sh.getRange(1, 1, LINHAS, n);
  tudo.clearFormat();
  sh.getBandings().forEach(function (b) { b.remove(); });
  sh.clearConditionalFormatRules();

  // 3. Fonte e alinhamento geral.
  tudo.setFontFamily('Inter').setFontSize(10).setVerticalAlignment('top')
    .setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);

  // 4. Cabeçalho: azul-escuro para dados do envio, âmbar para a equipe, verde para o chat.
  var cab = sh.getRange(1, 1, 1, n);
  cab.setBackground('#1f2a44').setFontColor('#ffffff').setFontWeight('bold')
    .setVerticalAlignment('middle').setHorizontalAlignment('center')
    .setWrapStrategy(SpreadsheetApp.WrapStrategy.WRAP);
  sh.getRange(1, col('responsavel'), 1, 2).setBackground('#8a5a00');
  sh.getRange(1, col('informacoes_aluno'), 1, 2).setBackground('#0f6b52');
  sh.setRowHeight(1, 40);
  sh.setFrozenRows(1);
  sh.setFrozenColumns(1);

  // Notas explicativas no cabeçalho.
  sh.getRange(1, col('status')).setNote('Respondida, Em revisão, Aguardando aluno ou Resolvida. A equipe atualiza aqui.');
  sh.getRange(1, col('responsavel')).setNote('Preenchido pela equipe: quem cuida da dúvida.');
  sh.getRange(1, col('ultima_atualizacao')).setNote('Preenchido pela equipe: recado curto que a Duda repassa ao aluno.');
  sh.getRange(1, col('informacoes_aluno')).setNote('Preenchido pela Duda (chat): informações novas enviadas pelo aluno.');

  // 5. Larguras, quebra de linha e alinhamento por coluna.
  LARGURAS.forEach(function (w, i) { sh.setColumnWidth(i + 1, w); });
  var corpo = function (nome) { return sh.getRange(2, col(nome), LINHAS - 1, 1); };
  TEXTO_LONGO.forEach(function (nome) { corpo(nome).setWrapStrategy(SpreadsheetApp.WrapStrategy.WRAP); });
  CENTRALIZADAS.forEach(function (nome) { corpo(nome).setHorizontalAlignment('center'); });
  corpo('protocolo').setFontFamily('Roboto Mono').setFontWeight('bold').setFontColor('#1f2a44');
  corpo('email').setFontColor('#4a5568');

  // 6. Linhas alternadas (a partir da linha 2, para não brigar com o cabeçalho).
  sh.getRange(2, 1, LINHAS - 1, n).applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY, false, false);

  // 7. Lista suspensa de status (aceita outros valores com aviso, para não travar o n8n).
  corpo('status').setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(STATUS, true).setAllowInvalid(true).build()
  );

  // 8. Cores por urgência, status, categoria e falha da IA.
  var regras = [];
  var pinta = function (nome, texto, fundo, fonte) {
    regras.push(SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo(texto)
      .setBackground(fundo).setFontColor(fonte).setBold(true).setRanges([corpo(nome)]).build());
  };
  pinta('urgencia', 'Alta', '#fde2e1', '#b42318');
  pinta('urgencia', 'Média', '#fef0c7', '#93590b');
  pinta('urgencia', 'Baixa', '#e0f2fe', '#075985');
  pinta('status', 'Respondida', '#dcfce7', '#166534');
  pinta('status', 'Em revisão', '#fef3c7', '#92400e');
  pinta('status', 'Aguardando aluno', '#ede9fe', '#5b21b6');
  pinta('status', 'Resolvida', '#e5e7eb', '#374151');
  pinta('categoria', 'Revisão manual', '#fff7ed', '#9a3412');

  var k = columnLetter(col('classificado_por_ia'));
  regras.push(SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=OR($' + k + '2=FALSE,$' + k + '2="false")')
    .setBackground('#fde2e1').setFontColor('#b42318').setBold(true)
    .setRanges([corpo('classificado_por_ia')]).build());

  // Dúvidas urgentes ainda não resolvidas: destaca o protocolo.
  var u = columnLetter(col('urgencia')), s = columnLetter(col('status'));
  regras.push(SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=AND($' + u + '2="Alta",$' + s + '2<>"Resolvida")')
    .setBackground('#b42318').setFontColor('#ffffff')
    .setRanges([corpo('protocolo')]).build());

  sh.setConditionalFormatRules(regras);
  sh.setTabColor('#1f2a44');

  SpreadsheetApp.getActive().toast('Planilha formatada. O n8n continua funcionando normalmente.', 'Central de Dúvidas', 5);
}

function col(nome) {
  var i = COLUNAS.indexOf(nome);
  if (i < 0) throw new Error('Coluna desconhecida: ' + nome);
  return i + 1;
}

function columnLetter(n) {
  var s = '';
  while (n > 0) { var m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
  return s;
}
