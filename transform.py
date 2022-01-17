import pandas as pd
import json
import numpy as np
import re

import nltk
nltk.download('punkt')
from nltk import word_tokenize
nltk.download('stopwords')
from nltk.corpus import stopwords
nltk.download('wordnet')
from nltk.corpus import wordnet as wn

class Transform:

    def __init__(self):
        self.pattern = r'''(?x)                 # set flag to allow verbose regexps
                        (?:[a-zA-Z]\.)+         # abbreviations, e.g. U.S.A.
                        | \w+(?:-\w+)*       # words with optional internal hyphens
                        | \$?\d+(?:\,.\d+)?%? # currency and percentages, e.g. $12.40, 82%
                        | \.\.\.             # ellipsis
                        | [][.,;"'?():-_`]   # these are separate tokens; includes ], [
                        '''
        
        self.stopwd = set(stopwords.words('english'))

    def cat_tokenization(self,category):
        category = nltk.regexp_tokenize(category, self.pattern)
        category = [re.sub(r'[^A-Za-z0-9]+', '',token) for token in category]
        category = [token for token in category if token]
        category = [word for word in category if word not in self.stopwd]
        
        if category[0] in ['Other','Humanities','Arts']:
            category = [category[0]]
        
        return category

    def desc_tokenization(self,description):
        description = nltk.regexp_tokenize(description, self.pattern)
        description = [re.sub(r'[^A-Za-z0-9]+', '',token) for token in description]
        description = [token for token in description if token]      
        description = [word for word in description if word not in self.stopwd]
        
        return description

    def db_transformer(self):
        with open("outputs/opportunities.json", "r", encoding='utf-8') as outfile:
            prime_info = json.load(outfile)
        
        df = pd.DataFrame.from_dict(prime_info, orient='index')
        
        df['t_cat'] = df['category'].map(lambda x: self.cat_tokenization(x))
        df['t_desc'] = df['description'].map(lambda x: self.desc_tokenization(x))
        df['funding'] = pd.to_numeric(df['funding']
                              .str.replace('$','',regex=True)
                              .str.replace(',','',regex=True)
                              .replace('&nbsp;',np.nan)
                             )
        
        df.to_json('outputs/cleaned_opportunities.json')
