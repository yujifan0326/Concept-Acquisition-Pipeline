path="bert-model/"
if [ ! -d ${path} ]; then
  mkdir ${path}
  wget -P ${path} https://storage.googleapis.com/bert_models/2018_10_18/uncased_L-12_H-768_A-12.zip
  wget -P ${path} https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip
  unzip -d ${path} ${path}uncased_L-12_H-768_A-12.zip
  unzip -d ${path} ${path}chinese_L-12_H-768_A-12.zip
fi
if [ ! -d "tmp/" ]; then
  mkdir tmp/
fi
path="data"
if [ ! -d "data/" ]; then
  mkdir data/
  wget http://lfs.aminer.cn/misc/moocdata/toolkit/data.zip
  unzip data.zip
fi
pip install -r requirements.txt
python init.py

