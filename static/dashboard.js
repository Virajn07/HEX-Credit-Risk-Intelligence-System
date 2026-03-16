/* =====================================================
GLOBAL CHART STORE
===================================================== */

let charts = {}


/* =====================================================
PORTFOLIO RISK DONUT
===================================================== */

function renderRiskChart(low, medium, high){

const ctx = document.getElementById("riskChart")
if(!ctx) return

if(charts.risk) charts.risk.destroy()

charts.risk = new Chart(ctx,{
type:"doughnut",
data:{
labels:["Low Risk","Medium Risk","High Risk"],
datasets:[{
data:[low,medium,high],
backgroundColor:["#22c55e","#f59e0b","#ef4444"],
borderWidth:0
}]
},
options:{
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{position:"bottom"}}
}
})

}


/* =====================================================
AI RISK RADAR
===================================================== */

function renderRiskRadar(high, medium, low){

const ctx = document.getElementById("riskRadar")
if(!ctx) return

if(charts.radar) charts.radar.destroy()

charts.radar = new Chart(ctx,{
type:"radar",
data:{
labels:[
"High Risk",
"Medium Risk",
"Low Risk",
"Portfolio Stability",
"Customer Quality"
],
datasets:[{
data:[high,medium,low,(low+medium),low],
backgroundColor:"rgba(37,99,235,0.15)",
borderColor:"#2563eb",
pointBackgroundColor:"#2563eb"
}]
},
options:{
responsive:true,
maintainAspectRatio:false,
scales:{r:{beginAtZero:true}}
}
})

}


/* =====================================================
LOAN AMOUNT DISTRIBUTION
===================================================== */

function renderLoanDistribution(data){

const ctx=document.getElementById("loanChart")
if(!ctx || !data) return

if(charts.loan) charts.loan.destroy()

const buckets={
"0-1L":0,
"1-3L":0,
"3-5L":0,
"5-10L":0,
"10L+":0
}

data.forEach(d=>{

const loan=Number(d.y)

if(loan<100000) buckets["0-1L"]++
else if(loan<300000) buckets["1-3L"]++
else if(loan<500000) buckets["3-5L"]++
else if(loan<1000000) buckets["5-10L"]++
else buckets["10L+"]++

})

charts.loan=new Chart(ctx,{
type:"bar",
data:{
labels:Object.keys(buckets),
datasets:[{
data:Object.values(buckets),
backgroundColor:"#2563eb"
}]
},
options:{
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{display:false}},
scales:{y:{beginAtZero:true}}
}
})

}


/* =====================================================
CIBIL SCORE DISTRIBUTION
===================================================== */

function renderCreditDistribution(data){

const ctx=document.getElementById("creditChart")
if(!ctx || !data) return

if(charts.credit) charts.credit.destroy()

const buckets={
"300-500":0,
"500-650":0,
"650-700":0,
"700-750":0,
"750+":0
}

data.forEach(d=>{

const score=Number(d.x)

if(score<500) buckets["300-500"]++
else if(score<650) buckets["500-650"]++
else if(score<700) buckets["650-700"]++
else if(score<750) buckets["700-750"]++
else buckets["750+"]++

})

charts.credit=new Chart(ctx,{
type:"bar",
data:{
labels:Object.keys(buckets),
datasets:[{
data:Object.values(buckets),
backgroundColor:"#22c55e"
}]
},
options:{
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{display:false}},
scales:{y:{beginAtZero:true}}
}
})

}


/* =====================================================
CREDIT SCORE GAUGE
===================================================== */

function renderCreditScore(score){

const ctx=document.getElementById("creditScoreChart")
if(!ctx) return

const numericScore=parseInt(score)

if(isNaN(numericScore)) return

if(charts.creditGauge) charts.creditGauge.destroy()

let color="#16a34a"

if(numericScore<650) color="#dc2626"
else if(numericScore<700) color="#f59e0b"

charts.creditGauge=new Chart(ctx,{
type:"doughnut",
data:{
datasets:[{
data:[numericScore,900-numericScore],
backgroundColor:[color,"#e5e7eb"],
borderWidth:0
}]
},
options:{
rotation:-90,
circumference:180,
cutout:"70%",
responsive:true,
maintainAspectRatio:false,
plugins:{
legend:{display:false},
tooltip:{enabled:false}
}
}
})

}


/* =====================================================
INCOME VS LOAN
===================================================== */

function renderIncomeChart(income,loan){

const ctx=document.getElementById("incomeChart")
if(!ctx) return

if(charts.income) charts.income.destroy()

charts.income=new Chart(ctx,{
type:"bar",
data:{
labels:["Income","Loan"],
datasets:[{
data:[income,loan],
backgroundColor:["#3b82f6","#ef4444"]
}]
},
options:{
responsive:true,
plugins:{legend:{display:false}},
scales:{y:{beginAtZero:true}}
}
})

}


/* =====================================================
EMI BURDEN
===================================================== */

function renderEmiChart(emi,income){

const ctx=document.getElementById("emiChart")
if(!ctx) return

if(charts.emi) charts.emi.destroy()

charts.emi=new Chart(ctx,{
type:"pie",
data:{
labels:["EMI","Remaining"],
datasets:[{
data:[emi,income],
backgroundColor:["#f59e0b","#22c55e"]
}]
},
options:{responsive:true}
})

}


/* =====================================================
TABLE SEARCH
===================================================== */

function searchLoans(){

const input=document.getElementById("searchInput")
if(!input) return

const filter=input.value.toLowerCase()
const rows=document.querySelectorAll("#loanTable tbody tr")

rows.forEach(row=>{
row.style.display=row.innerText.toLowerCase().includes(filter)?"":"none"
})

}


/* =====================================================
RISK FILTER
===================================================== */

function filterRisk(){

const filter=document.getElementById("riskFilter")
if(!filter) return

const value=filter.value
const rows=document.querySelectorAll("#loanTable tbody tr")

rows.forEach(row=>{

if(value==="All") row.style.display=""
else row.style.display=row.classList.contains(value.toLowerCase())?"":"none"

})

}


/* =====================================================
TABLE SORTING
===================================================== */

let sortDirection=true

function sortTable(column){

const table=document.getElementById("loanTable")
if(!table) return

const rows=Array.from(table.rows).slice(1)

sortDirection=!sortDirection

rows.sort((a,b)=>{

let x=a.cells[column].innerText
let y=b.cells[column].innerText

let numX=parseFloat(x)
let numY=parseFloat(y)

if(!isNaN(numX)&&!isNaN(numY))
return sortDirection?numX-numY:numY-numX

return sortDirection?x.localeCompare(y):y.localeCompare(x)

})

rows.forEach(row=>table.appendChild(row))

}


/* =====================================================
PAGINATION
===================================================== */

let currentPage=1
const rowsPerPage=10

function displayPage(){

const rows=document.querySelectorAll("#loanTable tbody tr")
if(rows.length===0) return

const start=(currentPage-1)*rowsPerPage
const end=start+rowsPerPage

rows.forEach((row,index)=>{
row.style.display=(index>=start && index<end)?"":"none"
})

const pageInfo=document.getElementById("pageInfo")
if(pageInfo) pageInfo.innerText="Page "+currentPage

}

function nextPage(){

const rows=document.querySelectorAll("#loanTable tbody tr")
const maxPage=Math.ceil(rows.length/rowsPerPage)

if(currentPage<maxPage){
currentPage++
displayPage()
}

}

function prevPage(){

if(currentPage>1){
currentPage--
displayPage()
}

}


/* =====================================================
AI CHAT
===================================================== */

function sendChat(){

const input=document.getElementById("chatInput")
const chatBox=document.getElementById("chatBox")

if(!input || !chatBox) return

const question=input.value.trim()

if(question==="") return

/* USER MESSAGE */

chatBox.innerHTML+=`
<div class="chat-user">
${question}
</div>
`

input.value=""

/* TYPING ANIMATION */

const typingId="typing_"+Date.now()

chatBox.innerHTML+=`
<div id="${typingId}" class="chat-typing">
AI is typing
<span class="typing-dots">
<span></span><span></span><span></span>
</span>
</div>
`

chatBox.scrollTop=chatBox.scrollHeight


fetch("/ai_chat",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
question:question
})

})

.then(res=>res.json())

.then(data=>{

const typing=document.getElementById(typingId)

if(typing) typing.remove()

let answer=data.answer.replace(/\$/g,"₹")

chatBox.innerHTML+=`
<div class="chat-ai">
${answer}
</div>
`

chatBox.scrollTop=chatBox.scrollHeight

})

.catch(()=>{

const typing=document.getElementById(typingId)

if(typing) typing.remove()

chatBox.innerHTML+=`
<div class="chat-ai">
AI assistant unavailable.
</div>
`

})

}


/* =====================================================
PRESET QUESTIONS
===================================================== */

function askPreset(question){

const input=document.getElementById("chatInput")
if(!input) return

input.value=question
sendChat()

}


/* =====================================================
INITIALIZE PAGE
===================================================== */

document.addEventListener("DOMContentLoaded",()=>{

if(document.getElementById("loanTable")){
displayPage()
}

const rawScore=document.body.dataset.creditScore

if(rawScore){

const score=parseInt(rawScore)

if(!isNaN(score)){
renderCreditScore(score)
}

}

})
function filterStatus(status){

const rows=document.querySelectorAll("#loanTable tbody tr")

rows.forEach(row=>{

const rowStatus=row.children[7].innerText.trim()

if(status==="All"){
row.style.display=""
}
else if(rowStatus===status){
row.style.display=""
}
else{
row.style.display="none"
}

})

}