from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pipeline.common import RunContext, read_csv

LOGGER = logging.getLogger(__name__)


def _records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        LOGGER.warning("Fila ausente; checklist usara conjunto vazio: %s", path)
        return []
    return read_csv(path).to_dict(orient="records")


def _json_for_html(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def build_checklist(context: RunContext) -> Path:
    manifest = context.load_manifest()
    snapshot_hash = (
        manifest.get("steps", {}).get("snapshot", {}).get("snapshot_sha256", "")
    )
    datasets = {
        "catalog": _records(context.paths.processed / "fila_curadoria_catalogo.csv"),
        "calibration": _records(context.paths.processed / "amostra_calibracao.csv"),
        "evidence": _records(context.paths.processed / "fila_revisao.csv"),
    }
    metadata = {
        "run_id": context.run_id,
        "as_of": context.as_of,
        "snapshot_sha256": snapshot_hash,
    }
    html = (
        HTML_TEMPLATE.replace("__CHECKLIST_METADATA__", _json_for_html(metadata))
        .replace("__CHECKLIST_DATASETS__", _json_for_html(datasets))
    )
    output_path = context.paths.outputs / "checklist_validacao.html"
    output_path.write_text(html, encoding="utf-8")
    context.update_manifest(
        "checklist",
        output_file=str(output_path.relative_to(context.paths.root)),
        catalog_items=len(datasets["catalog"]),
        calibration_items=len(datasets["calibration"]),
        evidence_items=len(datasets["evidence"]),
    )
    LOGGER.info(
        "Checklist HTML gerado: %s (%s catalogo, %s calibracao, %s evidencias)",
        output_path,
        len(datasets["catalog"]),
        len(datasets["calibration"]),
        len(datasets["evidence"]),
    )
    return output_path


HTML_TEMPLATE = r"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Checklist de validação | Lacunas de Capacitação CNJ</title>
  <style>
    :root {
      --ink: #172033;
      --muted: #607089;
      --paper: #ffffff;
      --canvas: #f3f6fa;
      --line: #d8e0ea;
      --navy: #173b63;
      --blue: #245f9e;
      --green: #157347;
      --red: #b42318;
      --amber: #9a6700;
      --soft-blue: #eaf2fb;
      --soft-green: #e9f6ee;
      --soft-red: #fceceb;
      --soft-amber: #fff7df;
      --radius: 14px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--canvas);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      line-height: 1.45;
    }
    button, input, select, textarea { font: inherit; }
    button { cursor: pointer; }
    .shell { max-width: 1500px; margin: 0 auto; padding: 22px; }
    header {
      display: flex;
      gap: 18px;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 16px;
    }
    h1 { margin: 0 0 6px; font-size: 25px; color: var(--navy); }
    h2 { margin: 0; font-size: 18px; color: var(--navy); }
    h3 { margin: 0 0 8px; font-size: 15px; color: var(--navy); }
    p { margin: 0; }
    .muted { color: var(--muted); }
    .small { font-size: 12px; }
    .card {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: 0 5px 16px rgba(30, 55, 90, .05);
    }
    .top-actions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
    .button {
      border: 1px solid var(--line);
      border-radius: 9px;
      padding: 9px 12px;
      background: var(--paper);
      color: var(--ink);
      font-weight: 650;
    }
    .button:hover { border-color: var(--blue); }
    .primary { background: var(--navy); border-color: var(--navy); color: white; }
    .success { background: var(--green); border-color: var(--green); color: white; }
    .danger { background: var(--red); border-color: var(--red); color: white; }
    .warning { background: var(--amber); border-color: var(--amber); color: white; }
    .notice { padding: 11px 14px; margin-bottom: 14px; background: var(--soft-amber); border-color: #ecd58b; }
    .tabs { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
    .tab.active { background: var(--navy); border-color: var(--navy); color: white; }
    .overview {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }
    .metric { padding: 13px; }
    .metric strong { display: block; color: var(--navy); font-size: 22px; }
    .controls {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr auto;
      gap: 9px;
      align-items: end;
      padding: 12px;
      margin-bottom: 14px;
    }
    label { display: block; color: var(--muted); font-size: 12px; font-weight: 700; }
    input, select, textarea {
      width: 100%;
      margin-top: 4px;
      padding: 9px 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--ink);
      background: white;
    }
    textarea { min-height: 76px; resize: vertical; }
    .workspace { display: grid; grid-template-columns: minmax(0, 1fr) 292px; gap: 14px; }
    .review { padding: 18px; min-height: 560px; }
    .sidebar { padding: 14px; align-self: start; position: sticky; top: 12px; }
    .toolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between; margin-bottom: 14px; }
    .toolbar-actions { display: flex; gap: 8px; }
    .progress { height: 8px; overflow: hidden; margin: 10px 0 4px; background: #e6ebf2; border-radius: 999px; }
    .progress > div { height: 100%; background: var(--green); }
    .badge {
      display: inline-block;
      margin: 0 5px 5px 0;
      padding: 4px 7px;
      border-radius: 999px;
      background: var(--soft-blue);
      color: var(--navy);
      font-size: 12px;
      font-weight: 700;
    }
    .badge.pending { background: var(--soft-amber); color: var(--amber); }
    .badge.done { background: var(--soft-green); color: var(--green); }
    .meta { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 9px; margin: 14px 0; }
    .meta div { padding: 9px; border-radius: 8px; background: #f7f9fc; }
    .meta span { display: block; color: var(--muted); font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .excerpt {
      max-height: 330px;
      overflow: auto;
      margin: 12px 0;
      padding: 14px;
      border-left: 4px solid var(--blue);
      background: #f8fbff;
      white-space: pre-wrap;
    }
    .actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    details { margin-top: 12px; border-top: 1px solid var(--line); padding-top: 10px; }
    summary { cursor: pointer; color: var(--navy); font-weight: 700; }
    .sidebar .button { width: 100%; margin-top: 8px; text-align: left; }
    .shortcut { display: flex; justify-content: space-between; gap: 8px; padding: 4px 0; color: var(--muted); font-size: 12px; }
    kbd { padding: 1px 5px; border: 1px solid var(--line); border-radius: 4px; background: #f7f9fc; }
    a { color: var(--blue); }
    .empty { padding: 48px 12px; color: var(--muted); text-align: center; }
    @media (max-width: 900px) {
      .overview { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .controls, .workspace { grid-template-columns: 1fr; }
      .sidebar { position: static; }
      .meta, .grid { grid-template-columns: 1fr; }
      header { display: block; }
      .top-actions { justify-content: flex-start; margin-top: 10px; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div>
        <h1>Checklist de validação da pesquisa</h1>
        <p class="muted">Lacunas de Capacitação CNJ · <span id="run-label"></span></p>
      </div>
      <div class="top-actions">
        <button class="button" id="export-backup">Baixar backup JSON</button>
        <button class="button" id="import-backup">Restaurar backup</button>
        <input type="file" id="backup-file" accept=".json,application/json" hidden>
      </div>
    </header>

    <section class="card notice small">
      As decisões ficam salvas automaticamente neste navegador. Antes de limpar
      dados do navegador ou trocar de computador, baixe um backup JSON. Para
      continuar o pipeline, use os botões de exportação CSV.
    </section>

    <nav class="tabs" id="tabs"></nav>

    <section class="overview" id="overview"></section>

    <section class="card controls">
      <label>Pesquisar
        <input id="search" type="search" placeholder="Título, trecho, termo ou URL">
      </label>
      <label>Situação
        <select id="status-filter">
          <option value="all">Todos</option>
          <option value="pending">Pendentes</option>
          <option value="done">Validados</option>
        </select>
      </label>
      <label>Seção
        <select id="section-filter">
          <option value="all">Todas</option>
          <option value="Producao Interna">Produção Interna</option>
          <option value="Parcerias Institucionais">Parcerias Institucionais</option>
        </select>
      </label>
      <label>Score mínimo
        <input id="score-filter" type="number" min="0" step="1" value="0">
      </label>
      <button class="button" id="clear-filters">Limpar filtros</button>
    </section>

    <section class="workspace">
      <article class="card review" id="review"></article>
      <aside class="card sidebar">
        <h3>Andamento da aba</h3>
        <div id="tab-progress"></div>
        <button class="button primary" id="export-csv">Baixar CSV preenchido</button>
        <p class="small muted" id="export-name"></p>
        <h3 style="margin-top: 18px">Identificação</h3>
        <label>Revisor principal
          <input id="reviewer-id" placeholder="Nome ou iniciais">
        </label>
        <label style="margin-top: 8px">Auditor
          <input id="auditor-id" placeholder="Nome ou iniciais">
        </label>
        <h3 style="margin-top: 18px">Atalhos</h3>
        <div class="shortcut"><span>Item anterior</span><kbd>←</kbd></div>
        <div class="shortcut"><span>Próximo item</span><kbd>→</kbd></div>
        <div class="shortcut"><span>Primeira decisão</span><kbd>1</kbd></div>
        <div class="shortcut"><span>Segunda decisão</span><kbd>2</kbd></div>
        <div class="shortcut"><span>Terceira decisão</span><kbd>3</kbd></div>
        <div class="shortcut"><span>Marcar relatório</span><kbd>R</kbd></div>
      </aside>
    </section>
  </main>

  <script id="checklist-metadata" type="application/json">__CHECKLIST_METADATA__</script>
  <script id="checklist-datasets" type="application/json">__CHECKLIST_DATASETS__</script>
  <script>
    "use strict";

    const metadata = JSON.parse(document.getElementById("checklist-metadata").textContent);
    const datasets = JSON.parse(document.getElementById("checklist-datasets").textContent);
    const tabSpec = {
      catalog: {
        label: "Catálogo",
        id: "doc_id",
        file: "fila_curadoria_catalogo_preenchida.csv"
      },
      calibration: {
        label: "Calibração",
        id: "evidencia_id",
        file: "amostra_calibracao_preenchida.csv"
      },
      evidence: {
        label: "Evidências",
        id: "evidencia_id",
        file: "fila_revisao_preenchida.csv"
      }
    };
    const storageKey = `cnj-checklist:${metadata.run_id}:${metadata.snapshot_sha256 || "sem-hash"}`;
    let state = loadState();
    let activeTab = "catalog";
    const cursors = { catalog: 0, calibration: 0, evidence: 0 };

    function el(id) { return document.getElementById(id); }
    function safe(value) {
      return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
      })[char]);
    }
    function emptyState() {
      return {
        version: 1,
        catalog: {},
        calibration: {},
        evidence: {},
        reviewerId: "",
        auditorId: ""
      };
    }
    function loadState() {
      try {
        return { ...emptyState(), ...JSON.parse(localStorage.getItem(storageKey) || "{}") };
      } catch {
        return emptyState();
      }
    }
    function saveState() {
      localStorage.setItem(storageKey, JSON.stringify(state));
    }
    function rowId(tab, row) { return String(row[tabSpec[tab].id] || ""); }
    function patchFor(tab, row) {
      const id = rowId(tab, row);
      if (!state[tab][id]) state[tab][id] = {};
      return state[tab][id];
    }
    function merged(tab, row) { return { ...row, ...(state[tab][rowId(tab, row)] || {}) }; }
    function isDone(tab, row) {
      const value = merged(tab, row);
      if (tab === "catalog") return value.validado_catalogo === true;
      if (tab === "calibration") return Boolean(value.decisao_calibracao);
      return Boolean(value.decisao_revisor && value.decisao_revisor !== "pendente");
    }
    function searchBlob(row) {
      return Object.values(row).join(" ").toLocaleLowerCase("pt-BR");
    }
    function filteredRows(tab) {
      const search = el("search").value.trim().toLocaleLowerCase("pt-BR");
      const status = el("status-filter").value;
      const section = el("section-filter").value;
      const minScore = Number(el("score-filter").value || 0);
      return datasets[tab].filter(original => {
        const row = merged(tab, original);
        if (search && !searchBlob(row).includes(search)) return false;
        if (status === "done" && !isDone(tab, original)) return false;
        if (status === "pending" && isDone(tab, original)) return false;
        if (section !== "all" && row.secao_portal !== section) return false;
        if (tab !== "catalog" && Number(row.score || 0) < minScore) return false;
        return true;
      });
    }
    function progressFor(tab) {
      const total = datasets[tab].length;
      const done = datasets[tab].filter(row => isDone(tab, row)).length;
      return { total, done, pending: total - done, percent: total ? Math.round(done * 100 / total) : 0 };
    }
    function badges(values, extra = "") {
      return String(values || "").split("|").filter(Boolean)
        .map(value => `<span class="badge ${extra}">${safe(value)}</span>`).join("");
    }
    function field(name, label, value, type = "text") {
      if (type === "textarea") {
        return `<label>${safe(label)}<textarea data-field="${safe(name)}">${safe(value)}</textarea></label>`;
      }
      return `<label>${safe(label)}<input data-field="${safe(name)}" value="${safe(value)}"></label>`;
    }
    function selectField(name, label, value, options) {
      const list = options.map(option => {
        const selected = String(value || "") === option ? " selected" : "";
        return `<option value="${safe(option)}"${selected}>${safe(option || "não preenchido")}</option>`;
      }).join("");
      return `<label>${safe(label)}<select data-field="${safe(name)}">${list}</select></label>`;
    }
    function externalLink(row) {
      const page = row.pagina ? `#page=${encodeURIComponent(row.pagina)}` : "";
      return row.url ? `<a href="${safe(row.url + page)}" target="_blank" rel="noopener">Abrir PDF na página indicada</a>` : "";
    }
    function itemHeader(tab, row, filtered, index) {
      const done = isDone(tab, row);
      return `
        <div class="toolbar">
          <div>
            <span class="badge ${done ? "done" : "pending"}">${done ? "validado" : "pendente"}</span>
            <span class="small muted">Item ${index + 1} de ${filtered.length} nos filtros atuais</span>
          </div>
          <div class="toolbar-actions">
            <button class="button" data-nav="-1">Anterior</button>
            <button class="button" data-nav="1">Próximo</button>
          </div>
        </div>`;
    }
    function renderCatalog(row, filtered, index) {
      const value = merged("catalog", row);
      return itemHeader("catalog", row, filtered, index) + `
        <h2>${safe(value.titulo_inferido || value.titulo_card || value.nome_arquivo)}</h2>
        <p class="muted">${safe(value.nome_arquivo)}</p>
        <div class="meta">
          <div><span>Seção</span>${safe(value.secao_portal)}</div>
          <div><span>Ano URL / documento</span>${safe(value.ano_url)} / ${safe(value.ano_documento)}</div>
          <div><span>Tipo / idioma</span>${safe(value.tipo_documento)} / ${safe(value.idioma_inferido)}</div>
        </div>
        <p>${externalLink(value)}</p>
        <p style="margin-top: 12px"><strong>Motivo automático:</strong> ${safe(row.motivo_status)}</p>
        <div class="actions">
          <button class="button success" data-action="catalog-include">1 · Incluir</button>
          <button class="button danger" data-action="catalog-exclude">2 · Excluir</button>
          <button class="button primary" data-action="catalog-confirm">3 · Confirmar decisão automática</button>
          <button class="button" data-action="catalog-pending">Deixar pendente</button>
        </div>
        <div class="grid">
          ${field("motivo_status", "Justificativa", value.motivo_status, "textarea")}
          ${field("nota_curadoria", "Nota local de curadoria", value.nota_curadoria || "", "textarea")}
        </div>
        <details>
          <summary>Contexto editorial e rastreabilidade</summary>
          <p class="small muted" style="margin-top: 8px">${safe(value.descricao_card)}</p>
          <p class="small muted">Família: ${safe(value.familia_documental_id)} · Card: ${safe(value.card_id)}</p>
          <p class="small muted">URL: ${safe(value.url)}</p>
        </details>`;
    }
    function renderCalibration(row, filtered, index) {
      const value = merged("calibration", row);
      return itemHeader("calibration", row, filtered, index) + `
        <h2>${safe(value.titulo)}</h2>
        <p class="muted">${safe(value.tipo_amostra)} · página ${safe(value.pagina)} · score ${safe(value.score)}</p>
        <div style="margin-top: 10px">${badges(value.tipo_gap)}${badges(value.eixos)}</div>
        <div class="excerpt">${safe(value.trecho)}</div>
        <p class="small">${externalLink(value)}</p>
        <p class="small muted">Termos: ${safe(value.termos_encontrados)} · grupos: ${safe(value.grupos_encontrados)}</p>
        <div class="actions">
          <button class="button success" data-action="calibration-confirm">1 · Gap confirmado</button>
          <button class="button danger" data-action="calibration-false">2 · Falso positivo</button>
          <button class="button warning" data-action="calibration-missing">3 · Termo ausente</button>
          <button class="button" data-action="calibration-pending">Deixar pendente</button>
        </div>
        ${field("nota_calibracao", "Nota de calibração", value.nota_calibracao || "", "textarea")}`;
    }
    function renderEvidence(row, filtered, index) {
      const value = merged("evidence", row);
      return itemHeader("evidence", row, filtered, index) + `
        <h2>${safe(value.titulo)}</h2>
        <p class="muted">${safe(value.secao_portal)} · página ${safe(value.pagina)} · score ${safe(value.score)}</p>
        <div style="margin-top: 10px">${badges(value.tipo_gap)}${badges(value.eixos)}</div>
        <div class="excerpt">${safe(value.trecho)}</div>
        <p class="small">${externalLink(value)}</p>
        <p class="small muted">Termos: ${safe(value.termos_encontrados)} · grupos: ${safe(value.grupos_encontrados)}</p>
        <div class="actions">
          <button class="button success" data-action="evidence-confirm">1 · Confirmar</button>
          <button class="button warning" data-action="evidence-adjust">2 · Ajustar</button>
          <button class="button danger" data-action="evidence-discard">3 · Descartar</button>
          <button class="button" data-action="evidence-pending">Deixar pendente</button>
          <button class="button ${value.uso_relatorio === "sim" ? "primary" : ""}" data-action="evidence-report">R · ${value.uso_relatorio === "sim" ? "Usar no relatório" : "Marcar para relatório"}</button>
        </div>
        <div class="grid">
          ${selectField("tipo_gap_revisado", "Tipo revisado", value.tipo_gap_revisado, ["", "explicito", "implicito", "potencial"])}
          ${field("eixos_revisados", "Eixos revisados", value.eixos_revisados || value.eixos)}
          ${field("hipotese_competencia_revisada", "Hipótese de competência revisada", value.hipotese_competencia_revisada || value.hipotese_competencia)}
          ${field("nota_revisor", "Nota do revisor", value.nota_revisor || "", "textarea")}
        </div>
        <details>
          <summary>Auditoria e conciliação</summary>
          <div class="grid" style="margin-top: 9px">
            ${selectField("auditoria_status", "Status da auditoria", value.auditoria_status, ["pendente", "aprovado", "nao_selecionado"])}
            ${field("auditor_id", "Auditor", value.auditor_id || state.auditorId)}
            ${field("nota_auditoria", "Nota da auditoria", value.nota_auditoria || "", "textarea")}
            ${selectField("conciliacao_status", "Status da conciliação", value.conciliacao_status, ["pendente", "conciliado", "nao_necessaria"])}
            ${field("nota_conciliacao", "Nota da conciliação", value.nota_conciliacao || "", "textarea")}
          </div>
        </details>`;
    }
    function renderReview() {
      const filtered = filteredRows(activeTab);
      if (!filtered.length) {
        el("review").innerHTML = `<div class="empty">Nenhum item corresponde aos filtros atuais.</div>`;
        return;
      }
      cursors[activeTab] = Math.max(0, Math.min(cursors[activeTab], filtered.length - 1));
      const index = cursors[activeTab];
      const row = filtered[index];
      el("review").innerHTML =
        activeTab === "catalog" ? renderCatalog(row, filtered, index) :
        activeTab === "calibration" ? renderCalibration(row, filtered, index) :
        renderEvidence(row, filtered, index);
    }
    function renderTabs() {
      el("tabs").innerHTML = Object.entries(tabSpec).map(([tab, spec]) => {
        const progress = progressFor(tab);
        return `<button class="button tab ${tab === activeTab ? "active" : ""}" data-tab="${tab}">
          ${spec.label} · ${progress.done}/${progress.total}
        </button>`;
      }).join("");
    }
    function renderOverview() {
      const progress = progressFor(activeTab);
      const visible = filteredRows(activeTab).length;
      el("overview").innerHTML = `
        <div class="card metric"><span class="small muted">Total da aba</span><strong>${progress.total}</strong></div>
        <div class="card metric"><span class="small muted">Validados</span><strong>${progress.done}</strong></div>
        <div class="card metric"><span class="small muted">Pendentes</span><strong>${progress.pending}</strong></div>
        <div class="card metric"><span class="small muted">Visíveis com filtros</span><strong>${visible}</strong></div>`;
      el("tab-progress").innerHTML = `
        <div class="progress"><div style="width: ${progress.percent}%"></div></div>
        <p class="small muted">${progress.done} de ${progress.total} · ${progress.percent}%</p>`;
      el("export-name").textContent = tabSpec[activeTab].file;
    }
    function render() {
      renderTabs();
      renderOverview();
      renderReview();
    }
    function move(delta) {
      const filtered = filteredRows(activeTab);
      if (!filtered.length) return;
      cursors[activeTab] = Math.max(0, Math.min(cursors[activeTab] + delta, filtered.length - 1));
      renderReview();
    }
    function applyAction(action) {
      const filtered = filteredRows(activeTab);
      if (!filtered.length) return;
      const row = filtered[cursors[activeTab]];
      const patch = patchFor(activeTab, row);
      const today = new Date().toISOString().slice(0, 10);
      let advance = true;
      if (action === "catalog-include") Object.assign(patch, { status_corpus: "incluir", validado_catalogo: true });
      if (action === "catalog-exclude") Object.assign(patch, { status_corpus: "excluir", validado_catalogo: true });
      if (action === "catalog-confirm") patch.validado_catalogo = true;
      if (action === "catalog-pending") { patch.validado_catalogo = false; advance = false; }
      if (action === "calibration-confirm") patch.decisao_calibracao = "gap_confirmado";
      if (action === "calibration-false") patch.decisao_calibracao = "falso_positivo";
      if (action === "calibration-missing") patch.decisao_calibracao = "termo_ausente";
      if (action === "calibration-pending") { patch.decisao_calibracao = ""; advance = false; }
      if (action === "evidence-confirm") Object.assign(patch, {
        decisao_revisor: "confirmado", revisor_id: patch.revisor_id || state.reviewerId,
        data_revisao: today, auditoria_status: patch.auditoria_status || "nao_selecionado",
        conciliacao_status: patch.conciliacao_status || "nao_necessaria"
      });
      if (action === "evidence-adjust") Object.assign(patch, {
        decisao_revisor: "ajustado", revisor_id: patch.revisor_id || state.reviewerId,
        data_revisao: today, auditoria_status: patch.auditoria_status || "nao_selecionado",
        conciliacao_status: patch.conciliacao_status || "nao_necessaria"
      });
      if (action === "evidence-discard") Object.assign(patch, {
        decisao_revisor: "descartado", revisor_id: patch.revisor_id || state.reviewerId,
        data_revisao: today, auditoria_status: patch.auditoria_status || "nao_selecionado",
        conciliacao_status: patch.conciliacao_status || "nao_necessaria"
      });
      if (action === "evidence-pending") { patch.decisao_revisor = "pendente"; advance = false; }
      if (action === "evidence-report") {
        patch.uso_relatorio = merged(activeTab, row).uso_relatorio === "sim" ? "" : "sim";
        advance = false;
      }
      saveState();
      if (advance && el("status-filter").value !== "pending") move(1); else render();
    }
    function updateField(field, value) {
      const filtered = filteredRows(activeTab);
      if (!filtered.length) return;
      patchFor(activeTab, filtered[cursors[activeTab]])[field] = value;
      saveState();
      renderTabs();
      renderOverview();
    }
    function csvEscape(value) {
      const text = String(value ?? "");
      return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
    }
    function exportCsv() {
      const rows = datasets[activeTab];
      if (!rows.length) return;
      const columns = Object.keys(rows[0]);
      const csv = [
        columns.map(csvEscape).join(","),
        ...rows.map(row => {
          const value = merged(activeTab, row);
          return columns.map(column => csvEscape(value[column])).join(",");
        })
      ].join("\r\n");
      download(tabSpec[activeTab].file, "\ufeff" + csv, "text/csv;charset=utf-8");
    }
    function download(name, content, type) {
      const blob = new Blob([content], { type });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = name;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(link.href);
    }
    function exportBackup() {
      const payload = { metadata, exportedAt: new Date().toISOString(), state };
      download(`checklist-backup-${metadata.run_id}.json`, JSON.stringify(payload, null, 2), "application/json;charset=utf-8");
    }
    async function importBackup(file) {
      if (!file) return;
      const payload = JSON.parse(await file.text());
      if (!payload.state || payload.metadata?.run_id !== metadata.run_id) {
        alert("Backup incompatível com esta linha de base.");
        return;
      }
      state = { ...emptyState(), ...payload.state };
      saveState();
      el("reviewer-id").value = state.reviewerId || "";
      el("auditor-id").value = state.auditorId || "";
      render();
      alert("Backup restaurado.");
    }
    function clearFilters() {
      el("search").value = "";
      el("status-filter").value = "all";
      el("section-filter").value = "all";
      el("score-filter").value = "0";
      cursors[activeTab] = 0;
      render();
    }

    document.addEventListener("click", event => {
      const target = event.target.closest("button");
      if (!target) return;
      if (target.dataset.tab) { activeTab = target.dataset.tab; render(); return; }
      if (target.dataset.nav) { move(Number(target.dataset.nav)); return; }
      if (target.dataset.action) { applyAction(target.dataset.action); return; }
    });
    document.addEventListener("change", event => {
      if (event.target.dataset.field) updateField(event.target.dataset.field, event.target.value);
    });
    ["search", "status-filter", "section-filter", "score-filter"].forEach(id => {
      el(id).addEventListener(id === "search" ? "input" : "change", () => {
        cursors[activeTab] = 0;
        render();
      });
    });
    document.addEventListener("keydown", event => {
      if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
      if (event.key === "ArrowLeft") move(-1);
      if (event.key === "ArrowRight") move(1);
      if (event.key.toLocaleLowerCase() === "r" && activeTab === "evidence") applyAction("evidence-report");
      const actions = activeTab === "catalog"
        ? { "1": "catalog-include", "2": "catalog-exclude", "3": "catalog-confirm" }
        : activeTab === "calibration"
          ? { "1": "calibration-confirm", "2": "calibration-false", "3": "calibration-missing" }
          : { "1": "evidence-confirm", "2": "evidence-adjust", "3": "evidence-discard" };
      if (actions[event.key]) applyAction(actions[event.key]);
    });
    el("clear-filters").addEventListener("click", clearFilters);
    el("export-csv").addEventListener("click", exportCsv);
    el("export-backup").addEventListener("click", exportBackup);
    el("import-backup").addEventListener("click", () => el("backup-file").click());
    el("backup-file").addEventListener("change", event => importBackup(event.target.files[0]));
    el("reviewer-id").addEventListener("input", event => { state.reviewerId = event.target.value; saveState(); });
    el("auditor-id").addEventListener("input", event => { state.auditorId = event.target.value; saveState(); });

    el("run-label").textContent = `${metadata.run_id} · corte editorial ${metadata.as_of}`;
    el("reviewer-id").value = state.reviewerId || "";
    el("auditor-id").value = state.auditorId || "";
    render();
  </script>
</body>
</html>
"""
