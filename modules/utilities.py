# -*- coding: utf-8 -*-
import abc
import os
from typing import Dict, List
from easydict import EasyDict
import yaml
import pandas as pd
import dash_core_components as dcc
import dash_daq as daq
from dash import html
from dash import dash_table
import dash_svg as svg
from load_config import CONFIG

class control_panel_manager:
  def __init__(self, model_dir:str):
    """
    This class manages the control panel on the left column. 
    It returns the contents, handles clear and submit behaviers.
    """
    self.model_dir = model_dir
    
    # Textbox for text input or copy-paste
    self.text_input = dcc.Textarea(id='text-input',
                            placeholder="input text here...",
                            value=""
                            )
    
    # optionally, use upload button to upload text
    self.upload_panel = dcc.Upload(id='text-upload-panel',
                        children=['Drag and Drop or ', html.A('Select a File')]
                        )
    
    # NER model dropdown
    NER_model_names = os.listdir(os.path.join(self.model_dir, 'NER'))
    assert len(NER_model_names) > 0, f'No models found under {self.model_dir}/NER'
    
    self.NER_model_dropdown = dcc.Dropdown(id='NER-model-dropdown',
                                      options=[{'label':model, 'value':model} for model in NER_model_names],
                                      value=None
                                  )
    # Entity display dropdown
    self.entity_dropdown = dcc.Dropdown(id='entity-dropdown',
                                        placeholder='entity types...',
                                        multi=True,
                                        disabled=True
                                        )
    # RE model dropdown
    RE_model_names = os.listdir(os.path.join(self.model_dir, 'RE'))
    assert len(RE_model_names) > 0, f'No models found under {self.model_dir}/RE'
    
    self.RE_model_dropdown = dcc.Dropdown(id='RE-model-dropdown',
                                      options=[{'label':model, 'value':model} for model in RE_model_names],
                                      value=None
                                  )
    # Replation display dropdown
    self.relation_dropdown = dcc.Dropdown(id='relation-dropdown',
                                          placeholder='relation types...',
                                          options=[],
                                          multi=True,
                                          disabled=True
                                          )

    self.submit_button = html.Button('Submit', id='submit-button', n_clicks=0,
            title='Click to run NLP model')
    
    self.clear_button = html.Button('Clear', id='clear-button', n_clicks=0,
                title='Click to clear input text')
    
    
  def load_model_info(self, model_name:str, mode:str) -> Dict[str, str]:
    """
    This method loads NER/ RE models' name, info and entities

    Parameters
    ----------
    model_name : str
      model name correspond to the folder name /model/NER or /model/RE
    mode : str
      NER or RE

    Returns
    -------
    a dict of {info, categories}
    """
    with open(os.path.join(self.model_dir, mode, model_name, 'config.yaml')) as yaml_file:
      config = EasyDict(yaml.safe_load(yaml_file))

    return config
    
    
  def get_entity_color(self, entities:List[str]) -> Dict[str, str]:
    """
    This method inputs a list of entities (from the model's info)
    outputs a dict of {entity:color code}

    Parameters
    ----------
    entities : List[str]
      list of entities the NER model could predict

    Returns
    -------
    Dict[str]
      dict of {entity:color code}
    """
    entity_color = {}
    for i, entity in enumerate(entities):
      total_default_colors = len(CONFIG['default_color_codes'])
      entity_color[entity] = CONFIG['default_color_codes'][i%total_default_colors]
    return entity_color
  

class report_manager:
  def __init__(self):
    """
    This class holds and controls objects for results display:
      display-textbox
      entity-table
      relation-table
    """
    self.display_textbox = dcc.Loading(
      html.Div(id='display-textbox', children=[], 
                                    className="scrollabletextbox", 
                                    style={'whiteSpace': 'pre-line'})
      )
    
    self.svg_container = dcc.Loading(
      svg.Svg(id='display-relation')
      )
    
    self.entity_table = dcc.Loading(dash_table.DataTable(id='entity-table',
                      columns=[{'name':'Entity extracted', 'id':'entity_text'}, 
                               {'name':'Entity type', 'id':'entity_type'},
                               {'name':'start', 'id':'start'},
                               {'name':'end', 'id':'end'},
                               {'name':'conf', 'id':'conf', 'type':'numeric', 
                                                'format': {'specifier': '.2f'}}],
                      filter_action="native",
                      sort_action="native",
                      row_selectable=None,
                      style_table={'width': '100%', 'height': '30vh', 'overflowY': 'auto'},
                      style_data={'whiteSpace': 'normal'},
                      style_cell={'textAlign': 'left', 'font_size': '12px'}
                        )
                      )
    self.relation_table = dcc.Loading(dash_table.DataTable(id='relation-table',
                  columns=[{'name':'Entity 1', 'id':'entity_1_text'}, 
                           {'name':'Entity 2', 'id':'entity_2_text'},
                           {'name':'Relation', 'id':'relation_type'},
                           {'name':'conf', 'id':'relation_prob', 'type':'numeric', 
                                              'format': {'specifier': '.2%'}}],
                  filter_action="native",
                  sort_action="native",
                  row_selectable=None,
                  style_table={'width': '100%', 'height': '30vh', 'overflowY': 'auto'},
                  style_data={'whiteSpace': 'normal'},
                  style_cell={'textAlign': 'left', 'font_size': '12px'}
                    )
                  )
    
    
class backend_model:
  def __init__(self):
    """
    This is a parent class for individual backend implementation to inherit
    The get_entities(), get_relations(), and reset() methods must be implemented and return 
    consistent data structure as defined.
    """
    pass
  
  @abc.abstractmethod
  def get_entities(self, text:str) -> List[Dict[str,str]]:
    """
    This method inputs the text (from input textbox) 
    and outputs a dict of extracted entities

    Returns
    -------
    List[Dict[str,str]]
      list of dict with {entity_id, entity_type, entity_text, start, end}
    """
    return NotImplemented
    
    
  @abc.abstractmethod
  def get_relations(self, text:str, entities:List[Dict[str,str]]) -> List[Dict[str,str]]:
    """
    This method inputs the text (from input textbox) and a list of entities:
      list of dict with {entity_id, entity_type, entity_text, start, end}
    Outputs a dict of extracted relations

    Returns
    -------
    List[Dict[str,str]]
      list of dict with {relation_id, entity_1_id, entity_1_text, entity_2_id, 
                         entity_2_text, relation_type}
    """
    return NotImplemented
  
  @abc.abstractmethod
  def reset(self):
    """
    This method releases backend model resources and reset the model names (if any)
    to default. This method is called when clear button click. 
    """
    return NotImplemented