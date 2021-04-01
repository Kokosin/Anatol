# -*- coding: utf-8 -*-

import os
import sys
import re
import csv
import time
import math
from   datetime import datetime
import scrapy
import anhelp

ROBOTSTXT_OBEY =  False
ensure_ascii   =  False
LOG_LEVEL      = 'ERROR'

d_options = {
    "basedir"       : "D:\TEST\kerkmann\\",
    "product_all"   : 0,                                                         # к-ть продуктів - всього
    "product_done"  : 0,                                                         # к-ть продуктів - оброблено
    "product_err"   : 0,                                                         # к-ть продуктів - err
    "csv_nom_all"   : 0}

file_item = d_options["basedir"] + 'kerkmann_item.txt'                           # вхідні
file_done = d_options["basedir"] + 'kerkmann_done.txt'                           # оброблені
file_csv  = d_options["basedir"] + 'kerkmann.csv'                                # csv

list_item = anhelp.file_add_to_list(file_item)                                   # з файла --->список (item)
list_done = anhelp.file_add_to_list(file_done)                                   # з файла --->список (done)

list_item_len = len(list_item)
list_done_len = len(list_done)

csv_head     = ["Explicit URL","Categories","Name","Price","Artikelnummer","Short description","Images","Description","Price-all"]
scrapy_date  = datetime.now().strftime("%Y-%m-%d")                               # '2021-03-01''
csv_last_url = list_item[list_item_len-1]
csv_list     = []
# ---------------------------------



# ---------------------------------
class GenericSpider(scrapy.Spider):
    name = 'generic'
    allowed_domains = ['www.kerkmann-shop.de']

    # ---------------------------------------
    def start_requests(self):
        for url_item in list_item:
            # print_log(f'Start_requests --- {url_item}')
            yield scrapy.Request(url=url_item, callback=self.parse)
    # ---------------------------------------

    # ---------------------------------------
    def parse(self, response):
        d_options["product_all"] += 1

        if int(response.status) >= 400:
            print(f'Скрапінг - response.status {response.status} - {response.url}')
            d_options["product_err"] += 1
        else:
            print(f'Скрапінг - продукт {d_options["product_all"]} з {list_item_len}     {response.url}')
            item = item_create()
            # --------------------------------------------------------------------- Explicit URL
            item["Explicit URL"] = response.url
            # --------------------------------------------------------------------- Categories
            try:
                element = response.xpath('//div[@class="breadcrumbs"]/ul/li//text()').getall()
                if element: element = ''.join(anhelp.list_clear_none(element)[2:-2])
            except Exception as err: element = print_Exception("Categories", element_value = '')
            if element: item["Categories"] = element
            # 'Büromöbel nach Art/Schreibtische'
            # --------------------------------------------------------------------- Name
            try:
                element = response.xpath('//div[@class="product-name"]/span/text()').get()
            except Exception as err: element = print_Exception("Name", element_value = '')
            if element: item["Name"] = element
            # 'Schreibtisch Artline'
            # --------------------------------------------------------------------- Price
            try:
                element = response.xpath('//div[@class="price-box"]/span/span/text()').get()
                # '274,00\xa0€'
                if element: element = get_element_price(element)
            except Exception as err: element = print_Exception("Price", element_value=0)
            if element: item["Price"] = element
            else: item["Price"] = 0
            # 274,00
            # --------------------------------------------------------------------- Artikelnummer
            try:
                element = response.xpath('//table[@class="data-table"]/tbody/tr/td/text()').getall()
                if element: element = element[0] if len(element) == 1 else element[len(element)-1]
            except Exception as err: element = print_Exception("Artikelnummer", element_value='')
            if element: item["Artikelnummer"] = element
            # 'k-7650'
            # --------------------------------------------------------------------- Short description
            try:
                element = response.xpath('//div[@class="short-description"]/div//text()').getall()
                if element: element = ' '.join([str.replace('\xa0', '').strip() for str in element])
            except Exception as err: element = print_Exception("Short description", element_value='')
            if element: item["Short description"] = element
            # 'Tiefe: 800 mm bzw. 1000 mm (bei Breite 2000 mm) | höhenverstellbar 680 -820 mm'
            # --------------------------------------------------------------------- Images ----> список
            try:
                element = response.xpath('//div[@class="product-image-gallery"]/img/@src').getall()
                if element: element = ' , '.join(element)
            except Exception as err: element = print_Exception("Images", element_value='')
            if element: item["Images"] = element
            # ---------------------------------------------------------------------


            # --------------------------------------------------------------------- Description
            description_list = []
            # -------------------
            # ['Ein stilvoller und repräsentativer Schreibtisch, der durch den Materialmix aus Holz und verchromtem Stahlrohr besticht....]
            try:
                element = response.xpath('//dl[@id="collateral-tabs"]/dd/div/div/p/text()').getall()
                if element: element = ' '.join([str.replace('\xa0', '').strip() for str in element])
            except Exception as err: element = print_Exception("Description-1", element_value='')
            if element: description_list.append(element)
            # -------------------
            # ['Tischplatte aus E1 Gütespan, melaminharzbeschichtet, mit ABS Kante 2 mm stark', 'Plattenstärke 19 mm',.....]
            try:
                element = response.xpath('//dl[@id="collateral-tabs"]/dd/div/div/ul/li/text()').getall()
                if element: element = ' , '.join([str.replace('\xa0', '').strip() for str in element])
            except Exception as err: element = print_Exception("Description-2", element_value='')
            if element: description_list.append(element)
            # -------------------
            try:
                element = response.xpath('//dl[@id="collateral-tabs"]/dd/div/div/ol/li/text()').getall()
                if element: element = ' , '.join([str.replace('\xa0', '').strip() for str in element])
            except Exception as err: element = print_Exception("Description-4", element_value='')
            if element: description_list.append(element)
            # -------------------
            try:
                element = response.xpath('//dl[@id="collateral-tabs"]/dd/div/div/p/span/text()').getall()
                if element: element = ' , '.join([str.replace('\xa0', '').strip() for str in element])
            except Exception as err: element = print_Exception("Description-5", element_value='')
            if element: description_list.append(element)
            # -------------------
            item["Description"] = ', '.join(description_list)
            # ---------------------------------------------------------------------



            # ---------------------------------------------------------------------
            # ['Farbe:', 'Plattenmaß:', 'Kabeldurchlass links', 'Kabeldurchlass mittig', 'Kabeldurchlass rechts', 'Tischplatten-Steckdose mit USB Ladeport']
            # --------------------------------------------------------------------- аналіз таблиці
            d_element   = {}
            table_xpath = '//*[@id="product-options-wrapper"]/dl'

            try:
                dl_element = response.xpath(table_xpath).getall()                                          # 2
                if dl_element:
                    dl_len = len(dl_element)
                    # print_log(f'(dl) елемент - кількість --- {dl_len}')
                    # ---------------------------
                    for dl in range(1, dl_len+1):
                        table_xpath_dl = table_xpath + ('/dd' if dl_len == 1 else f'[{dl}]/dd')
                        # print_log(f'(dl) елемент --- {dl} з {dl_len}')
                        # -------------------------------
                        dd_element = response.xpath(table_xpath_dl).getall()                               # 2 + 4
                        if dd_element:
                            dd_len = len(dd_element)
                            # print_log(f'(dd) елемент - кількість --- {dd_len}')
                            # ---------------------------
                            for dd in range(1, dd_len+1):
                                table_xpath_dl_dd = table_xpath_dl + ('/' if dd_len == 1 else f'[{dd}]/')
                                # print_log(f'(dd) елемент --- {dd} з {dd_len}')
                                # -------------------------------------------------------------------- назва елемента
                                table_xpath_dl_dt = table_xpath_dl_dd.replace('/dd', '/dt')
                                element_key = get_element_key(response.xpath(table_xpath_dl_dt + 'label/text()').getall())
                                # ['\n        ', 'Farbe:\n        ', '\n    ', '\n        ']     ---> 'Farbe'
                                # -------------------------------------------------------------------- type='radio'/'checkbox'
                                element_type = response.xpath(table_xpath_dl_dd + 'div/ul/li/input/@type').get()
                                # --------------------------------------------------------------------
                                table_xpath_dl_dd_element = table_xpath_dl_dd + 'div/ul/li/a/@title'
                                element_1 = response.xpath(table_xpath_dl_dd_element).getall()
                                # -------------------------------------------------------------------- Farbe
                                if element_1 and (element_key == "Farbe" or element_key =="Arbeitsplatte") and not element_type:
                                    try:
                                        element_2 = [0]* len(element_1)
                                        # ['Weiß', 'Anthrazit'] [0,0]

                                        save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, table_xpath_dl_dd_element, response.url)
                                    except Exception as err: print_log(f'Exception ---{element_key}--- {err}')
                                    continue
                                # --------------------------------------------------------------------- Plattenmass
                                if element_1 and element_key == "Plattenmaß" and not element_type:
                                    try:
                                        element_2 = get_element_plattenmass(response.text, element_1)
                                        # ['1200x800 mm', '1600x800 mm', '1800x800 mm', '2000x1000 mm']

                                        save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, table_xpath_dl_dd_element, response.url)
                                    except Exception as err: print_log(f'Exception ---{element_key}--- {err}')
                                    continue
                                # --------------------------------------------------------------------- select/option (Kabeldurchlass)
                                table_xpath_dl_dd_element = table_xpath_dl_dd + 'div/select/option/text()'
                                element_1 = response.xpath(table_xpath_dl_dd_element).getall()
                                # ---------------------------------------------------------------------
                                if element_1 and not element_key == "Höhe" and not element_key == "Variante":
                                    try:
                                        element_1 = [str[: str.find(' +') if str.find(' +') >= 0 else len(str) ] for str in element_1][1:]
                                        # ['-- Bitte wählen --', 'ohne ', 'weiß +32,00\xa0€', 'silber +32,00\xa0€','schwarz +32,00\xa0€']
                                        # ['ohne ', 'weiß', 'silber','schwarz']
                                        element_2 = response.xpath(table_xpath_dl_dd + 'div/select/option/@price').getall()
                                        element_2 = get_element_str_to_float(element_2)
                                        # [0.0, 32.0, 32.0, 32.0]

                                        save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, table_xpath_dl_dd_element, response.url)
                                    except Exception as err: print_log(f'Exception ---{element_key}--- {err}')
                                    continue
                                # --------------------------------------------------------------------- radio / checkbox (Tischplatten-Steckdose mit USB Ladeport)
                                table_xpath_dl_dd_element = table_xpath_dl_dd + 'div/ul/li/span/label/text()'
                                element_1 = response.xpath(table_xpath_dl_dd_element).getall()
                                # ---------------------------------------------------------------------
                                if element_1 and element_type == 'radio':
                                    try:
                                        element_2 = response.xpath(table_xpath_dl_dd + 'div/ul/li/input/@price').getall()
                                        if len(element_1) > len(element_2):
                                            element_2 = element_2 = ['0'] + element_2

                                        # print(f'element_2 ({element_2})')
                                        element_2 = get_element_str_to_float(element_2)
                                        # ['62.9', '62.9', '62.9']
                                        save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, table_xpath_dl_dd_element, response.url)
                                    except Exception as err: print_log(f'Exception ---{element_key}--- {err}')
                                    continue
                                # -------------------------------------------------------------
                                if element_1 and element_type == 'checkbox':
                                    try:
                                        element_2 = response.xpath(table_xpath_dl_dd + 'div/ul/li/input/@price').getall()
                                        element_2 = get_element_str_to_float(element_2)

                                        save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, table_xpath_dl_dd_element, response.url)
                                    except Exception as err: print_log(f'Exception ---{element_key}--- {err}')
                                    continue
                                # --------------------------------------------------------------------- Höhe
                                if not element_1 and element_key == "Höhe" and not element_type:
                                    try:
                                        element_new = get_element_hohe(response.text,element_name='Ordnerhöhen')
                                        element_1 = element_new[0]
                                        element_2 = element_new[1]

                                        save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, table_xpath_dl_dd_element, response.url)
                                    except Exception as err: print_log(f'Exception ---{element_key}--- {err}')
                                    continue
                                    # --------------------------------------------------------------------- Variante
                                if element_key == "Variante" and not element_type:
                                    try:
                                        element_new = get_element_Variante(response.text, element_name='Variante')
                                        element_1 = element_new[0]
                                        element_2 = element_new[1]

                                        save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, table_xpath_dl_dd_element, response.url)
                                    except Exception as err: print_log(f'Exception ---{element_key}--- {err}')
                                    continue
                                # ---------------------------------------------------------------------
                                print_log(f'Не знайдено елемент ---> {element_key} type={element_type} xpath {table_xpath_dl_dd_element} {response.url}')
                                # ----------------------------------------------------
                            # print_log(f'виходимо з циклу - dd - {dd}  dl {dl}')
                        # -------------------------------------------------------
                        else: print_log(f'(dd) елемент --- відсутній ! {response.url}')
                    # -------------------------------------------------------
                    # print_log(f'виходимо з циклу - dl - {dd}  dl {dl}')
                # else: print_log(f'(dl) елемент --- відсутній ! {response.url}')
            except Exception as err: print_log(f'Exception  --- таблиця --- {err} {response.url}')
            # ---------------------------------------------------------------------  словник d_element
            # d_element = {'Farbe': [['Weiß', 'Anthrazit'], [0, 0]],
            #              'Plattenmaß': [['1200x800 mm', '1600x800 mm', '1800x800 mm', '2000x1000 mm'],
            #                             [0.0, 25.0, 55.0, 135.0]],
            #              'Kabeldurchlass links': [['ohne', 'weiß', 'silber', 'schwarz'], [0.0, 32.0, 32.0, 32.0]],
            #              'Kabeldurchlass mittig': [['ohne', 'weiß', 'silber', 'schwarz'], [0.0, 32.0, 32.0, 32.0]],
            #              'Kabeldurchlass rechts': [['ohne', 'weiß', 'silber', 'schwarz'], [0.0, 32.0, 32.0, 32.0]],
            #              'Tischplatten-Steckdose mit USB Ladeport[links]': [['-', 'links'], [0, 62.9]],
            #              'Tischplatten-Steckdose mit USB Ladeport[mittig]': [['-', 'mittig'], [0, 62.9]],
            #              'Tischplatten-Steckdose mit USB Ladeport[rechts]': [['-', 'rechts'], [0, 62.9]]}
            # ---------------------------------------------------------------------

        # -------------------------------------------------------------------------
        list_done.append(item["Explicit URL"])                                        # добавляємо в список
        anhelp.file_add_from_str(file_done, item["Explicit URL"])                     # добавляємо в файл
        d_options["product_done"] += 1

        for key in d_element:
            if key not in csv_head:
                csv_head.append(key)

        kerkmann_csv_create(item, d_element)

        if csv_last_url == response.url:
            kerkmann_csv_write()
# ==========================================================================




# ==========================================================================
def print_log(print_log_text='', print_log_exit= False):
    if print_log_text != '':
        print('-'*20 + print_log_text)
    if print_log_exit:
        print('-'*20 + f' Скрапінг - Процес завершено (sys.exit)')
        sys.exit()
# ==========================================================================
def print_Exception(element_key, element_value = ''):
    print_log(f'Exception ---{element_key}--- {err}')
    return element_value
# ==========================================================================
def save_to_dict_d_element(d_element, element_type, element_key, element_1, element_2, xpath, url):
    try:
        if element_1 and element_2:
            # print_log(f'Оброблено елемент - {element_key} type ({element_type})')

            element_1 = [line.replace(',', '.') for line in element_1]                                            # ???

            if element_type == 'checkbox':
                for i in range(0, len(element_1)):
                    element_key_new = element_key + '[' + element_1[i].strip() + ']'
                    element_1_new = ['']
                    element_2_new = [0]

                    element_1_new.append(element_1[i].strip())
                    element_2_new.append(element_2[i])

                    d_element[element_key_new] = [element_1_new, element_2_new]
            elif element_type == 'radio':
                d_element[element_key] = [element_1, element_2]
            else:
                d_element[element_key] = [element_1, element_2]
        else:
            print_log(f'(save_to_dict_d_element) - не знайдено елемент ---> {element_key} type={element_type} {element_1} {element_2} xpath {xpath} {url}')
    except Exception as err: print_log(f'(save_to_dict_d_element) - Exception -  {element_key}--- {err}')
    return True
# ==========================================================================
def get_element_key(element):
    # ['\n        ', 'Farbe:\n        ', '\n    ', '\n        ']
    element = [str.strip() for str in element]
    # ['', 'Farbe:', '', '']
    element = list(filter(None, element))
    # ['Farbe:']
    element = ''.join(element).strip()
    element = element.replace(':', '')
    element = element.replace(',', '.')                     # ???
    # 'Farbe'
    return element                                          # повертає <str>
# ==========================================================================
def get_element_plattenmass(res, list_size):
    # ['1200x800 mm', '1600x800 mm', '1800x800 mm', '2000x1000 mm']
    # 2000x1000 mm","price":"135"
    # element_js = response.xpath('//div[@class="product-options"]/script').getall()
    list_price = []
    for size in list_size:
        try:
            line = float(anhelp.str_seek(str_in= res, str_start= size + '","price":"', str_end= '"', status='one'))
        except Exception as err:
            line = float('0')
        list_price.append(line)
    return list_price
# ==========================================================================
def get_element_hohe(res, element_name ='Ordnerhöhen'):
    # ,"label":"2 Ordnerh\u00f6hen", "price": "0", ..."label": "3 Ordnerh\u00f6hen","price": "20",... "label": "5 Ordnerh\u00f6hen", "price": "45"
    element_1   = []
    element_2   = []
    element_new = []

    try:
        list_count = res.count('hen","price":"')         # ---> 3
        kol  = res.find('hen","price":"')
        res1 = res[kol - 30:kol + 400]
        # ---------------------------
        element_2 = anhelp.str_seek(str_in=res1, str_start='hen","price":"', str_end='"', status='all')
        # ['0', '20', '45']
        # ---------------------------
        element_1 = anhelp.str_seek(str_in=res1, str_start='"label":"', str_end=' O', status='all')
        element_1 = [line + 'Ordnerhöhen' for line in element_1]
        # ['2 ', '3 ', '5 ']
        try:
            element_2 = [float(line) for line in element_2]
        except Exception as err:
            element_2 = [float('0') for line in element_2]

        element_new.append(element_1)
        element_new.append(element_2)

    except Exception as err: print_log(f'Exception ---get_element_hohe--- {err}')
    return element_new
# ==========================================================================
def get_element_Variante(res, element_name ='Variante'):
    # print('Працює ---- Variante')
    element_1   = []
    element_2   = []
    element_new = []

    try:
        str      = '"label":"' + element_name              # Variante
        str_find = res.find(str) + len(str)
        if str_find > 0:
            str      = res[str_find: str_find + 600]
            element_1 = anhelp.str_seek(str_in=str, str_start='"label":"', str_end='"', status='all')
            element_2 = anhelp.str_seek(str_in=str, str_start='price":"',  str_end='"', status='all')
        try:
            element_2 = [float(line) for line in element_2]
        except Exception as err:
            element_2 = [float('0') for line in element_2]

        element_new.append(element_1)
        element_new.append(element_2)

    except Exception as err: print_log(f'Exception ---get_element_Variante--- {err}')
    return element_new
# ==========================================================================
def get_element_str_to_float(list_price_in):
    list_price_out = []
    for line in list_price_in:
        try:
            line = float(line)
        except Exception as err:
            line = float('0')
        list_price_out.append(line)
    return list_price_out
# ==========================================================================
def get_element_price(element):                              # '274,00\xa0€'
    try:
        element = element.replace('\xa0', '')
        element = element.replace('€', '')
        element = element.replace('.', '')                   # числа 1.0000,00
        element = element.replace(',', '.')
        # element = float(element.replace(',', '.'))
    except Exception as err: element = print_Exception("get_element_price", element_value='0.00')
    return element                                      # '274.00' or '0.00'
# ==========================================================================
def list_2_to_1(element_key, list_1, list_2):
    element = []
    if element_key: element.append(element_key + ': ')
    try:
        if list_1 and list_2:
            # list_1 = ['a', 'b', 'c']
            # list_2 = ['1', '2', '3']
            list_1 = [str.replace('\xa0', '').strip() for str in list_1]
            list_2 = [str.replace('\xa0', '').strip() for str in list_2]
            element_new = [list(str) for str in zip(list_1, list_2)]
            # [['a', '1'], ['b', '2'], ['c', '3']]
            for line in element_new: element.append(' | '.join(line))
            # ['weiß | 32.00', 'silber | 32.00', 'schwarz | 32.00']
        elif list_1 and not list_2:
            element.append([str.replace('\xa0', '').strip() for str in list_1])
        elif list_2 and not list_1:
            element.append([str.replace('\xa0', '').strip() for str in list_2])
        else: pass
    except Exception as err: print_log(f'Exception ---list_2_to_1--- {err}'); element = []
    return element                                         # повертає список
# ==========================================================================
def item_create():
    item = {}
    item["Explicit URL"]      = ''
    item["Categories"]        = ''
    item["Name"]              = ''
    item["Price"]             = 0
    item["Artikelnummer"]     = ''
    item["Short description"] = ''
    item["Images"]            = ''
    item["Description"]       = ''
    item["Price-all"]         = ''
    return item
# ==========================================================================



# ==========================================================================
def kerkmann_csv_create(item, d_element):
    #----------------------------------------------------------------------- рекурсивна функція
    def kerkmann_recursion(level_index):
        global mas_line
        global mas_price
        global mas_result

        for element_index in range(0, len(mas[level_index][0])):

            mas_line[level_index]  = mas[level_index][0][element_index]
            mas_price[level_index] = mas[level_index][1][element_index]

            if level_index < mas_len-1:
                kerkmann_recursion(level_index+1)
            else:
                mas_result += ','.join(mas_line)  + ',' + format(sum(mas_price), '.2f') + '|'
        return True
    #-----------------------------------------------------------------------
    #  item = {'Explicit URL': 'https://www.kerkmann-shop.de/bueromoebel/schreibtische/schreibtisch-artline.html',
    #          'Categories': 'Büromöbel nach Art/Schreibtische',
    #          'Name': 'Schreibtisch Artline',
    #          'Price': '274.00',
    #          'Artikelnummer': 'k-7650',
    #          'Short description': 'Tiefe:  800 mm Höhe: 680 - 820 mm',
    #          'Images': 'https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/7/6/7660_1.jpg , https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/7/6/7660_1.jpg , https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/3/0/3003_3004_3005_1_5_4_4_3.jpg , https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/a/r/artline_07s.jpg , https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/a/r/artline_05s.jpg , https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/a/r/artline_10s.jpg , https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/a/r/artline_04s.jpg , https://www.kerkmann-shop.de/media/catalog/product/cache/1/image/1800x/040ec09b1e35df139433887a97daa66f/a/r/artline_06s.jpg',
    #          'Description': [
    #              'Ein stilvoller und repräsentativer Schreibtisch, der durch den Materialmix aus Holz und verchromtem Stahlrohr besticht. Das Gestell in C-Fuß-Form besteht aus einem Chromrohrrahmen mit 28/32 mm Durchmesser (Standrohr) bzw. 38 mm Durchmesser (Fußausleger) und lässt sich von 68 - 82 cm in der Höhe verstellen.Das Gestell verfügt über Stellfüße zum Ausgleich von Bodenunebenheiten. Die Tischplattenhaben eine pflegeleichte und strapazierfähige Melaminharzoberfläche und stoßfeste ABS-Kanten.Unterhalb der Arbeitsplatte befindet sich ein horizontaler Kabelkanal zur Aufnahme von Steckdosenleisten und Kabeln.Dank des stabilen Tischplatten-Unterbaus aus verchromten Stahlrohr beträgt die erforderliche Tischplattenstärke nur 19 mm. Dies verleiht dem Tisch ein ästhetisches Aussehen und vermittelt eine gewisse Leichtigkeit. Optional kann der Schreibtisch mit einem Besprechungsansatztisch in Kreissegment-Form ergänzt werden oder mit einer Verkettungsplatte und einem zweiten Schreibtisch zu einer Winkelkombination erweitert werden.Eine optionale Knieraumblende bietet Sichtschutz und verkleidet den Schreibtisch zu seiner Front hin. Ergänzt das Programm durch Winkelkombinationen (bestehend aus dem jeweiligen Schreibtisch und einem Anbautisch 1000 x 600 mm) und einem Freiformtisch, der sich optimal für Bildschirmarbeitsplätze eignet. Für Konferenzen ist ein Besprechungstisch für 6 Personen mit fixer Höhe lieferbar. Die Arbeitsplatte kann mit einem oder mehreren Kabeldurchlässen versehen werden. Anstelle eines Kabeldurchlasses können optional Tischsteckdosen mit integriertem USB-Ladeport montiert werden. So können Handies, Tablets, Laptops und Notebooks schnell an die Stromversorgung angeschlossen und geladen werden. Die 230V-Steckdose kann durch eine Schutzkappe abgedeckt werden. Der USB-Ladeport ist auch bei geschlossener Schutzkappe zugänglich.   ',
    #              'Tischplatte aus E1 Gütespan, melaminharzbeschichtet, mit ABS Kante 2 mm stark , Plattenstärke 19 mm , stabiles C-Fuß-Gestell aus verchromtem Rundrohr , höhenverstellbar von 680 bis 820 mm , Fußausleger auf Stellfüßen , mit horizontalem Kabelkanal , optional mit Anbautisch in gleicher Bauart , optional auszurüsten mit einer Knieraumblende , optionale Tischsteckdose mit USB Ladeport, Schutzkappe und 190 cm langem Netzkabel mit Stecker']}
    #-----------------------------------------------------------------------
    # d_element = {'Farbe': [['Weiß', 'Anthrazit'], [0, 0]],
    #               'Plattenmaß': [['1200x800 mm', '1600x800 mm', '1800x800 mm', '2000x1000 mm'], [0.0, 25.0, 55.0, 135.0]],
    #               'Kabeldurchlass links': [['ohne', 'weiß', 'silber', 'schwarz'], [0.0, 32.0, 32.0, 32.0]],
    #               'Kabeldurchlass mittig': [['ohne', 'weiß', 'silber', 'schwarz'], [0.0, 32.0, 32.0, 32.0]],
    #               'Kabeldurchlass rechts': [['ohne', 'weiß', 'silber', 'schwarz'], [0.0, 32.0, 32.0, 32.0]],
    #               'Tischplatten-Steckdose mit USB Ladeport[links]': [['', 'links'], [0, 62.9]],
    #               'Tischplatten-Steckdose mit USB Ladeport[mittig]': [['', 'mittig'], [0, 62.9]],
    #               'Tischplatten-Steckdose mit USB Ladeport[rechts]': [['', 'rechts'], [0, 62.9]]}
    #-----------------------------------------------------------------------
    # csv_head = ['Explicit URL', 'Categories', 'Name', 'Price', 'Artikelnummer', 'Short description', 'Images', 'Description', 'Price-all', 'Farbe', ...]
    #-----------------------------------------------------------------------
    csv_nom   = 0
    d_product = {}
    for key in csv_head:
        d_product[key] = ""

    for key in item:
        d_product[key] = item[key]
    # ===========================================================================
    if not d_element:
        csv_list.append(list(d_product.values()))
        csv_nom += 1
    # ===========================================================================
    else:
        mas = list(d_element.values())                             # [[['Weiß', 'Anthrazit'], [0, 0]],  ...]]]
        # ---------------
        global mas_line
        global mas_price
        global mas_result

        mas_len     = len(mas)
        mas_line    = [''] * mas_len
        mas_price   = [0]  * mas_len
        mas_result  = ''

        try:
            kerkmann_recursion(0)                        # mas_result     ---> Weiß,1200x800 mm,ohne,ohne,ohne,-,-,-,0.00|Weiß,1200x800 mm,ohne,ohne,ohne,-,-,rechts,62.90|....|
            mas_list_value = mas_result.split('|')[:-1]  # mas_list_value ---> ['Weiß,1200x800 mm,ohne,ohne,ohne,-,-,-,0.00', 'Weiß,1200x800 mm,ohne,ohne,ohne,-,-,rechts,62.90',....,'']
            mas_list_key   = list(d_element.keys())      # mas_list_key   ---> ['Farbe', 'Plattenmaß', ....  'Tischplatten-Steckdose mit USB Ladeport[rechts]',"Price-all"]
            mas_list_key.append("Price-all")

        except Exception as err: print(f'(kerkmann_create_csv) - Exception - {err}')
        for variable_name in ['mas_line', 'mas_price', 'mas_result']:
            del globals()[variable_name]
    # ===========================================================================формуємо список словників елемента
        for mas_line in mas_list_value:                                   # 'Weiß,1200x800 mm,ohne,ohne,ohne,-,-,-,0.00'
            line = mas_line.split(',')                                    # ['Weiß','1200x800 mm','ohne','ohne','ohne','-','-','-','0.00']

            index = 0
            for key in mas_list_key:
                d_product[key] = line[index]
                index += 1

            csv_list.append(list(d_product.values()))

            if csv_nom == 0:
                for key in item:
                    d_product[key] = ""
            csv_nom += 1
    # ===========================================================================
    d_options["csv_nom_all"] += csv_nom
    print(f'({d_options["csv_nom_all"]}) ....... добавлено ({csv_nom})')
    return True
# ===============================================================================
def kerkmann_csv_write():                          # на вході - csv_list,csv_head
    print(f'Наповнення csv.файла ({file_csv}) ....... Процес розпочато ..... ')
    try:
        anhelp.file_check(file_csv, True)

        with open(file_csv, mode="a", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",", lineterminator="\n")
            writer.writerow(csv_head)
            for line in csv_list:
                if len(csv_head) > len(line):
                    for i in range(1, len(csv_head) - len(line) + 1):
                        line.append('')
                writer.writerow(line)
            f.close
    except Exception as err:
        print_log(f'(kerkmann_csv_write) - Збій запису в csv.файл ({csv_file}) -{err}')
        f.close()
    return True
# ===============================================================================


# =================== команди на виконання =================================
# scrapy crawl generic -O dump.json -                     ---- формат .json
# scrapy crawl generic -O dump.csv -t csv                 ---- формат .csv
# scrapy crawl generic -O dump.csv -t xml                 ---- формат .xml
# ==========================================================================
