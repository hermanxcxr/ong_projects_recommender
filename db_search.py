import json
import pandas as pd
import numpy as np
import re
from textblob import TextBlob

import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import wordnet as wn
nltk.download('stopwords')
from nltk.corpus import stopwords

class DbSearch:

    def __init__(self,country,funding,keywords):
        self.country = country
        self.funding = int(funding)
        self.keywords = keywords
        self.pattern = r'''(?x)                 # set flag to allow verbose regexps
                        (?:[a-zA-Z]\.)+         # abbreviations, e.g. U.S.A.
                        | \w+(?:-\w+)*       # words with optional internal hyphens
                        | \$?\d+(?:\,.\d+)?%? # currency and percentages, e.g. $12.40, 82%
                        | \.\.\.             # ellipsis
                        | [][.,;"'?():-_`]   # these are separate tokens; includes ], [
                        '''
        
        self.stopwd = set(stopwords.words('english'))
    
    def translation(self,words_list):
        tmp_cat = nltk.regexp_tokenize(words_list, self.pattern)
        tmp_cat = [re.sub(r'[^A-Za-z0-9]+', '',token) for token in tmp_cat ]
        tmp_cat = [token for token in tmp_cat if token ]
        en_tmp_cat = []
        for word in tmp_cat:
            tmp_blob = TextBlob(word)
            tmp_word = tmp_blob.translate(to='en')        
            tmp_word = str(tmp_word)
            en_tmp_cat.append(tmp_word)
        return en_tmp_cat

    def country_det(self,token_list,country):
        country = country.lower()
        l_tl = [x.lower() for x in token_list]
        if country in l_tl:
            return True

    def ratings(self,in_ss,vs_ss):
        qualifications = {}
        q2 = {}
        for key,value in vs_ss.items():        
            partial_q = []
            tmp_string = []
            for skey,svalue in in_ss.items(): #in_ss siempre será un sólo objeto
                tmp = []
                tmp_string.append(skey)
                for tkey,tvalue in value.items():
                    similarity = svalue.path_similarity(tvalue)
                    tmp.append(similarity)
                tmp_q = sum(tmp) / len(tmp)
                partial_q.append(tmp_q)
            q1 = sum(partial_q) / len(partial_q)
            
            qualifications[f'{list(value.keys())} : {tmp_string}'] = q1 
            
            q2[f'{list(value.keys())}'] = q1
        
        print(sorted(qualifications.items(), key=lambda x: x[1], reverse=True))
        return qualifications, q2

    def db_searcher(self):
        with open('outputs/cleaned_opportunities.json','r',encoding='utf-8') as opportunities:
            op_dict = json.load(opportunities)
        op_df = pd.DataFrame.from_dict(op_dict)
        op_df['str_t_cat'] =  op_df['t_cat'].astype(str)

        cats = op_df['t_cat'].value_counts()
        cats_list = list(cats.index)
        vs_ss = {}
        for i in range(len(cats_list)):
            tmp = {}
            for initial in cats_list[i]:
                ss = wn.synsets(initial.lower())
                meaning = ss[0]
                tmp[initial] = meaning
            vs_ss[i] = tmp
        
        
        in_0 = self.translation(self.keywords)
        in_ss = {}
        for initial in in_0:
            ss = wn.synsets(initial.lower())
            meaning = ss[0]
            in_ss[initial] = meaning
        
        q, q2 = self.ratings(in_ss,vs_ss)

        best_category = sorted(q2.items(), key=lambda x: x[1], reverse=True)[0][0]

        target_1 =  op_df[op_df['str_t_cat'] == best_category]




        country = self.country
        country_idx = target_1['t_desc'].map(lambda x: self.country_det(x,country))
        how_many =  sum([ 1  for value in country_idx if value == True])

        if how_many == 0:
            target = target_1.nlargest(5,'funding')
        elif how_many < 5:   
            idxs = list(country_idx.where(country_idx == True).dropna().index)
            df_country = target_1.loc[idxs,:]
            target_1.drop(labels=idxs ,axis=0,inplace=True)
            df_others = target_1.nlargest(5-how_many,'funding')
            target = df_country.append(df_others)
        elif how_many >= 5:
            idxs = list(country_idx.where(country_idx == True).dropna().index)
            df_country = target_1.loc[idxs,:]
            target = df_country.nlargest(5,'funding')

        target.to_excel('outputs/opportunity.xlsx')



