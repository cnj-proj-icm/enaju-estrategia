const STATUS = ["Planejamento", "Agendado", "Em execução", "Avaliação", "Concluído"];
const ANNUAL_TARGET = 3000;
const PASSWORD_HASH = "5954b932196b479327a99d637b8c6ccd7b01376595d39cf6fc7e4616bafa0507";
const STAGES = {
  "Planejamento": { color: "#7489ad", progress: 15 },
  "Agendado": { color: "#1768c4", progress: 35 },
  "Em execução": { color: "#00a7d8", progress: 65 },
  "Avaliação": { color: "#446bb3", progress: 85 },
  "Concluído": { color: "#003e8f", progress: 100 }
};
const seedCourses = [
  {id:"c1",process:"13590/2026",name:"Assédio Eleitoral e o seu Enfrentamento",owner:"Igor Caires Machado",start:"2026-07-01",end:"2026-07-23",status:"Agendado",priority:"Alta",format:"Online",capacity:200,next:"Confirmar conteudistas e publicar inscrições"},
  {id:"c2",process:"13116/2026",name:"Curso Projeto Elo",owner:"Janilton Oliveira",start:"2026-07-01",end:"2026-07-23",status:"Agendado",priority:"Média",format:"Híbrido",capacity:120,next:"Validar programação final com parceiros"},
  {id:"c3",process:"18801/2025",name:"Formação Nacional de Intérpretes e Tradutores de Línguas Indígenas do Poder Judiciário (FNITI)",owner:"Fábio Lopes Fernandes Ramos",start:"2026-07-01",end:"2026-08-14",status:"Em execução",priority:"Alta",format:"Híbrido",capacity:80,next:"Acompanhar participação e suporte às turmas"},
  {id:"c4",process:"",name:"Capacitação e atuação de mediadoras indígenas — Justiça, Cidadania e Segurança das Mulheres Indígenas",owner:"A definir",start:"2026-09-14",end:"2026-09-18",status:"Planejamento",priority:"Alta",format:"Presencial",capacity:60,next:"Abrir processo SEI e definir responsável"},
  {id:"c5",process:"10719/2025",name:"Justiça e Direitos da População em Situação de Rua",owner:"Coordenação ENAJU / Comitê PopRuaJud",start:"2026-10-05",end:"2026-10-09",status:"Planejamento",priority:"Alta",format:"Online",capacity:300,next:"Compatibilizar agenda dos 10 formadores e definir datas",hours:20,readiness:82,source:"SEI_10719_2025.pdf",description:"Formação crítica, intersetorial e interdisciplinar para fortalecer a atuação do sistema de justiça na promoção dos direitos das pessoas em situação de rua.",audience:"Magistrados, servidores, equipes técnicas, comitês e equipes intersetoriais do sistema de justiça.",focalPoints:"Antonio Araújo · Coordenação do Comitê PopRuaJud",goal:"10 módulos síncronos de 2 horas",milestones:["Projeto pedagógico validado","10 módulos e metodologias definidos","10 responsáveis pela instrução indicados","Início recomendado para 2026","Datas e agenda dos formadores pendentes"],modules:["Marco normativo e Política PopRua","Intersetorialidade e atuação integrada","Acesso à documentação e ao Judiciário","Escuta qualificada e atuação restaurativa","Aporofobia e discriminação estrutural","Violência institucional e arquitetura hostil","Fluxos de atenção judicial","Crise climática, saúde e sobrevivência","Infância e pessoas com deficiência","Plano de ação e boas práticas"]},
  {id:"c6",process:"03938/2026",name:"Trilha Nacional de Formação — Programa Justiça pela Terra",owner:"Fábio Lopes F. Ramos / Rossilany M. Mota",start:"2026-07-01",end:"2026-12-18",status:"Planejamento",priority:"Alta",format:"A definir",capacity:2000,next:"Definir carga horária, modalidade e instrutores com a CNSF",hours:0,readiness:38,source:"SEI_03938_2026.pdf",description:"Trilha nacional de formação especializada para atuação em conflitos fundiários complexos, voltada à uniformização de práticas e à qualificação da prestação jurisdicional.",audience:"Magistrados, servidores e agentes públicos de todos os tribunais.",focalPoints:"Fábio Lopes Fernandes Ramos · Rossilany Marques Mota",goal:"2.000 agentes e adesão de 100% dos tribunais no primeiro ciclo",milestones:["Pontos focais ENAJU indicados","Definição do plano pedagógico: jun–jul/2026","Ampliação da trilha: jun–dez/2026","Carga horária pendente","Modalidade pendente","Instrutores devem ser indicados com prioridade"],modules:[]}
];
const savedCourses = JSON.parse(localStorage.getItem("enaju-courses") || "null");
let courses = savedCourses || seedCourses;
let outlookEvents = [];
let planActions = [];
let strategicAffinity = {macrochallenges:[],connections:[]};
let selectedMacro = "01";
// Enriquece versões já salvas no navegador com os dados oficiais extraídos dos PDFs.
["10719/2025","03938/2026"].forEach(process=>{
  const official=seedCourses.find(c=>c.process===process);
  const index=courses.findIndex(c=>c.process===process || (process==="10719/2025"&&c.name.includes("População em Situação de Rua")) || (process==="03938/2026"&&c.name.includes("Justiça pela Terra")));
  if(index>=0) courses[index]={...courses[index],...official,id:courses[index].id};
  else courses.push({...official});
});
let currentView = "overview";

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
const fmtDate = value => value ? new Intl.DateTimeFormat("pt-BR",{day:"2-digit",month:"short",timeZone:"UTC"}).format(new Date(value+"T00:00:00Z")).replace(".","") : "A definir";
const initials = name => name.split(" ").filter(Boolean).slice(0,2).map(v=>v[0]).join("").toUpperCase();
const statusClass = s => "s-"+s.toLowerCase().replace("em ","").normalize("NFD").replace(/[\u0300-\u036f]/g,"");
const save = () => localStorage.setItem("enaju-courses", JSON.stringify(courses));

const icons = {
  grid:'<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
  calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
  book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5z"/><path d="M4 6.5v13"/>',
  layers:'<path d="m12 2 9 5-9 5-9-5z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/>',
  chart:'<path d="M3 3v18h18"/><path d="m7 16 4-5 4 3 5-8"/>',
  search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/>',
  menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
  users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  check:'<path d="m5 12 4 4L19 6"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  alert:'<path d="M10.3 2.9 1.8 17a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 2.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
  download:'<path d="M12 3v12m0 0 5-5m-5 5-5-5"/><path d="M5 21h14"/>',
  target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>'
  ,network:'<circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="m8 7 8 0M7 8l4 8m6-8-4 8"/>'
};
function renderIcons(){ $$("[data-icon]").forEach(el => el.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true">${icons[el.dataset.icon]||icons.grid}</svg>`); }

function metrics(){
  const total=courses.length, scheduled=courses.filter(c=>c.status==="Agendado").length, active=courses.filter(c=>c.status==="Em execução").length;
  const capacity=courses.reduce((a,c)=>a+(+c.capacity||0),0);
  return [
    {label:"Ações na carteira",value:total,note:"ciclo de 2026",icon:"book",tone:"green",trend:"+3 previstas"},
    {label:"Datas confirmadas",value:scheduled,note:`${Math.round(scheduled/Math.max(total,1)*100)}% da carteira`,icon:"calendar",tone:"purple",trend:"agenda"},
    {label:"Em execução",value:active,note:"acompanhamento ativo",icon:"clock",tone:"orange",trend:"agora"},
    {label:"Vagas planejadas",value:capacity.toLocaleString("pt-BR"),note:`meta anual: ${ANNUAL_TARGET.toLocaleString("pt-BR")}`,icon:"users",tone:"blue",trend:`${Math.round(capacity/ANNUAL_TARGET*100)}%`}
  ];
}
function renderOverview(){
  $("#cycleSummary").textContent=`${courses.length} ações na carteira`;
  const today=new Date();today.setHours(0,0,0,0);
  const agendaSource=outlookEvents.length?outlookEvents.map(e=>({name:e.subject,start:e.start?.slice(0,10),category:e.category,process:e.courseProcess})):courses.map(c=>({name:c.name,start:c.start,category:c.status,process:c.process}));
  const deadlines=agendaSource.filter(item=>item.start&&new Date(item.start+"T00:00:00")>=today).sort((a,b)=>a.start.localeCompare(b.start)).slice(0,3);
  $("#deadlineList").innerHTML=deadlines.length?deadlines.map((item,index)=>{const date=new Date(item.start+"T00:00:00"),days=Math.ceil((date-today)/86400000);return `<article class="deadline-item ${index===0?"nearest":""}"><div class="deadline-date"><strong>${String(date.getDate()).padStart(2,"0")}</strong><span>${date.toLocaleDateString("pt-BR",{month:"short"}).replace(".","").toUpperCase()}</span></div><div><h4>${esc(item.name)}</h4><p>${item.process?"SEI "+esc(item.process)+" · ":""}${esc(item.category||"Agenda ENAJU")}</p></div><span class="countdown">${days===0?"Hoje":days===1?"Amanhã":`em ${days} dias`}</span></article>`}).join(""):'<div class="empty">Nenhum compromisso futuro registrado.</div>';
  const pending=courses.filter(c=>c.status!=="Concluído"&&(c.next||c.owner==="A definir"||!c.process)).sort((a,b)=>(a.priority==="Alta"?-1:1)-(b.priority==="Alta"?-1:1));
  $("#pendingCount").textContent=pending.length;$("#pendingPreview").innerHTML=pending.slice(0,3).map(c=>`<article><span class="pending-level ${c.priority==="Alta"?"high":""}"></span><div><h4>${esc(c.name)}</h4><p>${esc(c.next||(c.owner==="A definir"?"Definir responsável":"Registrar próximo passo"))}</p></div><span>${c.priority}</span></article>`).join("")||'<div class="empty">Nenhuma pendência aberta.</div>';
  $("#kpiGrid").innerHTML=metrics().map(m=>`<article class="kpi-card"><span class="kpi-icon ${m.tone}"><span class="icon" data-icon="${m.icon}"></span></span><div><p>${m.label}</p><strong>${m.value}</strong><small>${m.note}</small></div><span class="trend">${m.trend}</span></article>`).join("");
  const counts=Object.fromEntries(STATUS.map(s=>[s,courses.filter(c=>c.status===s).length]));
  const avg=Math.round(courses.reduce((a,c)=>a+STAGES[c.status].progress,0)/Math.max(courses.length,1));
  $("#donutValue").textContent=avg+"%"; $("#donutChart").style.background=`conic-gradient(var(--green) 0 ${avg}%, var(--lime) ${avg}% ${Math.min(avg+12,100)}%, #e8eef6 ${Math.min(avg+12,100)}%)`;
  $("#stageLegend").innerHTML=STATUS.map(s=>`<div class="legend-row"><i style="background:${STAGES[s].color}"></i><span>${s}</span><strong>${counts[s]}</strong></div>`).join("");
  const attention=courses.filter(c=>!c.process || c.owner==="A definir" || c.priority==="Alta"&&c.status==="Planejamento").slice(0,3);
  $("#alertCount").textContent=`${attention.length} alerta${attention.length===1?"":"s"}`;
  $("#attentionList").innerHTML=attention.length?attention.map(c=>`<div class="attention-item"><span class="att-icon"><span class="icon" data-icon="alert"></span></span><div><strong>${esc(c.name)}</strong><span>${!c.process?"Processo SEI pendente":c.owner==="A definir"?"Responsável não definido":"Prioridade alta em planejamento"}</span></div><time>${fmtDate(c.start)}</time></div>`).join(""):`<div class="empty">Nenhum ponto de atenção.</div>`;
  const upcoming=[...courses].filter(c=>c.start).sort((a,b)=>a.start.localeCompare(b.start)).slice(0,4);
  $("#upcomingList").innerHTML=upcoming.map(c=>{const d=new Date(c.start+"T00:00:00Z");return `<div class="upcoming-item"><div class="date-chip"><strong>${String(d.getUTCDate()).padStart(2,"0")}</strong><span>${d.toLocaleDateString("pt-BR",{month:"short",timeZone:"UTC"}).replace(".","").toUpperCase()}</span></div><div><h4>${esc(c.name)}</h4><p>${esc(c.format)} · ${esc(c.owner)}</p></div><span class="status-pill ${statusClass(c.status)}">${c.status}</span></div>`}).join("");
  const capacity=courses.reduce((a,c)=>a+(+c.capacity||0),0), pct=Math.min(Math.round(capacity/ANNUAL_TARGET*100),100);
  $("#capacityTotal").textContent=capacity.toLocaleString("pt-BR");$("#capacityProgress").style.width=pct+"%";$("#capacityPercent").textContent=pct+"%";$("#capacityRemaining").textContent=`${Math.max(ANNUAL_TARGET-capacity,0).toLocaleString("pt-BR")} vagas restantes`;$("#courseCountMini").textContent=courses.length;$("#confirmedCount").textContent=courses.filter(c=>c.status!=="Planejamento").length;
  const dossiers=courses.filter(c=>c.source);
  $("#dossierGrid").innerHTML=dossiers.map(c=>`<article class="dossier-card" data-id="${c.id}">
    <div class="dossier-top"><span class="process-chip">SEI ${esc(c.process)}</span><span class="readiness-ring" style="--ready:${c.readiness}"><b>${c.readiness}%</b></span></div>
    <h4>${esc(c.name)}</h4><p>${esc(c.description)}</p>
    <div class="dossier-facts"><span><b>${c.hours||"—"}${c.hours?"h":""}</b>Carga horária</span><span><b>${(+c.capacity).toLocaleString("pt-BR")}</b>Meta de alcance</span><span><b>${c.modules?.length||"—"}</b>Módulos</span></div>
    <footer><span><i class="dot ${c.readiness>60?"execution":"planned"}"></i>${c.readiness>60?"Projeto estruturado":"Definições pendentes"}</span><button>Ver dossiê →</button></footer>
  </article>`).join("");
  $$(".dossier-card").forEach(el=>el.onclick=()=>openDrawer(el.dataset.id));
  renderIcons();
}
function renderAgenda(){
  const months=["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"];
  $("#yearGrid").innerHTML=months.map((m,i)=>{
    const events=outlookEvents.filter(e=>e.start&&new Date(e.start).getMonth()===i);
    const linkedProcesses=new Set(events.map(e=>e.courseProcess).filter(Boolean));
    const planned=courses.filter(c=>c.start&&!linkedProcesses.has(c.process)&&new Date(c.start+"T00:00:00Z").getUTCMonth()===i).map(c=>({...c,subject:c.name,category:c.status,courseId:c.id}));
    const list=[...events.map(e=>({...e,courseId:courses.find(c=>c.process&&c.process===e.courseProcess)?.id})),...planned].sort((a,b)=>a.start.localeCompare(b.start));
    return `<div class="month-card ${i===new Date().getMonth()?"current":""}"><h4>${m}<span>${list.length||""}</span></h4>${list.map(event=>`<div class="month-event ${event.category==="CONCLUÍDO"?"scheduled":event.category==="HOJE"?"execution":""}" ${event.courseId?`data-id="${event.courseId}"`:""}><strong>${esc(event.subject)}</strong><span>${fmtDate(event.start.slice(0,10))} · ${esc(event.category||"Planejado")}</span></div>`).join("")||'<div class="empty">—</div>'}</div>`;
  }).join("");
  $$(".month-event[data-id]").forEach(el=>el.onclick=()=>openDrawer(el.dataset.id));
}
function renderCourses(){
  $("#statusFilter").innerHTML='<option value="">Todos os status</option>'+STATUS.map(s=>`<option>${s}</option>`).join("");
  filterCourses();
}
function filterCourses(){
  const q=($("#courseSearch")?.value||$("#globalSearch").value).toLowerCase(), status=$("#statusFilter")?.value||"", priority=$("#priorityFilter")?.value||"";
  const list=courses.filter(c=>(c.name+" "+c.process+" "+c.owner).toLowerCase().includes(q)&&(!status||c.status===status)&&(!priority||c.priority===priority));
  $("#courseTable").innerHTML=list.map(c=>{const progress=Number.isFinite(c.percentComplete)?c.percentComplete:STAGES[c.status].progress;return `<tr><td><strong>${esc(c.name)}</strong><small>${c.process?"SEI "+esc(c.process):"Processo pendente"} · ${esc(c.format)}</small></td><td><div class="owner-cell"><span class="owner-dot">${initials(c.owner)}</span><span>${esc(c.owner)}</span></div></td><td>${fmtDate(c.start)} — ${fmtDate(c.end)}</td><td><span class="status-pill ${statusClass(c.status)}">${c.status}</span></td><td><div class="progress-cell"><div class="tiny-bar"><i style="width:${progress}%"></i></div><span>${progress}%</span></div></td><td><button class="row-action" data-view-course="${c.id}" title="Consultar">Ver</button></td></tr>`}).join("")||'<tr><td colspan="6"><div class="empty">Nenhuma ação encontrada.</div></td></tr>';
  $("#tableCount").textContent=`${list.length} ${list.length===1?"ação":"ações"}`;
  $$("[data-view-course]").forEach(btn=>btn.onclick=()=>openDrawer(btn.dataset.viewCourse));
}
function renderPipeline(){
  $("#pipelineBoard").innerHTML=STATUS.map(s=>{const list=courses.filter(c=>c.status===s);return `<section class="pipeline-column"><div class="pipeline-head"><strong>${s}</strong><span>${list.length}</span></div>${list.map(c=>`<article class="pipeline-card" data-id="${c.id}"><div class="priority-line ${c.priority}"></div><h4>${esc(c.name)}</h4><p>${c.process?"SEI "+esc(c.process):"Sem processo SEI"}</p><footer><span class="owner-dot">${initials(c.owner)}</span><span>${fmtDate(c.start)}</span></footer></article>`).join("")}</section>`}).join("");
  $$(".pipeline-card").forEach(el=>el.onclick=()=>openDrawer(el.dataset.id));
}
function renderReports(){
  const avg=Math.round(courses.reduce((a,c)=>a+STAGES[c.status].progress,0)/Math.max(courses.length,1));
  $("#executionIndex").textContent=avg+"%";$("#executionLine").style.width=avg+"%";
  const owners={};courses.forEach(c=>owners[c.owner]=(owners[c.owner]||0)+1); const max=Math.max(...Object.values(owners),1);
  $("#ownerChart").innerHTML=Object.entries(owners).sort((a,b)=>b[1]-a[1]).map(([n,v])=>`<div class="bar-row"><span>${esc(n)}</span><div class="bar-track"><i style="width:${v/max*100}%"></i></div><b>${v}</b></div>`).join("");
  const formats={};courses.forEach(c=>formats[c.format]=(formats[c.format]||0)+1);
  $("#formatStats").innerHTML=Object.entries(formats).map(([n,v])=>`<div class="stat-row"><span>${n}</span><b>${v} · ${Math.round(v/courses.length*100)}%</b><div class="stat-bar"><i style="width:${v/courses.length*100}%"></i></div></div>`).join("");
  const quality=[["Com processo SEI",courses.filter(c=>c.process).length],["Com responsável",courses.filter(c=>c.owner!=="A definir").length],["Com cronograma",courses.filter(c=>c.start&&c.end).length],["Com próximo passo",courses.filter(c=>c.next).length]];
  $("#qualityList").innerHTML=quality.map(([n,v])=>`<div class="quality-row"><span>${n}</span><b>${Math.round(v/courses.length*100)}%</b><div class="stat-bar"><i style="width:${v/courses.length*100}%"></i></div></div>`).join("");
}
function renderPlan(filter=""){
  if(!planActions.length){$("#planKpis").innerHTML="";$("#planList").innerHTML='<div class="panel empty">Plano ainda não carregado.</div>';return}
  const direct=planActions.filter(a=>a.axis.startsWith("Eixo")).length,planner=planActions.filter(a=>a.hasPlanner).length,outlook=planActions.filter(a=>a.hasOutlook).length;
  $("#planKpis").innerHTML=[
    [planActions.length,"Ações comprometidas","target"],[direct,"Ligadas ao Plano de Gestão","chart"],[planner,"Com tarefa no Planner","layers"],[outlook,"Com agenda no Outlook","calendar"]
  ].map(([value,label,icon])=>`<article class="plan-kpi"><span class="icon" data-icon="${icon}"></span><div><strong>${value}</strong><p>${label}</p></div></article>`).join("");
  const list=planActions.filter(a=>!filter||(filter==="Eixo"&&a.axis.startsWith("Eixo"))||(filter==="Planner"&&a.hasPlanner)||(filter==="Outlook"&&a.hasOutlook)||(filter==="Pendente"&&!a.hasPlanner&&!a.hasOutlook));
  $("#planList").innerHTML=list.map(a=>`<article class="plan-action">
    <div class="plan-order">${String(a.order).padStart(2,"0")}</div>
    <div class="plan-main"><div class="plan-title"><h3>${esc(a.name)}</h3><span>${esc(a.axis)}</span></div><p>${esc(a.decision)}</p>
      <div class="plan-links">${a.hasPlanner?`<span class="source-chip planner">Planner · ${a.plannerTaskIds.length} tarefa${a.plannerTaskIds.length>1?"s":""}</span>`:""}${a.hasOutlook?`<span class="source-chip outlook">Outlook · ${a.outlookEventIds.length} evento${a.outlookEventIds.length>1?"s":""}</span>`:""}${!a.hasPlanner&&!a.hasOutlook?'<span class="source-chip pending">Sem registro operacional</span>':""}</div>
    </div>
    <div class="coverage ${a.coverageClass}"><strong>${a.coverage}%</strong><span>cobertura</span></div>
  </article>`).join("");
  renderIcons();
}
function renderAffinity(){
  const macros=strategicAffinity.macrochallenges||[],connections=strategicAffinity.connections||[];if(!macros.length){$("#connectionMap").innerHTML='<div class="empty">Base estratégica ainda não carregada.</div>';return}
  const objectives=strategicAffinity.objectives||[],objectiveLinks=strategicAffinity.objectiveConnections||[];
  const primary=connections.filter(c=>c.rank===1),high=connections.filter(c=>c.strength==="Alta").length;
  const approved=connections.filter(c=>c.approved).length;$("#approvalTotal").textContent=`${approved} vínculos aprovados`;
  $("#affinityKpis").innerHTML=[[macros.length,"Macrodesafios"],[new Set(connections.map(c=>c.courseOrder)).size,"Cursos conectados"],[approved,"Relações aprovadas"],[high,"Afinidades altas"]].map(([v,l])=>`<article><strong>${v}</strong><span>${l}</span></article>`).join("");
  const objectiveCounts=objectives.map(o=>({...o,count:objectiveLinks.filter(link=>link.objectiveCode===o.code).length,courses:objectiveLinks.filter(link=>link.objectiveCode===o.code).map(link=>link.courseName)})),maxCount=Math.max(...objectiveCounts.map(o=>o.count),1);
  $("#objectiveChart").innerHTML=objectiveCounts.map(o=>`<article class="${o.count?"has-courses":"no-courses"}" title="${esc(o.courses.join(" · ")||"Nenhum curso vinculado")}"><span class="objective-code">${o.code}</span><div><p>${esc(o.name)}</p><div class="objective-track"><i style="width:${o.count/maxCount*100}%"></i></div></div><strong>${o.count}</strong></article>`).join("");
  $("#objectiveTable").innerHTML=objectiveLinks.sort((a,b)=>a.courseOrder-b.courseOrder).map(link=>`<tr><td><strong>${esc(link.courseName)}</strong><small>Curso ${String(link.courseOrder).padStart(2,"0")}</small></td><td><span class="macro-code">${link.objectiveCode}</span>${esc(link.objectiveName)}</td><td><b>${link.score}%</b><span class="approved-chip"><span class="icon" data-icon="check"></span>Aprovado</span></td><td>${link.matchedTerms.map(term=>`<span class="term-chip">${esc(term)}</span>`).join("")}</td></tr>`).join("");
  $("#macroList").innerHTML=macros.map(m=>{const count=connections.filter(c=>c.macroCode===m.code).length;return `<button class="${m.code===selectedMacro?"active":""}" data-macro="${m.code}"><b>${m.code}</b><span>${esc(m.name)}</span><i>${count}</i></button>`}).join("");
  const macro=macros.find(m=>m.code===selectedMacro)||macros[0],links=connections.filter(c=>c.macroCode===macro.code).sort((a,b)=>b.score-a.score);
  $("#connectionHead").innerHTML=`<div class="macro-orbit"><span>${macro.code}</span></div><div><p>MACRODESAFIO SELECIONADO</p><h3>${esc(macro.name)}</h3><span>${macro.projectCount} projetos estratégicos cadastrados em 2026</span></div>`;
  $("#connectionMap").innerHTML=links.length?links.map((link,i)=>`<article class="course-connection" style="--delay:${i*35}ms"><span class="connector"></span><div><p>CURSO ${String(link.courseOrder).padStart(2,"0")} · ${link.approved?"APROVADO":"EM ANÁLISE"}</p><h4>${esc(link.courseName)}</h4><div>${link.matchedTerms.map(t=>`<span>${esc(t)}</span>`).join("")}</div></div><strong>${link.score}%<small>${link.strength}</small></strong></article>`).join(""):'<div class="empty">Nenhum vínculo lexical identificado para este macrodesafio.</div>';
  $("#affinityTable").innerHTML=primary.sort((a,b)=>a.courseOrder-b.courseOrder).map(c=>`<tr><td><strong>${esc(c.courseName)}</strong><small>Curso ${String(c.courseOrder).padStart(2,"0")}</small></td><td><span class="macro-code">${c.macroCode}</span>${esc(c.macroName)}</td><td><div class="affinity-score"><i style="width:${c.score}%"></i></div><b>${c.score}% · ${c.strength}</b></td><td>${c.matchedTerms.map(t=>`<span class="term-chip">${esc(t)}</span>`).join("")}</td><td><span class="approved-chip"><span class="icon" data-icon="check"></span>Aprovado</span></td></tr>`).join("");
  $$("[data-macro]").forEach(button=>button.onclick=()=>{selectedMacro=button.dataset.macro;renderAffinity()});renderIcons();
}
function renderAll(){renderOverview();renderAgenda();renderCourses();renderPipeline();renderReports();renderPlan($("[data-plan-filter].active")?.dataset.planFilter||"");renderAffinity()}
function switchView(view){
  currentView=view; $$(".view").forEach(v=>v.classList.toggle("active",v.id===`view-${view}`));$$(".nav-item").forEach(v=>v.classList.toggle("active",v.dataset.view===view));
  const titles={overview:"Visão geral",agenda:"Agenda",courses:"Cursos",pipeline:"Pipeline",reports:"Indicadores",plan:"Plano 2026",affinity:"Conexões PJ"};$("#pageTitle").textContent=titles[view];$("#sidebar").classList.remove("open");window.scrollTo(0,0);
}
function openDrawer(id){
  const c=courses.find(x=>x.id===id); if(!c)return; $("#drawerTitle").textContent=c.name;$("#courseDrawer").dataset.courseId=c.id;
  $("#readonlySummary").innerHTML=`<div class="readonly-grid"><span><b>Processo</b>${c.process?"SEI "+esc(c.process):"A definir"}</span><span><b>Status</b><i class="status-pill ${statusClass(c.status)}">${c.status}</i></span><span><b>Responsável</b>${esc(c.owner)}</span><span><b>Período</b>${fmtDate(c.start)} — ${fmtDate(c.end)}</span><span><b>Modalidade</b>${esc(c.format)}</span><span><b>Vagas</b>${(+c.capacity||0).toLocaleString("pt-BR")}</span></div><div class="next-step"><b>Próximo passo</b><p>${esc(c.next||"Não informado")}</p></div>`;
  const notes=JSON.parse(localStorage.getItem("enaju-notes")||"{}");$("#courseNotes").value=notes[c.id]||"";
  const intel=$("#processIntelligence");intel.hidden=!c?.source;
  if(c?.source){$("#intelTitle").textContent=`SEI ${c.process}`;$("#intelReadiness").textContent=`${c.readiness}% pronto`;$("#intelDescription").textContent=c.description;$("#intelMeta").innerHTML=`<span><b>Público-alvo</b>${esc(c.audience)}</span><span><b>Meta / desenho</b>${esc(c.goal)}</span><span><b>Pontos focais</b>${esc(c.focalPoints)}</span>`;$("#intelMilestones").innerHTML=c.milestones.map((m,i)=>`<label><input type="checkbox" disabled ${i<Math.floor(c.milestones.length*c.readiness/100)?"checked":""}><span>${esc(m)}</span></label>`).join("");$("#modulesBlock").hidden=!c.modules?.length;$("#intelModules").innerHTML=(c.modules||[]).map((m,i)=>`<span><b>${String(i+1).padStart(2,"0")}</b>${esc(m)}</span>`).join("");$("#intelPdf").href=`Agendar/${c.source}`;}
  $("#courseDrawer").classList.add("open");$("#overlay").classList.add("open");$("#courseDrawer").setAttribute("aria-hidden","false");
}
function closeDrawer(){$("#courseDrawer").classList.remove("open");$("#overlay").classList.remove("open");$("#courseDrawer").setAttribute("aria-hidden","true")}
function toast(msg){$("#toastText").textContent=msg;$("#toast").classList.add("show");setTimeout(()=>$("#toast").classList.remove("show"),2300)}
async function sha256(value){const data=new TextEncoder().encode(value);const digest=await crypto.subtle.digest("SHA-256",data);return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,"0")).join("")}
function unlock(){sessionStorage.setItem("enaju-auth","ok");$("#loginGate").classList.add("unlocked");document.body.classList.remove("locked")}
function initLogin(){
  if(sessionStorage.getItem("enaju-auth")==="ok"){unlock();return}
  document.body.classList.add("locked");
  $("#loginForm").onsubmit=async e=>{e.preventDefault();const validUser=$("#loginUser").value.trim().toLowerCase()==="admin";const validPassword=await sha256($("#loginPassword").value)===PASSWORD_HASH;if(validUser&&validPassword){unlock();$("#loginError").textContent=""}else{$("#loginError").textContent="Usuário ou senha inválidos.";$("#loginPassword").select()}};
}
function exportCSV(){
  const rows=[["Processo","Ação educacional","Responsável","Início","Fim","Status","Prioridade","Modalidade","Vagas","Próximo passo"],...courses.map(c=>[c.process,c.name,c.owner,c.start,c.end,c.status,c.priority,c.format,c.capacity,c.next])];
  const csv="\ufeff"+rows.map(r=>r.map(v=>`"${String(v??"").replace(/"/g,'""')}"`).join(";")).join("\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));a.download="agenda-cursos-enaju.csv";a.click();URL.revokeObjectURL(a.href);toast("Planilha exportada");
}
async function loadExternalData(){
  try{
    let calendar,planner,plan,affinity;
    if(location.protocol==="file:"&&window.ENAJU_DATA){
      ({calendar,planner,plan,affinity}=window.ENAJU_DATA);
    }else{
      const [calendarResponse,plannerResponse,planResponse,affinityResponse]=await Promise.all([fetch("data/outlook-calendar.json",{cache:"no-store"}),fetch("data/planner.json",{cache:"no-store"}),fetch("data/capacitation-plan.json",{cache:"no-store"}),fetch("data/strategic-affinity.json",{cache:"no-store"})]);
      if(!calendarResponse.ok||!plannerResponse.ok||!planResponse.ok||!affinityResponse.ok)throw new Error("bases indisponíveis");
      [calendar,planner,plan,affinity]=await Promise.all([calendarResponse.json(),plannerResponse.json(),planResponse.json(),affinityResponse.json()]);
    }
    outlookEvents=calendar.events||[];planActions=plan.actions||[];strategicAffinity=affinity;
    planner.tasks.forEach(task=>{let c=courses.find(item=>(task.courseProcess&&item.process===task.courseProcess)||item.plannerTaskId===task.id);if(!c){c={id:task.id,process:task.courseProcess||"",name:task.courseName||task.title,owner:task.owner||"A definir",start:task.start||"",end:task.end||"",status:task.dashboardStatus||"Planejamento",priority:task.priority||"Média",format:"A definir",capacity:0,next:task.nextAction||"",plannerTaskId:task.id,percentComplete:task.percentComplete};courses.push(c)}else{c.owner=task.owner||c.owner;c.next=task.nextAction||c.next;c.start=task.start||c.start;c.end=task.end||c.end;c.plannerTaskId=task.id;c.percentComplete=task.percentComplete;if(task.dashboardStatus&&STATUS.includes(task.dashboardStatus))c.status=task.dashboardStatus}});
    const dates=[calendar.updatedAt,planner.updatedAt].filter(Boolean).sort();if(dates.length)$("#lastSyncLabel").textContent=`Sincronizado em ${new Intl.DateTimeFormat("pt-BR",{dateStyle:"short",timeStyle:"short"}).format(new Date(dates.at(-1)))}`;
    renderAll();
  }catch(error){
    if(window.ENAJU_DATA){const {calendar,planner,plan,affinity}=window.ENAJU_DATA;outlookEvents=calendar.events||[];planActions=plan.actions||[];strategicAffinity=affinity;renderAll();$("#lastSyncLabel").textContent="Usando base portátil"}
    else $("#lastSyncLabel").textContent="Base de dados indisponível";
  }
}
function init(){
  initLogin();
  $("#todayLabel").textContent=new Intl.DateTimeFormat("pt-BR",{weekday:"long",day:"2-digit",month:"long",year:"numeric"}).format(new Date()).toUpperCase();
  renderAll();
  $$(".nav-item").forEach(b=>b.onclick=()=>switchView(b.dataset.view));$$("[data-goto]").forEach(b=>b.onclick=()=>switchView(b.dataset.goto));$("#closeDrawer").onclick=$("#cancelDrawer").onclick=$("#overlay").onclick=closeDrawer;$("#menuBtn").onclick=()=>$("#sidebar").classList.toggle("open");
  $("#courseSearch").oninput=filterCourses;$("#statusFilter").onchange=filterCourses;$("#priorityFilter").onchange=filterCourses;
  $("#globalSearch").oninput=e=>{if(e.target.value){switchView("courses");$("#courseSearch").value=e.target.value;filterCourses()}};
  document.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key==="k"){e.preventDefault();$("#globalSearch").focus()}if(e.key==="Escape")closeDrawer()});
  $("#saveNotes").onclick=()=>{const id=$("#courseDrawer").dataset.courseId;if(!id)return;const notes=JSON.parse(localStorage.getItem("enaju-notes")||"{}");notes[id]=$("#courseNotes").value.trim();localStorage.setItem("enaju-notes",JSON.stringify(notes));toast("Anotações salvas")};
  $("#exportBtn").onclick=exportCSV;$("#printBtn").onclick=()=>window.print();
  $$("[data-plan-filter]").forEach(button=>button.onclick=()=>{$$("[data-plan-filter]").forEach(b=>b.classList.remove("active"));button.classList.add("active");renderPlan(button.dataset.planFilter)});
  loadExternalData();
}
init();
