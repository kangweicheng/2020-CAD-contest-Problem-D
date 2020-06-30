## 2020-CAD-contest-Problem-D

B05901082 楊晟甫 B05505028 康惟誠

### 1. Prerequisites

- basic ML packages: sklearn, pandas, numpy
- pytorch
- lightgbm

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

To generate processed metadata, please modify the path of metadata and the path of cell libraries in data/preprocess.py and execute:

```bash
$ python3 preprocess.py
```





