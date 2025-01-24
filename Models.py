# -*- coding: utf-8 -*-
"""6182101013_Soal1

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1BLwBsVNkljlYxGKOyi_K1-dYlaw03qSp

#Soal 1

## Import Library dan Dataset yang Diperlukan
"""

import pandas as pd
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import chi2, SelectKBest
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
test_bank = pd.read_csv("test_bank.csv")
train_bank = pd.read_csv("train_bank.csv")

"""## Tahap 1 : Eksplorasi dan Pembersihan Data"""

#fungsi preproses data
def preprocess (data):
  label_encoder = LabelEncoder()
  for column in data:
      if data[column].dtype in ['object']:
       data[column] = label_encoder.fit_transform(data[column])
       print(f"Mapping untuk kolom  non numerik{column}: {dict(enumerate(label_encoder.classes_))}")

      # non numerics have label now
       invalid_values = data[data[column] < 0]
       print(f"Distribusi kolom numerik {column}:")
       print(data[column].value_counts(), "\n")
       print(f"Nilai minimum untuk kolom numerik {column}:")
       print(data[column].min(skipna=True), "\n")
       print(f"Nilai maksimum untuk kolom numerik {column}:")
       print(data[column].max(skipna=True),"\n")

       if not invalid_values.empty:
           print(f"Nilai tidak valid pada kolom {column}:")
           print(invalid_values, "\n")

test_bank.describe()
test_bank.info()
train_bank.describe()
train_bank.info()

preprocess(train_bank)
preprocess(test_bank)

"""Preproses sudah dilakukan dan data siap dipakai, kolom numerik sudah dimapping sehingga sudah menjadi kolom numerik. Tidak ada value data yang didrop atau diubah karena valuenya salah (misalnya ada nilai minus pada kolom yang seharusnya tidak minus)."""

test_bank.describe()
test_bank.info()
train_bank.describe()
train_bank.info()

"""##Tahap 2 : Pembuatan Model Klasifikasi Dengan Algoritma Decision Tree

### Eksperimen pemilihan fitur (kolom) terbaik
"""

x = train_bank.drop(columns=['Exited', 'id', 'CustomerId'])
y = train_bank['Exited']

x_test = test_bank.drop(columns=['Exited', 'id', 'CustomerId'])
y_test = test_bank['Exited']

accuracy_scores_by_k ={}

for k in range(1, 12):
    # Pilih k fitur terbaik berdasarkan Chi-Square
    selector = SelectKBest(chi2, k=k)
    x_selected = selector.fit_transform(x, y)
    top_columns = x.columns[selector.get_support()]
    print(f"Jumlah fitur terpilih (k={k}):", top_columns.tolist())
    # Terapkan fitur yang dipilih ke dataset uji
    x_test_selected = selector.transform(x_test)

    # Buat model Decision Tree
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(x_selected, y)

    # Prediksi data uji
    y_pred = dt_model.predict(x_test_selected)

    # Evaluasi model
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    print("Accuracy:", accuracy)
    print("\nClassification Report:")
    print(report)

    accuracy_scores_by_k[(k)] = (top_columns,accuracy)

# print (accuracy_scores_by_k)
res = sorted(accuracy_scores_by_k.items(), key=lambda x: x[1][1], reverse=True)

best_k , (best_col, best_accuracy) = res[0]

print ('Model terbaik berdasarkan accuracy :')
print (f'Jumlah Atribut Terbaik = {best_k}')
print (f'Dengan Kolom Atribut Terbaik = {best_col}')
print (f'Dengan Accuracy Terbaik = {best_accuracy}')

"""Kesimpulan :

Model terbaik berdasarkan akurasi

Jumlah Atribut Terbaik : 10

Dengan Kolom Atribut Terbaik  (yang diurutkan berdasarkan chi2):
1. 'Surname'
2. 'CreditScore'
3. 'Geography'
4. 'Gender'
5. 'Age'
6. 'Tenure'
7. 'Balance'
8. 'NumOfProducts'
9. 'IsActiveMember'
10. 'EstimatedSalary'

Dengan Accuracy Terbaik = 0.7985408972573712

### Pembuatan Model dengan Fitur terbaik
"""

best_columns = ['Surname', 'CreditScore', 'Geography', 'Gender', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'IsActiveMember', 'EstimatedSalary']
x_selected= train_bank[best_columns]
y = train_bank['Exited']

x_test_selected = test_bank[best_columns]
y_test = test_bank['Exited']


# Buat model Decision Tree
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(x_selected, y)
# Prediksi data uji
y_pred = dt_model.predict(x_test_selected)
# Evaluasi model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
print("Accuracy:", accuracy)
print("\nClassification Report:")
print(report)

"""Kesimpulan :
- Akurasi global = 0.7985408972573712

- **Kelas terbaik berdasarkan F1-Score**: Kelas 0 (No Exit) dengan f1-score: 0.87
- **Kelas terburuk berdasarkan F1-Score**: Kelas 1 (Exited) dengan f1-score: 0.53

## Tahap 3 : Random Forest

Berdasarkan model dt tersebut, dapatkan terlebih dahulu hyper paramsnya, berikut ini adalah hasilnya:
1. max depth = none, yang berarti pohon tidak dibatasi dalamnya. pohon akan tetap terus bertambah dalamnya sampai didapatkan seluruh node leafnya terdiri dari hanya satu kelas.
2. min sample split = 2, yang artinya pohon akan tetap mencoba split sebuha node jika terdapat minimal 2 sample, sehingga pohon akan tetap bertambah panjang dalamnya hingga tedapat kurang dari 2 sample pada leafnya. hal ini dapat membuat model lebih terhidanr dari under fit
3. min sample leaf = 1, yang artinya harus ada minmal 1 sample pada setiap node. hal ini akan membuat pohon akan terus bertmabh panjang dalamnya dan mencegah under fit
"""

dt_max_depth = dt_model.get_params()['max_depth']
dt_min_samples_split = dt_model.get_params()['min_samples_split']
dt_min_samples_leaf = dt_model.get_params()['min_samples_leaf']

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
max_depths = [dt_max_depth, 5, 10]
min_samples_splits = [dt_min_samples_split, 10, 20]
min_samples_leafs = [dt_min_samples_leaf, 10, 15]

best_accuracy = 0
best_params = None
for max_depth in max_depths:
  for min_samples_split in min_samples_splits:
    for min_samples_leaf in min_samples_leafs:
      # rf model use dt hyperparam
      rf_model = RandomForestClassifier(
          n_estimators=100,  # Number of trees in the Random Forest
          max_depth = max_depth,
          min_samples_split = min_samples_split,
          min_samples_leaf = min_samples_leaf,
          random_state=42
      )

      rf_model.fit(x_selected, y)

      y_pred_rf = rf_model.predict(x_test_selected)

      accuracy_rf = accuracy_score(y_test, y_pred_rf)
      report_rf = classification_report(y_test, y_pred_rf)
      conf_matrix_rf = confusion_matrix(y_test, y_pred_rf)

      if  accuracy_rf > best_accuracy:
        best_accuracy = accuracy_rf
        best_params = (max_depth, min_samples_split, min_samples_leaf)
      # Print results
      print ("-----------------")
      print (f"max_depth = {max_depth}, min_samples_split = {min_samples_split}, min_samples_leaf = {min_samples_leaf}")
      # Print evaluation metrics
      print("Accuracy (Random Forest):", accuracy_rf)
      print("\nClassification Report (Random Forest):")
      print(report_rf)
      print("\nConfusion Matrix (Random Forest):")
      print(conf_matrix_rf)

print (best_accuracy)
print (best_params)

"""Kesimpulan : setelah dilakukan eskplorasi didapatkan sebuah model RF terbaik berdasarkan akurasinya yaitu ** 86,29%** , dengan param max_depth = 10, min_samples_split = 2, min_samples_leaf = 1. Dibandingkan dengan akurasi dt yaitu **79.85%**

# 4. Pemanfaatan Model

## Train model sesuai hyper param terbaik yang sudah didapatkan sebelumnya
"""

rf_model = RandomForestClassifier(
          n_estimators=100,  # Number of trees in the Random Forest
          max_depth = 10,
          min_samples_split = 2,
          min_samples_leaf = 1,
          random_state=42)

rf_model.fit(x_selected, y)

"""## Data baru

"""

data = [
    {"id": 91, "CustomerId": 15579526, "Surname": "Niu", "CreditScore": 743, "Geography": "Germany", "Gender": "Male", "Age": 37.0, "Tenure": 2, "Balance": 132627.51, "NumOfProducts": 1, "HasCrCard": 1.0, "IsActiveMember": 0.0, "EstimatedSalary": 183566.87, "Exited": 0},
    {"id": 92, "CustomerId": 15623082, "Surname": "Ndukaku", "CreditScore": 726, "Geography": "France", "Gender": "Female", "Age": 26.0, "Tenure": 5, "Balance": 0.0, "NumOfProducts": 2, "HasCrCard": 1.0, "IsActiveMember": 0.0, "EstimatedSalary": 52449.97, "Exited": 0},
    {"id": 93, "CustomerId": 15641822, "Surname": "Mironova", "CreditScore": 431, "Geography": "France", "Gender": "Male", "Age": 37.0, "Tenure": 4, "Balance": 0.0, "NumOfProducts": 2, "HasCrCard": 1.0, "IsActiveMember": 1.0, "EstimatedSalary": 171344.06, "Exited": 0},
    {"id": 94, "CustomerId": 15756875, "Surname": "Johnston", "CreditScore": 571, "Geography": "France", "Gender": "Female", "Age": 50.0, "Tenure": 4, "Balance": 0.0, "NumOfProducts": 1, "HasCrCard": 1.0, "IsActiveMember": 0.0, "EstimatedSalary": 145567.36, "Exited": 0},
    {"id": 95, "CustomerId": 15791534, "Surname": "Scott", "CreditScore": 588, "Geography": "Germany", "Gender": "Male", "Age": 30.0, "Tenure": 10, "Balance": 126683.4, "NumOfProducts": 1, "HasCrCard": 1.0, "IsActiveMember": 1.0, "EstimatedSalary": 131636.55, "Exited": 0},
    {"id": 96, "CustomerId": 15671139, "Surname": "Shih", "CreditScore": 659, "Geography": "Spain", "Gender": "Female", "Age": 39.0, "Tenure": 0, "Balance": 107042.74, "NumOfProducts": 1, "HasCrCard": 1.0, "IsActiveMember": 0.0, "EstimatedSalary": 102284.2, "Exited": 0},
]

# value EXITEDnya 0, tetapi tidak berarti tergabung ke kelas 0, hanya default inisialisasi

data = pd.DataFrame(data)
preprocess(data)

"""
## Hasil Prediksi"""

best_columns = ['Surname', 'CreditScore', 'Geography', 'Gender', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'IsActiveMember', 'EstimatedSalary']
data_selected = data[best_columns]

y = rf_model.predict(data_selected)
data['Exited'] = y
print(data)