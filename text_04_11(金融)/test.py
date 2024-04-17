import time
import openpyxl
import csv
import requests
import os
import re
from concurrent.futures import ThreadPoolExecutor
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             ' AppleWebKit/537.36 (KHTML, like Gecko)'
                             ' Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'}

def data_writer(items):
    with open('finance.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(items)

def down_load(title, pdf, i):
    #开始拼接url
    if pdf[0] == 'g':
        pdf_url = (f"http://reportdocs.static.szse.cn/UpFiles/jgsy/{pdf}")
    else:
        pdf_url = (f"http://reportdocs.static.szse.cn/UpFiles/zqjghj/{pdf}")
    response = requests.get(pdf_url, headers=headers)

    cleaned_filename = str(i) + '_' + re.sub(r'[\\/*?:"<>|]', '', title) + '.pdf'
    with open(cleaned_filename, mode="wb") as f:
        f.write(response.content)
    print(f"已保存 PDF 文件: {cleaned_filename}")

def down(company, content, i):
    cleaned_filename = re.sub(r'[\\/*?:"<>|]', '', company)
    with open(f'{i}_{cleaned_filename}.txt', mode='w', encoding='utf-8', newline='') as f:
        f.write(content)


if __name__ == '__main__':
    # 用法示例：
    wb = openpyxl.load_workbook('监管措施.xlsx')
    sheet_name = '监管措施'

    sheet = wb[sheet_name]
    os.makedirs("downloads_2", exist_ok=True)  # 创建一个名为 "downloads" 的文件夹
    os.chdir("downloads_2")  # 切换到 "downloads" 文件夹
    cells = sheet['A3672':'E4255']  #3688
    i = 3671
    for r in cells:
        down_load(r[1].value, r[4].value, i)
        i += 1

    for r in cells:
        down(r[1].value, r[4].value, i)
        i += 1
    datas = list(sheet.values)
    # 第一步，取出标题
    title = datas[0]
    case_list = []
    for case in datas[0:]:
        case_list.append(case)
        data_writer(case_list)
    os.makedirs("downloads", exist_ok=True)  # 创建一个名为 "downloads" 的文件夹
    os.chdir("downloads")  # 切换到 "downloads" 文件夹
    for case in datas[1:]:
        down_load(case[4])
        time.sleep(2)
    print("over!")


'''准备将数据导入数据库'''
import re
import csv
import os
import pymongo

target_mongo_url = "mongodb://keger:keger!%40%23%24@121.22.248.8:30019/?authMechanism=SCRAM-SHA-1&authSource=publisher"
target_db_name = "publisher"
client = pymongo.MongoClient(target_mongo_url)[target_db_name]
'''从数据库中选取了两个集合'''
target_collection = client["Shen_regulatory_measures"]
source_collection = client["Hu_regulatory_measures"]

'''插入函数'''
def insert_test(row):
    collection = target_collection
    document = {
        "gkxx_gsdm": row[0],
        "gkxx_gsjc": row[1],
        "gkxx_gdrq": row[2],
        "gkxx_jgcs": row[3],
        "hjnr": row[4]
    }
    collection.insert_one(document)

def doc(filename):
    '''逐行读取文件的内容并返回'''
    cleaned_filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    folder_path = 'x1'
    file_path = os.path.join(folder_path, cleaned_filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        content = ''.join(lines)
    return content

# 打开 CSV 文件
with open('finance.csv', encoding='utf-8', newline='') as csvfile:
    # 创建 CSV 文件读取器
    reader = csv.reader(csvfile)
    i = 1
    for row in reader:
        if ".pdf" in row[4]:
            row[4] = doc(f"{i}_{row[1]}.txt")
            insert_test(row)
        else:
            insert_test(row)
        i += 1

print("over!")




