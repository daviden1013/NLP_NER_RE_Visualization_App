# -*- coding: utf-8 -*-
import os
import yaml
from easydict import EasyDict

global CONFIG
with open('app_config.yaml') as yaml_file:
  CONFIG = EasyDict(yaml.safe_load(yaml_file))