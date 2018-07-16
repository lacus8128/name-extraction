# -*- coding: utf-8 -*-

"""
最善のハイパーパラメータを選択するため、グリッドサーチを行う
（モデルとしては SVM を使用。クロスバリデーションも実行）
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV


# 特徴量データの読み込み
feature_file = 'family_name_feature.csv'
fmlname_data = pd.read_csv(feature_file, encoding='utf-8')

# データセットを特徴量とラベルに分ける
y = fmlname_data.loc[:,'is_family_name']
x = fmlname_data.loc[:, ['head_validity','tail_validity','middle_validity',
                         'linking_validity','repetition']]

# 学習用データとテスト用データに分離（1:4 の比率）
x_train, x_test, y_train,  y_test = train_test_split(x, y, test_size = 0.2,
                                          train_size = 0.8, shuffle = True)

# グリッドサーチで利用する候補パラメータ群
parameters = [
    {"C": [1,10,100,1000], "kernel":['linear']},
    {"C": [1,10,100,1000], "kernel":['rbf'], "gamma": [0.001, 0.0001]},
    {"C": [1,10,100,1000], "kernel":['poly'], "degree": [2,3,4], "gamma": [0.001, 0.0001]},
    {"C": [1,10,100,1000], "kernel":['sigmoid'], "gamma": [0.001, 0.0001]}
]

# グリッドサーチを実行
kfold_cv = KFold(n_splits=5, shuffle=True)
clf = GridSearchCV( estimator=SVC(), param_grid=parameters, cv=kfold_cv, verbose=False )
clf.fit(x_train, y_train)

# 最適なパラメータを表示
print('Best Parameters :')
print(clf.best_params_)

# 最適なパラメータで評価した際の正解率を表示
y_pred = clf.predict(x_test)
print('Accuracy of the best model :')
print(accuracy_score(y_test, y_pred))
