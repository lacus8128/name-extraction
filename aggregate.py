# -*- coding: utf-8 -*-

import csv
from pymongo import MongoClient


# main function; entry point
def main():
    # aggregated data
    agg_data = dict()
    
    # knowledge data (on family name string)
    knowledge_data = list()
    
    # 元のcsvデータを開く
    file_name = './family_name.csv'
    with open(file_name, 'rt', encoding='utf-8') as f:
        reader = csv.reader(f)
        original_data_list = list(reader)
        
        for elem in original_data_list:
            if elem[2] == 'family_name':
                # ラベルが「人名」の場合のみ下記を実行
                
                # 知識データに「人名」「地名」等の類型を登録
                knowledge_data.append({
                    "name" : elem[1],
                    "type_cand" : elem[3].split(':')
                })
                
                # ch: character
                fmlname = elem[1]
                ch_pos = 0    # pos: position
                fmlname_len = len(fmlname)   # family name length
                for ch in elem[1]:
                    # 未登録の文字ならば新規で用意
                    if ch not in agg_data:
                        agg_data[ch] = {
                            "character" : ch,
                            "total_cnt" : 0,
                            "head_cnt" : 0,
                            "tail_cnt" : 0,
                            "middle_cnt" : 0,
                            "prev_char" : [],
                            "next_char" : [],
                            "single" : False
                        }

                    agg_data[ch]["total_cnt"] += 1

                    # note: the maximum length of family name is 3
                    if ch_pos == 0:
                        agg_data[ch]["head_cnt"] += 1
                        if fmlname_len==1:
                            agg_data[ch]["single"] = True
                        elif fmlname_len >= 2:
                            if fmlname[1] not in agg_data[ch]["next_char"]:
                                agg_data[ch]["next_char"].append(fmlname[1])
                    elif ch_pos == 1:
                        if fmlname_len==2:
                            agg_data[ch]["tail_cnt"] += 1
                        elif fmlname_len==3:
                            agg_data[ch]["middle_cnt"] += 1
                            if fmlname[2] not in agg_data[ch]["next_char"]:
                                agg_data[ch]["next_char"].append(fmlname[2])

                        if fmlname[0] not in agg_data[ch]["prev_char"]:
                            agg_data[ch]["prev_char"].append(fmlname[0])
                    elif ch_pos == 2:
                        agg_data[ch]["tail_cnt"] += 1
                        if fmlname[1] not in agg_data[ch]["prev_char"]:
                            agg_data[ch]["prev_char"].append(fmlname[1])
                
                    ch_pos += 1
                # -- character loop end --


    # insert data into MongoDB
    mclient = MongoClient('localhost', 27017)
    agg_insert_list = [agg_data[ch] for ch in list(agg_data.keys())]
    mongo_insert_list(mclient, agg_insert_list, 'fmlname_agg')
    mongo_insert_list(mclient, knowledge_data, 'fmlname_knowledge')
    mclient.close()


def mongo_insert_list(mclient, list, collection_name):
    db = mclient['name_extraction']
    collection = db[collection_name]
    collection.remove({})
    result = collection.insert_many(list)
    # print(result.inserted_ids)


if __name__ == '__main__':
    main()
