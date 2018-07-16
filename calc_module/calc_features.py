# -*- coding: utf-8 -*-

"""
元の名前データあるいは入力データから特徴量を算出するモジュール
※ 文字がもつ情報を参照するために、MongoDB を使用する
"""

from pymongo import MongoClient
import math


class Calc:
    # インスタンス生成時、MongoDB への接続を確立
    def __init__(self, collection_name):
        self.mclient = MongoClient('localhost', 27017)
        self.db = self.mclient['name_extraction']
        self.collection = self.db[collection_name]


    def close(self):
        self.mclient.close()


    # 特徴量をリストにして返却（個別のメソッドの処理をまとめている）
    def gen_feature_list(self, input_str):
        input_len = len(input_str)
        # 最初に入力文字列（input_str）の1文字ごとに MongoDB に問い合わせる
        mongo_result_list = list()
        for input_ch in input_str:
            mongo_temp = mongo_temp = self.collection.find_one({"character" : input_ch})
            mongo_result_list.append(mongo_temp)
    
        head_validity = self.calc_head_validity(input_str, mongo_result_list)
        tail_validity = self.calc_tail_validity(input_str, mongo_result_list)
        middle_validity = self.calc_middle_validity(input_str, mongo_result_list,
                                               head_validity, tail_validity)
        linking_validity = self.calc_linking_validity(input_str, mongo_result_list,
                                    head_validity, tail_validity, middle_validity)
        repetition = self.detect_repetition(input_str)

        return [head_validity, tail_validity, middle_validity, linking_validity, repetition]


    """
    以下は、各特徴量を計算する関数
    外部からは直接呼ばれない想定
    """
    def calc_head_validity(self, input_str, mongo_result_list):
        mongo_result_head = mongo_result_list[0]   # 最初の文字に対応するデータ
        if mongo_result_head is not None:
            head_cnt = mongo_result_head["head_cnt"]    # 最初の文字としての出現回数
            if head_cnt==0:
                head_validity = 0.1
            else:
                head_validity = 1.0 + math.log2(head_cnt)
            return head_validity
        else:
            return 0.1    # 乗算で使用する値なので、ゼロにはしない


    def calc_tail_validity(self, input_str, mongo_result_list):   
        mongo_result_tail = mongo_result_list[-1]   # 最後の文字に対応するデータ
        if mongo_result_tail is not None:
            tail_cnt = mongo_result_tail["tail_cnt"]    # 最後の文字としての出現回数
            if len(input_str) >=2 :
                if tail_cnt==0:
                    return 0.1
                else:
                    tail_validity = 1.0 + math.log2(tail_cnt)
            elif len(input_str) == 1:
                if mongo_result_tail["head_cnt"] == 0:
                    tail_validity = 0.1
                else:
                    tail_validity = 1.0 + math.log2(mongo_result_tail["head_cnt"])
            return tail_validity
        else:
            return 0.1    # 乗算で使用する値なので、ゼロにはしない


    def calc_middle_validity(self, input_str, mongo_result_list, h_validity, t_validity):
        middle_validity = None
        input_len = len(input_str)
        if input_len == 3:
            mongo_result_middle = mongo_result_list[1]
            if mongo_result_middle is not None:
                middle_cnt = mongo_result_middle["middle_cnt"]
                if input_len >= 2:
                    if middle_cnt==0:
                        middle_validity = 0.1
                    else:
                        middle_validity = 1.0 + math.log2(middle_cnt)
                elif input_len == 1:
                    middle_validity = 1.0 + math.log2(mongo_result_middle["head_cnt"])
            else:
                middle_validity = 0.1
        elif input_len == 1 or input_len == 2:
            # 中間に位置する文字が存在しないため、代わりの値を用意
            middle_validity = (h_validity + t_validity) / 2.0

        return middle_validity


    def calc_linking_validity(self, input_str, mongo_result_list, h_validity, t_validity, m_validity):
        linking_validity = None
        input_len = len(input_str)
        if input_len == 1:
            if mongo_result_list[0] is not None:
                linking_validity = 1.0
            else:
                linking_validity = 0.1
        elif input_len == 2:
            if mongo_result_list[0] is not None:
                if input_str[1] in mongo_result_list[0]["next_char"]:
                    linking_validity = (h_validity + t_validity) / 2.0
                else:
                    # 「つながらない」組み合わせの場合
                    linking_validity = 0.1 * (h_validity + t_validity) / 2.0
            else:
                linking_validity = 0.1 * (h_validity + t_validity) / 2.0
        elif input_len == 3:
            lnk_vld_1 = None
            if mongo_result_list[0] is not None:
                if input_str[1] in mongo_result_list[0]["next_char"]:
                    lnk_vld_1 = (h_validity + m_validity) / 2.0
                else:
                    lnk_vld_1 = 0.1 * (h_validity + m_validity) / 2.0
            else:
                lnk_vld_1 = 0.1 * (h_validity + m_validity) / 2.0
            lnk_vld_2 = None
            if mongo_result_list[1] is not None:
                if input_str[2] in mongo_result_list[1]["next_char"]:
                    lnk_vld_2 = (m_validity + t_validity) / 2.0
                else:
                    lnk_vld_2 = 0.1 * (m_validity + t_validity) / 2.0
            else:
                lnk_vld_2 = 0.1 * (m_validity + t_validity) / 2.0

            # 最後に平均をとる
            linking_validity = (lnk_vld_1 + lnk_vld_2) / 2.0

        return linking_validity


    # family name の中に文字の重複があるか判定する処理
    # 重複がない場合は 1.0 を、ある場合は 0.0 を返す
    def detect_repetition(self, input_str):
        repetition = 1.0
        input_len = len(input_str)
        if input_len == 1:
            return 1.0
        elif input_len == 2:
            if input_str[0] == input_str[1]:
                repetition = 0.0
        elif input_len == 3:
            # ch: character
            # 1組でも文字が重複していれば 0.0 を返す
            flg_1 = input_str[0] == input_str[1]
            flg_2 = input_str[0] == input_str[2]
            flg_3 = input_str[1] == input_str[2]
            if flg_1 or flg_2 or flg_3:
                repetition = 0.0
        
        return repetition
