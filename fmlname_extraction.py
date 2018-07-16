# 

"""
日本人の名字（漢字）を判定するクラス
ファイルから読み出したテキストに対し、
"""

from pymongo import MongoClient
from sklearn.svm import SVC
from sklearn.externals import joblib

from calc_module.calc_features import Calc


class FamilyNameExtraction:
    def __init__(self):
        
        # MongoDB の準備
        self.mclient = MongoClient('localhost', 27017)
        self.db = self.mclient['name_extraction']
        self.agg_collection = self.db['fmlname_agg']    # 文字ごとの集計
        self.knowledge_collection = self.db['fmlname_knowledge']    # 「名字」などの分類知識

        # Calc クラス（自前定義）の準備／特徴量生成のため
        self.calcf = Calc('fmlname_agg')
        
        # 学習済みモデルの準備
        self.prepare_ml_model()


    # MongoDB 接続をクローズ
    def close(self):
        self.mclient.close()


    # 学習済みモデルを取得する処理／ml: Machine Learning
    def prepare_ml_model(self, model_filename='fmlname_model.pkl'):
        self.clf = joblib.load(model_filename)


    # 文字の種類を調べ、MongoDB から検索を実行するかどうかを判定する関数
    # ※ 日本語以外のUnicode文字の混入は想定していない
    def character_filtering(self, ch):
        # ch: character
        # 結果が True ならば MongoDB からの検索を実行
        result = True
        
        if ord(ch) >= 32 and ord(ch) <= 126:
            # ASCII文字
            result = False
        elif (ch>='\u3041' and ch<='\u3096') or (ch>='\u3099' and ch<='\u309e'):
            # ひらがな
            result = False
        elif ch>='\u3041' and ch<='\u3096':
            # カタカナ
            result = False

        return result


    # クエリを実行
    def char_mongo_query(self, ch):
        mongo_result = None
        # 文字をフィルタにかける
        flg_do_query = self.character_filtering(ch)

        # フラグが True の場合のみクエリを実行
        if flg_do_query:
            mongo_result = self.agg_collection.find_one({"character": ch})

        return mongo_result


    # MongoDB の中に情報をもつ文字が現れた場合、人名が現れるか
    # ただし一般名詞や地名の可能性もある
    def pick_up_name(self, line, ch_pos, blocking_list):
        extracted_name_dict = None
    
        cand_list = self.create_cand(line, ch_pos, blocking_list)

        for cand_list_elem in cand_list:
            # 特徴量を生成
            feature_list = self.calcf.gen_feature_list(cand_list_elem['str'])
                    
            # ml: Machine Learning
            # SVM で名前かどうかを判定する
            ml_result = self.clf.predict([feature_list])
            
            if ml_result[0] == 'family_name':
                # 当面、最初に陽性判定が出た時点でループを抜ける
                extracted_name_dict = cand_list_elem
                break
        
        return extracted_name_dict


    # 「前3文字」「前2文字」「1文字のみ」「後2文字」「後3文字」という候補の作成
    # それぞれ、該当する文字列を格納した辞書を用意する
    def create_cand(self, line, ch_pos, blocking_list):
        cand_list = list()
        line_len = len(line)

        if ch_pos == 0:
            if line_len >= 1:
                cand_list.append({"str": line[ch_pos:ch_pos+2], "range":[0,1], "length": 2})
                if line_len > 1:
                    cand_list.append({"str": line[ch_pos:ch_pos+3], "range":[0,2], "length": 3})
            cand_list.append({"str": line[ch_pos], "range":[0,0], "length": 1})    # 1文字は優先度を下げる
        elif ch_pos == 1:
            if ch_pos-1 not in blocking_list:
                cand_list.append({"str": line[ch_pos-1:ch_pos+1], "range":[0,1], "length": 2})
            if line_len >= 2:
                cand_list.append({"str": line[ch_pos:ch_pos+2], "range":[1,2], "length": 2})
                if line_len > 2:
                    cand_list.append({"str": line[ch_pos:ch_pos+3], "range":[1,3], "length": 3})
            cand_list.append({"str": line[ch_pos], "range":[0,0], "length": 1})
        elif ch_pos >= 2:
            if ch_pos-2 not in blocking_list:
                cand_list.append({"str": line[ch_pos-2:ch_pos+1], "range":[ch_pos-2,ch_pos], "length": 3})
            if ch_pos-1 not in blocking_list:
                cand_list.append({"str": line[ch_pos-1:ch_pos+1], "range":[ch_pos-1,ch_pos], "length": 2})
            if ch_pos < line_len-1:
                cand_list.append({"str": line[ch_pos:ch_pos+2], "range":[ch_pos,ch_pos+1], "length": 2})
                if ch_pos < line_len-2:
                    cand_list.append({"str": line[ch_pos:ch_pos+3], "range":[ch_pos,ch_pos+2], "length": 3})
            cand_list.append({"str": line[ch_pos], "range":[ch_pos,ch_pos], "length": 1})

        return cand_list


    # 「名字」「一般名詞」といった分類を決定する処理
    # （人間が行っているような柔軟な判断はできない）
    # @param extracted_name_dict    抽出された「名前」のデータ
    def decide_class(self, line, extracted_name_dict):
        # MongoDB の「知識」コレクションから検索する
        knlge_result = self.knowledge_collection.find_one({"name": extracted_name_dict['str']})
        
        if knlge_result is None:
            # 知識がまだない場合、「名字」と判定しておく
            extracted_name_dict['class'] = '名字'
        else:
            # 知識が存在する場合
            if knlge_result['default_class'] != '名字':
                if '名字' in knlge_result['class']:
                    # 「名字」がデフォルトではなく、かつ候補の中に存在している場合
                    start = extracted_name_dict['range'][1] + 1    # 「名前」の直後の文字
                    if start == len(line)-1:
                        extracted_name_dict['class'] = knlge_result['default_class']
                    elif start < len(line)-1:
                        if line[start] == '様' or line[start] == '殿':
                            # 「～様」「～殿」の形式
                            extracted_name_dict['class'] = '名字'
                        elif start<len(line)-2 and line[start]=='さ' and (line[start+1]=='ん' or line[start+1]=='ま'):
                            # 「～さん」の形式
                            extracted_name_dict['class'] = '名字'
                        else:
                            extracted_name_dict['class'] = knlge_result['default_class']
                else:
                    extracted_name_dict['class'] = knlge_result['default_class']
            else:
                extracted_name_dict['class'] = knlge_result['default_class']



    # クラスの外部から呼び出すメイン処理
    def main(self):
        
        # テキストファイル読み込み／ただし UTF-8 の想定
        filename = './test.txt'
        text_file = open(filename, mode='rt', encoding='utf-8')
        line_list = text_file.readlines()
        
        # 抽出された名前を入れるリスト
        name_list = list()
        
        line_number = 1
        
        # 1行ごとに処理を実行
        for line in line_list:
            # すでに名前と認識した箇所は index を記憶させておく
            blocking_list = list()
            
            ch_pos = 0    # pos: position（位置）
            # 1文字ずつ調べる
            while ch_pos < len(line):
                # MongoDB に格納された文字であれば、検索して情報を取り出す
                mongo_result = self.char_mongo_query(line[ch_pos])
                
                if mongo_result is not None:
                    extracted_name_dict = self.pick_up_name(line, ch_pos, blocking_list)
                    if extracted_name_dict is not None:
                        # 名前であった場合は、その類型（分類）を決定する
                        self.decide_class(line, extracted_name_dict)
                        name_list.append(extracted_name_dict)

                        # blocking_list に要素を追加する
                        blk_cnt = extracted_name_dict['range'][0]
                        while blk_cnt <= extracted_name_dict['range'][1]:
                            if blk_cnt not in blocking_list:
                                blocking_list.append(blk_cnt)
                            blk_cnt += 1

                        # ch_pos を（名前の長さ - 1）だけ進める
                        ch_pos += extracted_name_dict["length"] - 1

                ch_pos += 1
                # ---- while loop end ----
            
            blocking_list.clear()
            line_number += 1
        
        text_file.close()
        self.close()    # MongoDB をクローズ
        
        print(name_list)


if __name__=='__main__':
    FamilyNameExtraction().main()
