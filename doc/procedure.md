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
1. 【機械学習】family_name_learning.py の実行

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
