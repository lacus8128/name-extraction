# -*- coding: utf-8 -*-

"""
特徴量を含んだ csv ファイルを読み込んで学習を行う
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib


# 特徴量データの読み込み
feature_file = 'family_name_feature.csv'
fmlname_data = pd.read_csv(feature_file, encoding='utf-8')

# データセットを特徴量とラベルに分ける
y = fmlname_data.loc[:,'is_family_name']
x = fmlname_data.loc[:, ['head_validity','tail_validity','middle_validity','linking_validity','repetition']]

# 学習用データとテスト用データに分離（1:4 の比率）
x_train, x_test, y_train,  y_test = train_test_split(x, y, test_size = 0.2, train_size = 0.8, shuffle = True)

# 学習 classifier
clf = SVC( C=1, kernel='linear', max_iter=-1, probability=False, random_state=None,
           shrinking=True, verbose=False)
clf.fit(x_train, y_train)

# 正解率の評価
y_pred = clf.predict(x_test)
print("[family_name] Accuracy = " , accuracy_score(y_test, y_pred))

# モデルを .pkl ファイルとして保存する
joblib.dump(clf, 'fmlname_model.pkl')
