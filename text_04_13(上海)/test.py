# import json
# import csv
#
# with open('x1.json', 'r', encoding='utf-8') as f:
#     file_content = f.read()
#     # 将 JSON 字符串解析为字典
#     data_dict = json.loads(file_content)
#
# def data_writer(items):
#     with open('finance1.csv', 'w', encoding='utf-8', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         # 写入 CSV 标题行
#         writer.writerow(["stockcode " "extGSJC " "extWTFL " "docTitle " "extTeacher " "cmsOpDate "])
#         # 写入数据行
#         writer.writerows(items)
#
# # 初始化数据列表
# items = []
# # 遍历数据字典中的每个条目
# for infor in data_dict["pageHelp"]["data"]:
#     stockcode = infor["stockcode"]
#     extGSJC = infor["extGSJC"]
#     extWTFL = infor["extWTFL"]
#     docTitle = infor["docTitle"]
#     extTeacher = infor["extTeacher"]
#     cmsOpDate = infor["cmsOpDate"]
#     # 将每个字段作为列表添加到数据列表中
#     items.append([stockcode, extGSJC, extWTFL, docTitle, extTeacher, cmsOpDate])
#
# # 写入数据到 CSV 文件
# data_writer(items)
#
#
# import requests
# import json
# import os
# from lxml import etree
# import re
#
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
#                              ' AppleWebKit/537.36 (KHTML, like Gecko)'
#                              ' Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'}
#
# with open('x1.json', 'r', encoding='utf-8') as f:
#     file_content = f.read()
#     # 将 JSON 字符串解析为字典
#     data_dict = json.loads(file_content)
#
# def down_load1(extGSJC, docTitle, i):
#     #直接保存到txt文件中
#     with open(f'{i}_{extGSJC}.txt', mode='w', encoding='utf-8') as f:
#         f.write(docTitle)
#     print(f"{i}.ok")
#
# def down_load2(docURL, extGSJC, i):
#     #利用json文件中的URL，直接发起请求开始下载
#     docURL = 'http://' + docURL
#     resp = requests.get(docURL, headers=headers)
#     with open(f'{i}_{extGSJC}.pdf', mode='wb') as f:
#         f.write(resp.content)  # 正确写法，使用 response.content 获取字节数据
#     print(f"{i}.ok")
#
# def down_load3(docURL, extGSJC, i):
#     #向页面发起请求，正常爬取数据
#     docURL = 'http://' + docURL
#     resp = requests.get(docURL, headers=headers)
#     # 解析 HTML 内容
#     html = resp.content
#     tree = etree.HTML(html)
#     #提取标题
#     title = tree.xpath('/html/body/div[8]/div[2]/div/div[1]/div/div/h2/text()')
#     #提取文件内容
#     doc_list = tree.xpath('/html/body/div[8]/div[2]/div/div[1]/div/div/div[2]/p')
#     # 将文本内容连接成一个字符串
#     content = '\n'.join([''.join(doc.xpath('.//text()')) for doc in doc_list])
#     # 将内容写入文件
#     with open(f'{i}_{extGSJC}.txt', mode='w', encoding='utf-8') as f:
#         f.write(content)
#     print(f"{i}.ok")
#
#
# os.makedirs("downloads_1", exist_ok=True)  # 创建一个名为 "downloads" 的文件夹
# os.chdir("downloads_1")  # 切换到 "downloads" 文件夹
# i = 1
# for infor in data_dict["pageHelp"]["data"]:
#     docURL = infor["docURL"]
#     infor["extGSJC"] = re.sub(r'[\\/*?:"<>|]', '', infor["extGSJC"])
#     if len(docURL) == 0 or docURL[-1] == 'c':
#         #直接保存docTitle
#         down_load1(infor["extGSJC"], infor["docTitle"], i)
#         i += 1
#
#     elif docURL[-1] == 'f':
#         #如果是pdf文档，向网页发起请求，下载pdf
#         down_load2(infor["docURL"], infor["extGSJC"], i)
#         i += 1
#
#     elif docURL[-1] == 'l':
#         #如果是shtml，向页面发起请求，爬取页面相应的数据
#         down_load3(infor["docURL"], infor["extGSJC"],  i)
#         i += 1

'''准备将数据导入数据库'''
import re
import csv
import os
import pymongo
import json

target_mongo_url = "mongodb://keger:keger!%40%23%24@121.22.248.8:30019/?authMechanism=SCRAM-SHA-1&authSource=publisher"
target_db_name = "publisher"
client = pymongo.MongoClient(target_mongo_url)[target_db_name]
'''从数据库中选取了两个集合'''
target_collection = client["Hu_regulatory_measures"]


'''插入函数'''
def insert_test(resp):
    collection = target_collection
    document = {
        # "stockcode": row[0],
        # "extGSJC": row[1],
        # "extWTFL": row[2],
        "docTitle": resp
        # "extTeacher": row[4],
        # "cmsOpDate": row[5]
    }
    collection.insert_one(document)

def update_test(query, update_data):
    # cleaned_query = re.sub(r'[\\/*?:"<>|]', '', query)
    collection = target_collection
    update_query = {"stockcode": query}
    # 使用 $set 操作符来设置字段值
    update_operation = {"$set": {"docTitle": update_data}}
    collection.update_one(update_query, update_operation)



def doc(filename):
    '''逐行读取文件的内容并返回'''
    cleaned_filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    folder_path = "downloads_1"
    file_path = os.path.join(folder_path, cleaned_filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        content = ''.join(lines)
    return content

# 打开 CSV 文件
with open('finance1.csv', encoding='utf-8', newline='') as csvfile:
    # 创建 CSV 文件读取器
    reader = csv.reader(csvfile)
    i = 1
    for row in reader:
        # insert_test(row)
        resp = doc(f"{i}_{row[1]}.txt")
        update_test(row[0], resp)
        i += 1
        # # print(resp)
        # print(str(i))

