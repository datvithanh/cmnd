TRAIN=5
VALID=3

rm -rf data/train 
rm -rf data/valid
mkdir data/train
mkdir data/valid
python3 text_draw.py -t $TRAIN -v $VALID