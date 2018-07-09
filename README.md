# name-extraction
extract people's name by using machine learning


## プログラムの内容
文字列を読み込み、人名を判定する。  
（ただし現在、日本人の名字のみが対象）

人名か否かを示すラベルが付いたデータを元に特徴量データを生成し、  
特徴量データを SVM で学習させ、人名か否かを判定する処理を行う。
