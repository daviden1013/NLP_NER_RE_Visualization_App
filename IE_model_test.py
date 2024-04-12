# -*- coding: utf-8 -*-
import os
from typing import List, Dict
from easydict import EasyDict
import yaml
import torch
from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification
from IE_modules.Utilities import Information_Extraction_Document
from IE_modules.NER_utilities import Sentence_NER_Dataset, NER_Predictor
from modules.utilities import backend_model


class IE_model(backend_model):
  def __init__(self):
    self.ie = Information_Extraction_Document(doc_id='100035', 
                                     filename=os.path.join('E:\David projects\IE Dash', '100035.ie'))
  
  def get_entities(self, text:str) -> List[Dict[str,str]]:
    return self.ie['entity']
  
  
  def get_relations(self, text:str, entities:List[Dict]) -> List[Dict[str,str]]:
    return self.ie['relation']
    
