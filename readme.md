## 2020-CAD-contest-Problem-D

B05901082 楊晟甫 B05505028 康惟誠

### 1. Prerequisites

- basic ML packages: sklearn, pandas, numpy

- pytorch

- lightgbm

- Download the data from the following link and place under the corresponding directory:

- data/train/

  

- data/test/

  
### 2. Directory

```
# place the cell library in the correct folder
.
├── data/
|   ├── read.py
|   ├── parse.py
|   ├── preprocess.py
|   ├── train/
|		├── *.lib
|		├── power.csv
|		└── timing.csv
|   └── test/
|		├── *.lib
|		├── power.csv
|		└── timing.csv
├── config/
|   └── *.yaml/
├── saved/
└── train.py
```

### 3. Usage

To generate processed metadata, please execute the following command:
```bash
$ cd data/
$ python3 preprocess.py
```
To execute the linear regression example, please execute the following command:
```bash
# timing.yaml or power.yaml
$ python3 linear_regression.py --cfg_path config/timing.yaml
```
To execute the lightgbm example, please execute the following command:
```bash
# timing.yaml or power.yaml
# if grid search is desired, please use the grid_search flag
$ python3 lgbm.py --cfg_path config/timing.yaml --gid_search
```
To perform training on our model, please execute the following command:
```bash
# timing.yaml or power.yaml
$ python3 train.py --cfg_path config/timing.yaml
````
After training, you may want to perform testing on some checkpoint
```bash
$ python3 train.py --cfg_path config/timing.yaml --checkpoint your_ckpt_path --eval_only
```