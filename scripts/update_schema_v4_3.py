#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'data' / 'project_msr_database.schema.json'
s = json.loads(path.read_text(encoding='utf-8'))
s['$id'] = 'https://project-msr.local/schema/project_msr_database-4.3.0.json'
s['title'] = 'Project-MSR Integrated Planner Database Schema v4.3.0'
meta = s['properties']['meta']['properties']
meta['version'] = {'const':'4.3.0'}
meta['application_version'] = {'const':'4.3.0'}
meta['engineering_work_package_schema'] = {'const':'4.3'}
meta['implementation_plan_schema'] = {'const':'1.0'}
s['properties']['meta']['required'] = list(dict.fromkeys(s['properties']['meta']['required'] + ['application_version','engineering_work_package_schema','implementation_plan_schema']))
s['properties']['planning_profile']['properties']['version'] = {'const':'4.3.0'}

impl_step = {
  'type':'object',
  'required':['step_id','action','responsible_role','work_location','required_inputs','detailed_guidance','tools_equipment','outputs_and_records','acceptance_condition'],
  'properties':{
    'step_id':{'type':'string','minLength':3},
    'action':{'type':'string','minLength':10},
    'responsible_role':{'type':'string','minLength':2},
    'supporting_roles':{'type':'array','items':{'type':'string'}},
    'work_location':{'type':'string','minLength':10},
    'required_inputs':{'type':'array','minItems':1,'items':{'type':'string','minLength':3}},
    'detailed_guidance':{'type':'string','minLength':80},
    'tools_equipment':{'type':'array','minItems':1,'items':{'type':'string','minLength':2}},
    'outputs_and_records':{'type':'array','minItems':1,'items':{'type':'string','minLength':3}},
    'acceptance_condition':{'type':'string','minLength':20},
    'hold_point':{'type':'string'}
  },
  'additionalProperties': True,
}
impl_plan = {
  'type':'object',
  'required':['implementation_readiness','implementation_summary','delivery_strategy','make_buy_partner_decision','authorizations_and_prerequisites','implementation_steps','procurement_and_contracting_actions','long_lead_items','decision_points','field_lab_or_vendor_activities','fallbacks_and_contingencies','implementation_records','linked_playbooks','implementation_source_basis','open_decisions','implementation_quality_score'],
  'properties':{
    'implementation_readiness':{'type':'string','minLength':20},
    'implementation_summary':{'type':'string','minLength':40},
    'delivery_strategy':{'type':'object','minProperties':3,'additionalProperties':True},
    'make_buy_partner_decision':{'type':'object','minProperties':3,'additionalProperties':True},
    'authorizations_and_prerequisites':{'type':'array','minItems':2,'items':{'type':'object','required':['authorization','evidence'],'additionalProperties':True}},
    'implementation_steps':{'type':'array','minItems':5,'items':impl_step},
    'procurement_and_contracting_actions':{'type':'array','minItems':1,'items':{'type':'string','minLength':15}},
    'long_lead_items':{'type':'array','items':{'type':'object','required':['item','action'],'additionalProperties':True}},
    'decision_points':{'type':'array','minItems':1,'items':{'type':'object','required':['decision','required_by','evidence'],'additionalProperties':True}},
    'field_lab_or_vendor_activities':{'type':'array','minItems':1,'items':{'type':'object','required':['activity','where','evidence'],'additionalProperties':True}},
    'fallbacks_and_contingencies':{'type':'array','minItems':1,'items':{'type':'object','required':['trigger','response'],'additionalProperties':True}},
    'implementation_records':{'type':'array','minItems':4,'items':{'type':'string','minLength':10}},
    'linked_playbooks':{'type':'array','items':{'type':'string'}},
    'implementation_source_basis':{'type':'array','items':{'type':'object','additionalProperties':True}},
    'open_decisions':{'type':'array','minItems':1,'items':{'type':'object','required':['decision','owner','required_by','closure_evidence'],'additionalProperties':True}},
    'implementation_quality_score':{'type':'integer','minimum':0,'maximum':100},
  },
  'additionalProperties':True,
}
s['$defs']['implementationStep'] = impl_step
s['$defs']['implementationPlan'] = impl_plan
task = s['$defs']['task']
task['required'] = list(dict.fromkeys(task['required'] + ['implementation_plan']))
task['properties']['implementation_plan'] = {'$ref':'#/$defs/implementationPlan'}

for name in ['implementation_playbooks','fuel_supply_plan','chemistry_processing_plan']:
    if name not in s['required']:
        s['required'].append(name)
s['properties']['implementation_playbooks'] = {'type':'object','minProperties':8,'additionalProperties':{'type':'object','additionalProperties':True}}
s['properties']['fuel_supply_plan'] = {'type':'object','required':['playbook_id','title','objective'],'additionalProperties':True}
s['properties']['chemistry_processing_plan'] = {
    'type': 'object',
    'required': ['playbook_id', 'title', 'objective', 'experiment_matrix'],
    'properties': {
        'experiment_matrix': {
            'type': 'array',
            'minItems': 25,
            'items': {
                'type': 'object',
                'required': ['test_id','campaign','objective','configuration','material_stage','primary_measurements','analytical_methods','acceptance_basis','model_or_decision_supported','linked_task_ids','planned_window','facility_strategy','required_records'],
                'additionalProperties': True,
            },
        },
    },
    'additionalProperties': True,
}
if 'implementation_closure_register' not in s['required']:
    s['required'].append('implementation_closure_register')
s['properties']['implementation_closure_register'] = {
    'type': 'array',
    'minItems': 1,
    'items': {
        'type': 'object',
        'required': ['closure_id','closure_item','work_required','accountable_functions','need_date','closure_evidence','status'],
        'properties': {
            'closure_id': {'type':'string','minLength':4},
            'closure_item': {'type':'string','minLength':10},
            'work_required': {'type':'string','minLength':40},
            'accountable_functions': {'type':'string','minLength':5},
            'need_date': {'type':'string','pattern':r'^\d{4}-\d{2}-\d{2}$'},
            'closure_evidence': {'type':'string','minLength':20},
            'status': {'type':'string','minLength':2},
        },
        'additionalProperties': True,
    },
}
path.write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('updated',path)
