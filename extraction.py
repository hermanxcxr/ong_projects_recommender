import re
import json

from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Extraction:

    def __init__(self,path,website_url,specific_url):
        self.path = path
        self.w_url = website_url
        self.s_url = specific_url

        

    def extractor(self):
        delay = 10
        driver = webdriver.Chrome(self.path)
        driver.get(self.w_url)
        pages = 8
        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

        prime_info = {}
        conv = 0
        prime_url = self.s_url
        pattern = r'[^\d]'
        for i in range(pages):
            
            for i in range(2,27):
                opportunity_number = WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//tr[{}]/td/a[contains(@href,"javascript:viewOppDetails")]'.format(i))
                    )
                )
                
                tmp_txt = re.sub(pattern,'',opportunity_number.get_attribute('href'))
                
                prime_info[conv] = {'title_id' : opportunity_number.get_attribute('innerHTML') ,
                                    'url' : prime_url + tmp_txt }
                conv += 1
            
            
            next_button = WebDriverWait(driver,delay).until(
                EC.presence_of_element_located(
                    (By.XPATH,'//span[@id="paginationTop"]/a[contains(@href,"javascript:next()")]')
                )
            )
            next_button.click()

        features_list = [
            'Funding Opportunity Title:',
            'Opportunity Title:',
            'Category of Funding Activity:',
            'Estimated Total Program Funding:',
            'Award Ceiling:',
            'Agency Name:',
            'Description:'
        ]
        for key, value in prime_info.items():
            print(key)
            driver.get(prime_info[key]['url'])
            driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
            
            table_1l =  WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//div[contains(@id,"DetailsGeneralInfoTableLeft")]/table/tbody')
                    )
                )
            table_1r =  WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//div[contains(@id,"DetailsGeneralInfoTableRight")]/table/tbody')
                    )
                )

            features_l = table_1l.find_elements_by_tag_name('th')
            features_r = table_1r.find_elements_by_tag_name('th')

            features_cl = []
            for item in features_l:
                features_cl.append(item.get_attribute('innerHTML'))
            features_cr = []
            for item in features_r:
                features_cr.append(item.get_attribute('innerHTML'))


            features_indexes={}
            for feature in features_list:
                try:
                    features_indexes[feature] = features_cl.index(feature) + 1
                except:
                    pass
            for feature in features_list:
                try:
                    features_indexes[feature] = features_cr.index(feature) + 1
                except:
                    pass
            
            try:
                title =  WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//div[contains(@id,"DetailsGeneralInfoTableLeft")]/table/tbody/tr[{}]/td/span'.format(features_indexes['Funding Opportunity Title:']))
                    )
                )
            except:
                title =  WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//div[contains(@id,"DetailsGeneralInfoTableLeft")]/table/tbody/tr[{}]/td/span'.format(features_indexes['Opportunity Title:']))
                    )
                )
            prime_info[key]['title'] = title.get_attribute('innerHTML')

            category =  WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//div[contains(@id,"DetailsGeneralInfoTableLeft")]/table/tbody/tr[{}]/td/span/span'.format(features_indexes['Category of Funding Activity:']))
                    )
                )
            prime_info[key]['category'] = category.get_attribute('innerHTML')

            funding =  WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//div[contains(@id,"DetailsGeneralInfoTableRight")]/table/tbody/tr[{}]/td/span'.format(features_indexes['Estimated Total Program Funding:']))
                    )
                )
            
            if funding.get_attribute('innerHTML') == '&nbsp;':
                funding =  WebDriverWait(driver,delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH,'//div[contains(@id,"DetailsGeneralInfoTableRight")]/table/tbody/tr[{}]/td/span'.format(features_indexes['Award Ceiling:']))
                    )
                )
            
            prime_info[key]['funding'] = funding.get_attribute('innerHTML')
            
            agency = WebDriverWait(driver,delay).until(
                EC.presence_of_element_located(
                    (By.XPATH,'//div[contains(@id,"DetailsAdditionalInfoTable")]/table/tbody/tr[1]/td/span')
                )
            )
            prime_info[key]['agency'] = agency.get_attribute('innerHTML')
            
            description = WebDriverWait(driver,delay).until(
                EC.presence_of_element_located(
                    (By.XPATH,'//div[contains(@id,"DetailsAdditionalInfoTable")]/table/tbody/tr[2]/td/span/span')
                )
            )
            prime_info[key]['description'] = description.text

            with open("outputs/opportunities.json", "w") as outfile:
                json.dump(prime_info, outfile)
            outfile.close()