# -*- coding: utf-8 -*-
import subprocess
from lxml import etree



date_dic = {#元旦
            '20150101':'20150104', '20150102':'20150104', '20150103':'20150104', '20150104':'20150104',
            #春节
            '20150215':'20150215', '20150218':'20150225', '20150219':'20150225', '20150220':'20150225', 
            '20150221':'20150225', '20150222':'20150225', '20150223':'20150225', '20150224':'20150225', 
            #清明
            '20150404':'20150407', '20150405':'20150407', '20150406':'20150407',
            #五一
            '20150501':'20150504',
            #端午节
            '20150620':'20150623', '20150621':'20150623', '20150622':'20150623',
            #国庆
            '20151001':'20151008', '20151002':'20151008', '20151003':'20151008', '20151004':'20151008', 
            '20151005':'20151008', '20151006':'20151008', '20151007':'20151008', '20151010':'20151010',             
            }

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def get_db_clear_date(xmlstring):
    tree = etree.fromstring(xmlstring)
    r = tree.getroottree()
    root = r.getroot()
    round_num = root[0].text
    first_round_cleardate = root[1][0][1].text
    first_clearround = root[1][0][2].text
    second_round_cleardate = root[1][1][1].text
    second_clearround = root[1][1][2].text
    return (round_num, first_round_cleardate, first_clearround, second_round_cleardate, second_clearround)
    
    

def run():
    for key in sorted(date_dic.keys()):
        command = '''dbtools "select content from workday where workdate='{0}'"'''.format(key)
        process = subprocess.Popen(command, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
        xmlstring = str(process.stdout.read().strip()[0:-2]).strip()
        db_clear_date = get_db_clear_date(xmlstring)
        if db_clear_date[1] == db_clear_date[3] and date_dic[key] == db_clear_date[0]:
            print("Date: {0},  Clear_Date: {1}, Match!".format(key, db_clear_date))
        else:
            print("Wrong!!! \t {0}".format(key))
        process.kill()

            
if __name__ == '__main__':
    run()
 
