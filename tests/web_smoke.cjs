"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/i);
assert(match, "Expected standalone browser script");
new vm.Script(match[1]);

const defaults = {
  target:"EGFR", ligand:"EXAMPLE-01", sequence:"MTEYKLVVVG", smiles:"CCO",
  mw:"420", logp:"2.5", tpsa:"65", hbd:"2", hba:"4", rot:"4",
  "task-id":"TASK-1", specimen:"SAMPLE-1", primary:"29.4", secondary:"14.8", descriptor:"NOMINAL"
};
const nodes = new Map();
function element(id) {
  if (!nodes.has(id)) {
    const listeners = {};
    nodes.set(id, {
      value:defaults[id] ?? "", checked:false, hidden:false, disabled:false, textContent:"",
      listeners, addEventListener(type,cb){listeners[type]=cb;},
      checkValidity(){return true;}, setAttribute(name,value){this[name]=value;}
    });
  }
  return nodes.get(id);
}
vm.runInNewContext(match[1], {
  document:{getElementById:element}, Blob, URL, setTimeout,
});
function submit(id){element(id).listeners.submit({preventDefault(){}});}
submit("screen-form");
const screen=JSON.parse(element("screen-result").textContent);
assert.equal(screen.target_id,"EGFR");
assert.equal(screen.heuristic_affinity_kcal_mol,-10.01);
assert.equal(screen.lipinski_violations,0);
assert.equal(screen.heuristic_qed,1);
assert.equal(screen.not_validated,true);
element("tab-task").listeners.click();
assert.equal(element("screen-panel").hidden,true);
assert.equal(element("task-panel").hidden,false);
submit("task-form");
const task=JSON.parse(element("task-result").textContent);
assert.equal(task.overall_urgency,"ELEVATED_RISK");
assert.equal(task.audit_hash,null);
element("critical").checked=true;
submit("task-form");
assert.equal(JSON.parse(element("task-result").textContent).overall_urgency,"CRITICAL_STAT_PANIC");
console.log("Browser syntax, calculations, task triage and tabs passed");
