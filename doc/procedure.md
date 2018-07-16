# プログラムの動作手順書

> since: July 2018

## 必要なもの
* Python3 （v3.6.3）
* Python モジュール（機械学習・MongoDB）
    * scikit-learn （v0.19.1）
    * pandas （v0.23.1）
    * pymongo （v3.7.0）
* MongoDB （v3.6.2）


## 手順
下記手順は、Python3 および MongoDB をインストールし、  
必要な Python のモジュールをインストールした上で行うものである。  

1. MongoDB の立ち上げ（mongod を実行）
1. aggregate.py の実行
1. 【特徴量データ生成】preprocess.py の実行
1. 【学習】family_name_learning.py の実行
1. 【SVMによる判定】fmlname_extraction.py の実行

family_name_learning.py は、特徴量データの 80% を学習データ、  
残りの 20% をテストデータとして使用する実装となっている。

下記のような出力（正解率の値）が得られれば成功。  
この例では、正解率が約 98.4% となっている。
```
$ python family_name_learning.py
[family_name] Accuracy =  0.984251968504
```

なお、family_name.csv が元のデータ、  
family_name_feature.csv が特徴量データである。  

このとき、fmlname_model.pkl というファイルが生成されることを確認する。  
最後の fmlname_extraction.py では、このpklファイルから学習モデルを読み込んで利用する。



## 人名／地名 の判定
人名抽出の対象のテキストが記録されたファイル test.txt には、デフォルトで  
「そろそろ、川崎さんが到着するはずだ。」  
というテキストが書かれており、fmlname_extraction.py を実行すると次の出力が得られる。

```
[{'str': '川崎', 'range': [5, 6], 'length': 2, 'class': '名字'}]
```

これは、名字として「川崎」が抽出されたことを示している。  
ただし、test.txt の「川崎さん」の部分を「川崎」に変更すると、`'class': '地名'` と判定されるようになる。  


## 交差検証・グリッドサーチ
grid_search.py は、SVM について交差検証およびグリッドサーチを行うプログラムである。  
本プログラムでは、グリッドサーチの結果として得られたパラメータを family_name_learning.py に使用している。  

