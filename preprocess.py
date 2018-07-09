# -*- coding: utf-8 -*-

"""
元の csv を再度開き、特徴量データを加えて新しい csv に書き込む
"""

import csv
from calc_module.calc_features import Calc


def main():
    original_data_list = None
    # 元の csv データを開く
    orig_file_name = './family_name.csv'
    with open(orig_file_name, mode='rt', encoding='utf-8') as f:
        reader = csv.reader(f)
        original_data_list = list(reader)
    
    # 新しい csv データを開く
    out_file_name = './family_name_feature.csv'
    with open(out_file_name, mode='w', encoding='utf-8') as fout:
        writer = csv.writer(fout, lineterminator='\n')
        # 8 columns
        csv_header = ['index', 'original_string', 'head_validity', 'tail_validity', 'middle_validity',
                  'linking_validity', 'repetition', 'is_family_name']
        writer.writerow(csv_header)

        # Calc クラスの利用／MongoDB のコレクション名を指定
        calcf = Calc('fmlname_agg')

        # get a vector of features
        for orig_data in original_data_list:
            orig_str = orig_data[1]
            row_data = [orig_data[0], orig_str]  # "index", "original_string"
            feature_list = calcf.gen_feature_list(orig_str)    # get 5 features
            row_data += feature_list
            row_data.append(orig_data[2])    # Add Label

            writer.writerow(row_data)
            row_data.clear()

        calcf.close()


if __name__ == '__main__':
    main()
