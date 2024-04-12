# -*- coding: utf-8 -*-
import os
from typing import List, Dict
from easydict import EasyDict
import yaml
import torch
from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification, AutoModelForSequenceClassification
from IE_modules.Utilities import Information_Extraction_Document
from IE_modules.NER_utilities import Sentence_NER_Dataset, NER_Predictor
from IE_modules.RE_utilities import InlineTag_RE_Dataset, RE_Predictor
from modules.utilities import backend_model
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

class IE_model(backend_model):
  def __init__(self):
    self.reset()
    
    
  def reset(self):
    self.ner_model_info = None
    self.ner_model = None
    self.ner_tokenizer = None
    self.re_model_info = None
    self.re_model = None
    self.re_tokenizer = None
    
  
  def get_entities(self, NER_model_info:Dict[str, str], text:str) -> List[Dict[str,str]]:
    """ Check if model is first time loaded or has been changed """
    logging.info('NER prediction starts...')
    if (self.ner_model_info is None or 
      NER_model_info['model_name'] != self.ner_model_info['model_name']):
      
      logging.info('Loading NER model...')
      self.ner_model = AutoModelForTokenClassification.\
        from_pretrained(os.path.join('models', 'NER', NER_model_info['model_name'], 'weight'))
        
      logging.info('Loading NER tokenizer...')
      self.ner_tokenizer = AutoTokenizer.\
        from_pretrained(os.path.join('models', 'NER', NER_model_info['model_name'], 'tokenizer'))
        
      self.ner_model_info = NER_model_info
      
    """ Prediction """
    logging.info('Packaging input text...')
    ie = Information_Extraction_Document(doc_id='input_doc', text=text)
    pred_dataset = Sentence_NER_Dataset(IEs=[ie], 
                                        tokenizer=self.ner_tokenizer, 
                                        label_map=self.ner_model_info['label_map'], 
                                        token_length=self.ner_model_info['token_length'], 
                                        has_label=False,
                                        mode=self.ner_model_info['BIO_mode'])
    
    predictor = NER_Predictor(model=self.ner_model,
                          tokenizer=self.ner_tokenizer,
                          dataset=pred_dataset,
                          label_map=self.ner_model_info['label_map'],
                          batch_size=self.ner_model_info['eval_batch_size'])
    
    logging.info('Predicting...')
    pred_IEs = predictor.predict()
    return pred_IEs[0]['entity']
      
  
  def get_relations(self, RE_model_info:Dict[str, str], text:str, entities:List[Dict]) -> List[Dict[str,str]]:
    """ Check if model is first time loaded or has been changed """
    logging.info('RE prediction starts...')
    if (self.re_model_info is None or 
      RE_model_info['model_name'] != self.re_model_info['model_name']):
      
      logging.info('Loading RE model...')
      self.re_model = AutoModelForSequenceClassification.\
        from_pretrained(os.path.join('models', 'RE', RE_model_info['model_name'], 'weight'))
        
      logging.info('Loading RE tokenizer...')
      self.re_tokenizer = AutoTokenizer.\
        from_pretrained(os.path.join('models', 'RE', RE_model_info['model_name'], 'tokenizer'))
        
      self.re_model_info = RE_model_info
    
    """ Prediction """
    logging.info('Packaging input text...')
    ie = Information_Extraction_Document(doc_id='input_doc', text=text, entity_list=entities)
    pred_dataset = InlineTag_RE_Dataset(IEs=[ie], 
                                        tokenizer=self.re_tokenizer, 
                                        possible_rel=self.re_model_info['possible_rel'],
                                        token_length=self.re_model_info['token_length'], 
                                        label_map=self.re_model_info['label_map'], 
                                        has_label=False)
    
    predictor = RE_Predictor(model=self.re_model,
                            tokenizer=self.re_tokenizer,
                            dataset=pred_dataset,
                            label_map=self.re_model_info['label_map'],
                            batch_size=self.re_model_info['eval_batch_size'])
    
    pred_IEs = predictor.predict()
    return pred_IEs[0]['relation']