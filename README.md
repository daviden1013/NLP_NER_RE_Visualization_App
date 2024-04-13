# Overview
An interactive web App for named entity recognition (NER) and relation extraction (RE) model visualization. The main framework is [Plotly Dash](https://dash.plotly.com/) with Python for the backend and JavaScrtip for frontend. 
In this repo, we use [PyTorch](https://pytorch.org/) to implement the backend NLP model. More details about the backend is available in [this repo](https://github.com/daviden1013/NLP_IE_Pipelines.git) 
## Demo
**App layout and features**

![Demo screenshot](https://github.com/daviden1013/NLP_NER_RE_Visualization_App/assets/24928020/ba18b5bd-0630-4947-90f0-cb7d3b574c14)

**Demo video**

https://github.com/daviden1013/NLP_NER_RE_Visualization_App/assets/24928020/9bc978ca-9cc5-49de-a2ab-03b3e2322ac8

# How to use this App
## Installation
To install the App, clone this repo and install environment
~~~cmd
>> git clone https://github.com/daviden1013/NLP_NER_RE_Visualization_App.git
>> cd <project dir>
>> conda env create -f environment.yml
~~~
## Deployment
To run the app on your localhost (default behavior)
~~~cmd
>> cd <project dir>
>> python app.py

Dash is running on http://127.0.0.1:8050/

<datetime> - Dash is running on http://127.0.0.1:8050/
~~~
Then open a browser and visit **http://localhost:8050/**.

For deployment on other IP, replace the IP and port in *./app_config.yaml* with your new IP and port. This will allow other devices in the same network to access the App. 
~~~yaml
---
  # IP address this App will run on, default is localhost
  address: <new_IP>
  # specify port, default is 8050
  port: <new_port>
~~~
# How to customize the backend NLP model
This frontend App is by default connected to a BERT information extraction pipeline in [this repo](https://github.com/daviden1013/NLP_IE_Pipelines.git). See *./IE_model.py* and *./IE_modules/* for more details.
All backend NLP models are stored in the *./models/* following file structure:
~~~
./models
  - /NER
    - <first_ner_model>
    - <second_ner_model>
  - /RE
    - <first_re_model>
    - <second_re_model>
~~~
Each model folder must have a *config.yaml* file with **model_name**, **info**, and **categories**. For example (*./models/NER/i2b2_2018_BERT100%/configs.yaml*):
~~~yaml
---
  # Standard model info
  # This section is required for all models regardless of implemtation
  model_name: i2b2_2018_BERT100%
  info: This is a NER model trained with the 2018 i2b2 (Medication and ADE extraction) challenge training set. 
  categories:
    - Drug
    - Strength
    - Dosage
    - Duration
    - Frequency
    - Form
    - Route
    - Reason
    - ADE
~~~


# Use ANY NLP systems with this App
A completely different backend implementation is possible by customizing the **backend_model** class in *./modules/utilities*. In other words, users can use any NLP systems they prefer. 
Users will define their own model class by inherting the parent backend_model, and make sure to define the *get_entities()*, *get_relations()*, and *reset()* methods following the define interfaces. 
See *./IE_model.py* for an example. 
~~~python
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
~~~





