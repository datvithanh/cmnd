TRAIN=2000
VALID=200

rm -rf data/train 
rm -rf data/valid
mkdir data/train
mkdir data/valid
python3 text_draw.py -t $TRAIN -v $VALID