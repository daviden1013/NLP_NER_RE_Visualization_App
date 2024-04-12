# -*- coding: utf-8 -*-
from typing import List
import base64
import os 
import pandas as pd
import json
from easydict import EasyDict
import yaml
from load_config import CONFIG
import dash
from dash import html, dcc, clientside_callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions import EventListener
from IE_modules.Utilities import Information_Extraction_Document
from modules.utilities import control_panel_manager, report_manager, backend_model
from IE_model import IE_model

""" Load manager obj """
cpm = control_panel_manager(model_dir='models')
rm = report_manager()
model = IE_model()
NER_model_info = None
RE_model_info = None

""" App layout """
app = dash.Dash(meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}], 
                external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(id='app-container', children=[
  html.Div(id='entity-store', style={"display": "none"}, **{"data-json":""}),
  html.Div(id='relation-store', style={"display": "none"}, **{"data-json":""}),
  dbc.Modal(children=[dbc.ModalHeader(''), dbc.ModalBody('')],
              id="information-modal",
              is_open=False,
          ),
  
  html.Div(id="banner", className="banner", children=[
    #html.Img(id="thumbnail", src=app.get_asset_url("App icon.png"),width=200, height=100)]),
    html.Img(id="thumbnail", src=app.get_asset_url("App icon.png"))]),
  html.Div(id='content', className='row', children=[
    html.Div(id='left-column', className='column', children=[
      html.Div(id='input-text-container', 
               children=[html.H5('Input text for processing:'), 
                         cpm.text_input,
                         cpm.upload_panel]),
      html.Div(id='ner-model-container', 
               children=[html.H5('Select named entity recognition (NER) model:'), 
                cpm.NER_model_dropdown,
                cpm.entity_dropdown]),
      html.Div(id='re-model-container', 
               children=[html.H5('Select relation extraction (RE) model:'), 
                cpm.RE_model_dropdown,
                cpm.relation_dropdown]),

      html.Div(id='button-container', className='row', children=[
        html.Div(cpm.clear_button, className='button-holder'),
        html.Div(cpm.submit_button, className='button-holder')
      ])
      ]),
    
    html.Div(id='right-column', className='column', children=[
      html.H5('Entities & Relations extracted:'),
      html.Div(id='display-textbox-container', children=[rm.display_textbox, rm.svg_container]),
      html.Div(id='table-container', className='row', children=[
        html.Div(id='entity-table-container', children=[html.H6('Entities extracted:'), rm.entity_table]),
        html.Div(id='relation-table-container', children=[html.H6('Relations extracted:'), rm.relation_table])
                 ])
      ])
    ])
  ])


@app.callback(
  output=dict(
    entity_dropdown_options = Output("entity-dropdown", "options"),
    entity_dropdown_value = Output("entity-dropdown", "value")
  ),
  inputs=dict(
    NER_model_dropdown_value = Input("NER-model-dropdown", "value"),
  )
)
def select_NER_model_dropdown(NER_model_dropdown_value:str):
  """
  When a NER model is selected, entity dropdown/ display is updated

  Parameters
  ----------
  NER_model_dropdown_value : str
    NER model name.
  """
  if NER_model_dropdown_value is None:
    return {"entity_dropdown_options":[], "entity_dropdown_value":""}

  else:
    global NER_model_info
    NER_model_info = cpm.load_model_info(model_name=NER_model_dropdown_value, mode='NER')
    color_map = cpm.get_entity_color(NER_model_info['categories'])
    
    return {"entity_dropdown_options":[{'label':html.Span(c, style={'color':color_map[c]}), 'value':c} for c in NER_model_info['categories']],
            "entity_dropdown_value":NER_model_info['categories']}

@app.callback(
  output=dict(
    relation_dropdown_options = Output("relation-dropdown", "options"),
    relation_dropdown_value = Output("relation-dropdown", "value"),
  ),
  inputs=dict(
    RE_model_dropdown_value = Input("RE-model-dropdown", "value"),
  )
)
def select_RE_model_dropdown(RE_model_dropdown_value:str):
  """
  When a RE model is selected, relation dropdown/ display is updated

  Parameters
  ----------
  RE_model_dropdown_value : str
    relation model name.
  """
  if RE_model_dropdown_value is None:
    return {"relation_dropdown_options":[], "relation_dropdown_value":""}
  else:
    global RE_model_info
    RE_model_info = cpm.load_model_info(model_name=RE_model_dropdown_value, mode='RE')
    
    return {"relation_dropdown_options":[{'label':c, 'value':c} for c in RE_model_info['categories']],
            "relation_dropdown_value":RE_model_info['categories']}

@app.callback(
  output=dict(
    information_modal_open = Output("information-modal", "is_open"),
    information_modal_children = Output("information-modal", "children"),
    entity_store_data = Output("entity-store", "data-json"),
    relation_store_data = Output("relation-store", "data-json"),
    entity_table_data = Output("entity-table", "data"),
    relation_table_data = Output("relation-table", "data")
  ),
  inputs=dict(
    submit_button = Input("submit-button", "n_clicks"),
    text_input = Input("text-input", "value"),
    NER_model_dropdown_value = Input("NER-model-dropdown", "value"),
    RE_model_dropdown_value = Input("RE-model-dropdown", "value")
  ),
  prevent_initial_call=True
)
def click_submit_button(submit_button:int, text_input:str,
                          NER_model_dropdown_value:str, RE_model_dropdown_value:str):
  """
  When submit button is clicked, backend model calculate and update data in 
  entity-store and relation-store
  """
  ctx = dash.callback_context
  trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
  
  if  trigger_id != "submit-button":
    raise PreventUpdate
  
  if text_input is None or text_input == "":
    head = "Input text for processing:"
    msg = "Please enter text or upload text (.txt)"
    return {"information_modal_open":True, 
            "information_modal_children":[dbc.ModalHeader(head), 
                                          dbc.ModalBody(msg)],
            "entity_store_data":dash.no_update, 
            "relation_store_data":dash.no_update, 
            "entity_table_data":dash.no_update,
            "relation_table_data":dash.no_update}
              
  # NER
  if NER_model_dropdown_value is None:
    head = "Select named entity recognition (NER) model:"
    msg = "Please select a NER model from the dropdown menu."
    return {"information_modal_open":True, 
            "information_modal_children":[dbc.ModalHeader(head), 
                                          dbc.ModalBody(msg)],
            "entity_store_data":dash.no_update, 
            "relation_store_data":dash.no_update, 
            "entity_table_data":dash.no_update,
            "relation_table_data":dash.no_update}

  else:
    global NER_model_info
    color_map = cpm.get_entity_color(NER_model_info['categories'])
    entities = model.get_entities(NER_model_info, text_input)
    for entity in entities:
      entity['color'] = color_map[entity['entity_type']]
  
  # RE
  if RE_model_dropdown_value is None:
    return {"information_modal_open":dash.no_update,
            "information_modal_children":dash.no_update,
            "entity_store_data":json.dumps(entities), 
            "relation_store_data":dash.no_update, 
            "entity_table_data":entities,
            "relation_table_data":dash.no_update}
  else:
    global RE_model_info
    relations = model.get_relations(RE_model_info, text_input, entities)
    return {"information_modal_open":dash.no_update,
            "information_modal_children":dash.no_update,
            "entity_store_data":json.dumps(entities), 
            "relation_store_data":json.dumps(relations),
            "entity_table_data":entities,
            "relation_table_data":relations}


@app.callback(
  output=dict(
    text_input_value = Output("text-input", "value"),
    NER_model_dropdown_value = Output("NER-model-dropdown", "value"),
    entity_dropdown_options = Output("entity-dropdown", "options", allow_duplicate=True),
    entity_dropdown_value = Output("entity-dropdown", "value", allow_duplicate=True),
    RE_model_dropdown_value = Output("RE-model-dropdown", "value"),
    relation_dropdown_options = Output("relation-dropdown", "options", allow_duplicate=True),
    relation_dropdown_value = Output("relation-dropdown", "value", allow_duplicate=True),
    entity_table_data = Output("entity-table", "data", allow_duplicate=True),
    relation_table_data = Output("relation-table", "data", allow_duplicate=True),
    entity_store_data = Output("entity-store", "data-json", allow_duplicate=True),
    relation_store_data = Output("relation-store", "data-json", allow_duplicate=True)
  ),
  inputs=dict(
    submit_button = Input("clear-button", "n_clicks"),
  ),
  prevent_initial_call=True
)
def click_clear_button(submit_button:int):
  """
  When clear button clicked, input text, NER and RE model dropdown, and backend 
  model are reset to default. Stored data for entity and relation are cleared.
  """
  ctx = dash.callback_context
  trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
  
  if  trigger_id != "clear-button":
    raise PreventUpdate
  
  model.reset()
  return {"text_input_value":"",
          "NER_model_dropdown_value":None,
          "entity_dropdown_options":[],
          "entity_dropdown_value":None,
          "RE_model_dropdown_value":None,
          "relation_dropdown_options":[],
          "relation_dropdown_value":None,
          "entity_table_data":None,
          "relation_table_data":None,
          "entity_store_data":"",
          "relation_store_data":""
          }


@app.callback(
  output=dict(
    text_input_value = Output("text-input", "value", allow_duplicate=True)
  ),
  inputs=dict(
    text_upload_panel_filename = Input("text-upload-panel", "filename"),
    text_upload_panel_contents = Input("text-upload-panel", "contents")
    ),
  prevent_initial_call=True
)
def upload(text_upload_panel_filename, text_upload_panel_contents):
  ctx = dash.callback_context
  trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
  if trigger_id == "text-upload-panel":
    if text_upload_panel_filename[-4:] != '.txt':
      raise PreventUpdate
    
    byte_part = text_upload_panel_contents.replace('data:text/plain;base64,', '')
    byte_str = base64.b64decode(byte_part).decode('utf-8')
    return {"text_input_value":byte_str}


if __name__ == "__main__":
  app.run(debug=False)