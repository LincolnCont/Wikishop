#!/usr/bin/env python
# coding: utf-8

# <h1>Содержание<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Подготовка" data-toc-modified-id="Подготовка-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Подготовка</a></span></li><li><span><a href="#Обучение" data-toc-modified-id="Обучение-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Обучение</a></span><ul class="toc-item"><li><span><a href="#Логичстическая-регрессия" data-toc-modified-id="Логичстическая-регрессия-2.1"><span class="toc-item-num">2.1&nbsp;&nbsp;</span>Логичстическая регрессия</a></span></li><li><span><a href="#Дерево-решений" data-toc-modified-id="Дерево-решений-2.2"><span class="toc-item-num">2.2&nbsp;&nbsp;</span>Дерево решений</a></span></li><li><span><a href="#Cлучайный-лес" data-toc-modified-id="Cлучайный-лес-2.3"><span class="toc-item-num">2.3&nbsp;&nbsp;</span>Cлучайный лес</a></span></li><li><span><a href="#LightGBM" data-toc-modified-id="LightGBM-2.4"><span class="toc-item-num">2.4&nbsp;&nbsp;</span>LightGBM</a></span></li><li><span><a href="#XGBoost" data-toc-modified-id="XGBoost-2.5"><span class="toc-item-num">2.5&nbsp;&nbsp;</span>XGBoost</a></span></li><li><span><a href="#Анализ-полученных-метрик-и-выбор-модели:" data-toc-modified-id="Анализ-полученных-метрик-и-выбор-модели:-2.6"><span class="toc-item-num">2.6&nbsp;&nbsp;</span>Анализ полученных метрик и выбор модели:</a></span></li></ul></li><li><span><a href="#Выводы" data-toc-modified-id="Выводы-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Выводы</a></span></li><li><span><a href="#Чек-лист-проверки" data-toc-modified-id="Чек-лист-проверки-4"><span class="toc-item-num">4&nbsp;&nbsp;</span>Чек-лист проверки</a></span></li></ul></div>

# # Проект для «Викишоп»

# Интернет-магазин «Викишоп» запускает новый сервис. Теперь пользователи могут редактировать и дополнять описания товаров, как в вики-сообществах. То есть клиенты предлагают свои правки и комментируют изменения других. Магазину нужен инструмент, который будет искать токсичные комментарии и отправлять их на модерацию. 
# 
# Обучите модель классифицировать комментарии на позитивные и негативные. В вашем распоряжении набор данных с разметкой о токсичности правок.
# 
# Постройте модель со значением метрики качества *F1* не меньше 0.75. 
# 
# **Инструкция по выполнению проекта**
# 
# 1. Загрузите и подготовьте данные.
# 2. Обучите разные модели. 
# 3. Сделайте выводы.
# 
# Для выполнения проекта применять *BERT* необязательно, но вы можете попробовать.
# 
# **Описание данных**
# 
# Данные находятся в файле `toxic_comments.csv`. Столбец *text* в нём содержит текст комментария, а *toxic* — целевой признак.

# ## Подготовка

# In[1]:



import pandas as pd
import matplotlib.pyplot as plt 
plt.style.use('seaborn-pastel')
import seaborn as sns 
import numpy as np 
import warnings
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as nltk_stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize


import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV
import lightgbm as lgb
import xgboost as xgb
from sklearn.metrics import f1_score

from time import time
from tqdm import tqdm

pd.options.display.max_columns = None
warnings.filterwarnings("ignore")


# In[ ]:





# 
# <div class="alert alert-success">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# Успех:
# 
# Собираем все импорты в верхней части, чтобы легче было ориентироваться и добавлять новые по необходимости. 
# 
#  
# <div class="alert alert-warning">
# 
# 
# Совет:
# 
#     
#     
# - у тебя тут есть лишние импорты, то что ты не использовано или использовано не верно - стоит убрать, чтобы поберечь ресурсы      
#  
#  
#  
# 
# - есть рекомендации PEP-8 при написании кода, в том числе и для импортов. Если интересно можешь почитать [тут](https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html). Есть что поправить 
# 
# 

# In[19]:


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

stopwords = set(nltk_stopwords.words('english'))


# In[20]:


df = pd.read_csv('/datasets/toxic_comments.csv')
df.head()


# <div class="alert alert-warning">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# Совет: 
# 
# 
# Если не знаешь - чтобы не было столбца  `Unnamed: 0` при чтении файла можно так:
# 
# 
#     pd.read_csv(..., index_col=0)
# 
#     
# (`Unnamed: 0` появляется при не совсем корректном сохранении файла)    
# 
# 
# Unnamed: 0 это "след" старых индексов. Если ты уберёшь первые 10 примеров и своего датасета, сохранишь его, а потом откроешь,  то появится столбец Unnamed: 0 начиная с цифры 9, и появится новый индексы начиная с нуля 
# 
# 
# Но это мелочь,  даже не нужно ничего исправлять. Просто знай, чтобы увидев такое в чужом коде не удивляться что бы это могло означать

# In[21]:


df.info()


# Согласно документации к данным, cтолбец text содержит текст комментария, а toxic — целевой признак.
# 

# In[22]:


df.isna().sum()


# In[23]:


df['text'].duplicated().sum()


# В датасете нет пропусков и дубликатов
# 
# Изучим сблансированность данных

# In[24]:


df['toxic'].hist()


# <div class="alert alert-warning">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# Совет 🤔:
# 
# 
# - Если хочешь убрать <AxesSubplot:>.  то ставь в конце `;` или пропиши plt.show()
# 
# - Не   правильно для категориальных значений использовать гистограмму

# Данные имееют дисбаланс.
# 
# Создадим функцию, которая очистит текст для будущей лемматизации:

# <div class="alert alert-success">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# Успех:
# 
#  
#     
# 
# -  проверку на сбалансированность 
# 
# 
# 
# - промежуточный вывод в конце раздела
# 
#  
# 
# <div class="alert alert-warning">
# 
# Совет: 
# 
# 
#  
# 
# - можно также посчитать количество слов в предложений,  длину слов в твите, опять же в разбивке по Таргету.  Если будут какие-то сильные отличия, возможно из-за этого стоит сгенерировать дополнительные признаки для наших моделей. Или например можно использовать библиотеку SentimentIntensityAnalyzer для оценки сантиментов, и посмотреть насколько хорошо ее оценки корелирует с нашими таргетами
#    
#    
# - когда мы работаем с текстами, describe итп описательные статистике не использовать, но можно провести частотный анализ текста.  Предлагаю для этого использовать [облако слов](https://habr.com/ru/post/517410/) - чтобы получить общее представление о тематике и о наиболее часто встречаемых словах в токсичных и нетоксичных твитах (в облаке уже автоматически будут убраны стоп слова). Кроме того графики, рисунки делают проект визуально интересней
#    
#    
# В тренажере облако импортируем так
# 
#     !/opt/conda/bin/python -m pip install wordcloud 
# 
# 
# или
# 
#     !/opt/conda/bin/python -m pip install wordcloud==1.8.2.2  
# 
# 
# И возможно дополнительно надо будет сделать
# 
# 
# 
#     !pip install --upgrade Pillow  (попробуй версию 9.5.0)
# 
#   
# 

# In[25]:


def clear_text(text):
    text = re.sub(r'[^a-zA-Z ]', ' ', text.lower()) 
    retext = text.split() 
    text = " ".join(retext)
    return text


# Создадим функцию для тоекнизации и лемматизации текста:

# In[ ]:





# In[27]:


def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


# In[28]:


nltk.download('stopwords')
stopwords = set(nltk_stopwords.words('english'))


# In[29]:


lemmatizer = WordNetLemmatizer()


# In[30]:


def lemmetize(text):
    
    token = nltk.word_tokenize(text)
    text = [word for word in token if word not in stopwords]
    text = ' '.join([lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in text])
    
    return text


# <span style="background-color: #FFFF00">Сделал и проверил на датасете из 10 строк</span>
# 
# 

# In[31]:





# Воспользуемся функциями и посмотрим результат:

# In[32]:


df['lemm_text'] = df['text'].apply(clear_text)
df['lemm_text'] = df['lemm_text'].apply(lemmetize)

df['lemm_text']


# <div class="alert alert-success">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# Успех:
# 
# 
#  
# - Плюс за использование apply, неэффективные циклы нам ни к чему.
# 
# 
# - Да, всегда лучше проверить что получилось  в итоге, так всегда будет возможность поправить ошибку
# 
# <div class="alert alert-warning">
# 
# 
# Совет: 
# 
# 
#     
# - попробуй .progress_apply, делает что .apply, но еще и показывает на какой итерации находится процесс.  
# 
# Для некоторых версий, чтобы заработал .progress_apply предварительно нужно сделать:
#     
#     
#     from tqdm.notebook import tqdm
#     tqdm.pandas()
#     
# 
# И cудя по всему импорты нужно засунуть внутрь функции
# 
# То же самое делает .swifter.apply  Предварительно
# 
# 
#     !pip install swifter
#     import swifter
# 
# 
# 
# - если  процесс лемматизации затягивается, можно попробовать [.parallel_apply](https://pypi.org/project/pandarallel/), для WordNetLemmatizer это работает точно (для spacy у меня не получлось, но там есть своя, встроенная схема парализации расчётов через pipline). Кому-то это помогает уменьшить время прогона кода раз в 5-7 (Хотя студенты начинают жаловаться что получается даже медленнее). Но попробовать стоит

# Чтобы алгоритмы умели определять тематику и тональность текста, их нужно обучить на корпусе (англ. corpus). Это набор текстов, в котором эмоции и ключевые слова уже размечены.
# 
# Разделим датасет на тестовую и тренировочную выборку, размер тестовой выборки - 20% от общих данных:

# In[14]:


train_features, test_features, train_target, test_target = train_test_split(
    df.drop('toxic', axis=1),
    df['toxic'],
    test_size=0.2,
    random_state=12345,
    stratify=df['toxic'] 
)


corpus_train = train_features['lemm_text']
corpus_test = test_features['lemm_text']
corpus_train


# Воспользуемся TfidfVectorizer и, чтобы почистить мешок слов, добавим в него стоп-слова:

# In[15]:


count_tf_idf = TfidfVectorizer(stop_words=stopwords) 
tf_idf_train = count_tf_idf.fit_transform(corpus_train) 
tf_idf_test = count_tf_idf.transform(corpus_test) 

print("Размер матрицы:", tf_idf_train.shape)
print("Размер матрицы:", tf_idf_test.shape)


# Обработка данных выполнена, TF-IDF подсчитано, можно приступить к обучению модели:

# ## Обучение

# Воспользуемся несколькими моделями машинного обучения:
# 
# - Линейная регрессия
# - Дерево решений
# - Случайный лес
# - Градиентный бустинг
# 
# Создадим функцию, которая обучит и вернет модель, а так же заполнит таблицу для анализа метрик:

# In[16]:



analisys = pd.DataFrame({'model':[], 'F1_model':[], 'F1_on_train':[]})
all_models = []


def train_model(model, parameters):
    
    model_random = RandomizedSearchCV(
        estimator=model,
        param_distributions=parameters,
        scoring='f1', 
        n_jobs=-1,
        cv=4, 
        verbose=2
        random_state=45
    )
    
   
    start = time()
    model_random.fit(tf_idf_train, train_target)
    print('RandomizedSearchCV подбирал параметры %.2f секунд' %(time() - start))
    
   
    f1 = model_random.best_score_
    f1_on_train = f1_score(train_target, model_random.predict(tf_idf_train))
    
    print('Лучшие параметры:', model_random.best_params_)
    print('F1 обученной модели:', f1)
    print('F1 на тренировочной выборке:', f1_on_train)

     
    all_models.append(model_random)
    row = []
    row.extend([model, f1, f1_on_train])
    analisys.loc[len(analisys.index)] = row
    
    return model_random


# <div class="alert alert-success">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# Успех:
# 
# 
# 
# 
# 
# 
# Корректно использован RandomizedSearchCV. Есть и другие варианты, тюнинга гиперпараметров, можешь [ознакомиться](https://www.freecodecamp.org/news/hyperparameter-optimization-techniques-machine-learning/). Выделю оptuna, очень много плюсов, причем изучение можно начать с [**OptunaSearchCV**](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.integration.OptunaSearchCV.html). Интерфейс практически такой же, как у GridSearchCV, поэтому очень легко начать пользоваться
# 
#  
# 
#  
# 
# 
#     
# 
# <div class="alert alert-warning">
# 
# 
# 
# 
# 
# Совет: 
# 
#  
# Молодец что используешь GridSearch, но еще лучше использовать связку GridSearchCV/RandomizedSearchCV + pipeline. 
# 
# 
# О pipeline:
# 
# [Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html), это тема которая сразу затрагивает кроссвалидацию, тюнинг "векторайз", подбор гиперпараметров модели и о том что код стоит делать компактным.
#     
#     
# - в TfidfVectorizer(stop_words=stopwords) у тебя по умолчанию ngram_range=(1, 1), тут можно подбирать разное число n- грамм (и другие параметры), максимизируя метрику, но как объединить перебор по ngram_range с обучением моделей, чтобы не делать это по отдельности или с использованием цикла?! pipeline! Готовый [пример для работы с текстами](https://medium.com/@yoni.levine/how-to-grid-search-with-a-pipeline-93147835d916). Всё что нужно там есть, хотя очень лаконично. Можешь погуглить по:
# 
# 
#     
#     pipeline nlp gridsearchcv
# 
# 
# 
# - как избежать ошибки подглядывания в будущее, когда мы предварительно работаем с данными (шкалирование, нормализация, TfidfVectorizer итп итд)? pipeline! особенно это важно, когда мы используем кроссвалидацию. Для TfidfVectorizer делаем .fit (обучаемся) на train, а transform на test, но точно также нужно сделать для валидационной выборки. Но GS делает валидационные внутри себя, спрашивается как добраться до нее и избежать подглядывания в будущее? Казалось бы никак, но нет! Pipeline! ) 
#     
#     
# - pipeline позволяет делать наш код компактней и читабельней, это большой плюс, когда код будет раздуваться     
#     
#     
# 
#          
# Если раньше не использовал pipeline то могу посоветовать видео в котором [индус](https://www.youtube.com/watch?v=mOYJCR0IDk8&ab_channel=HimanshuChandra) на английском с сильным акцентом, но на пальцах обьясняет  самое непонятное (по моему опыту): сопряженность методов fit и transform. Там же есть и код и ссылка на текст. Мне помогло )
# 
# 
# 
# В общем если сделать RS+pipeline будет вообще хорошо )  
#     
# <div>   

# ### Логичстическая регрессия

# In[17]:


ran_lr = {
    "penalty": ['l1', 'l2', 'elasticnet', 'none'],
    "class_weight": ['balanced', 'none'],
}

logr = LogisticRegression(max_iter=300)

lr_random = train_model(logr, ran_lr)


# ### Дерево решений 

# In[18]:


ran_grid_tree = {
    "max_depth": list(range(45, 56))
}

dtr = DecisionTreeClassifier()

dtr_random = train_model(dtr, ran_grid_tree)


# ### Cлучайный лес 

# In[19]:


ran_grid_forest = {
    'max_depth': [300, 310],
    'n_estimators': [12, 14],
}

rfc = RandomForestClassifier(n_jobs=-1)

rfc_random = train_model(rfc, ran_grid_forest)


# ### LightGBM

# In[20]:


rand_lgbm_param = {
    'max_depth': [15, 25],
    'learning_rate': [0.1, 0.3]
}

gbm = lgb.LGBMClassifier(
    boosting_type='gbdt',
    n_jobs=-1
)

gbm_random= train_model(gbm, rand_lgbm_param)


# ### XGBoost

# In[21]:


rand_xgb_param = {
    'max_depth': [6, 7, 8, 9],
    'learning_rate': [0.5, 1.0]
}

xb = xgb.XGBClassifier(booster='gbtree', 
                      use_rmm=True,
                      n_jobs=-1)

xb_random = train_model(xb, rand_xgb_param)


# ### Анализ полученных метрик и выбор модели:

# In[22]:


all_names = pd.DataFrame({'names':[ 'LogisticRegression', 'DecisionTree', 'RandomForest', 'LightGBM', 'XGBoost']})
analisys = pd.concat([analisys, all_names], axis=1, join='inner')
display(analisys)

analisys.plot.bar(y='F1_model', x='names', rot=45, figsize=(15,7), color='orange')
plt.title('Сравнение метрик моделей', fontsize='x-large')
plt.xlabel('Модель')
plt.show()

analisys.plot.bar(y='F1_on_train', x='names', rot=45, figsize=(15,7), color='green')
plt.title('Сравнение метрик на тренировочной выборке', fontsize='x-large')
plt.xlabel('Модель')
plt.show()


# Исходя из полученных метрик качества моделей, лучшая модель на RandomizedSearchCV - LightGBM c параметрами max_depth: 25, learning_rate: 0.3. На тренировочной выборке, лучшую метрику показывает модель Случайного леса, но и худшую на подборе параметров, то есть модель переобучена и не показывает нужных метрик.

# <div class="alert alert-success">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# 
# 
# Успех 👍:
# 
# 
# 
# Наглядно. 
#     
# (Вообще Случайный лес не склонен переобучению,  Даже интересно почему так получилось)
# 
# 
#  

# ## Выводы

# In[23]:


predicted = xb_random.predict(tf_idf_test)
print('F1 лучшей модели на тестовой выборке:', f1_score(test_target, predicted))


# <div class="alert alert-success">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# Успех: 
# 
# - Все верно, логика моделирования не нарушена, тут тестируем только лучшую модель отобранную на валидации, или парочку лучших, если на валидации результаты близки
# 
#  
# 
# - Если студент получил на тесте f1 выше 0,75, это считается приемлемым результатом.
# 
# 
# <div class="alert alert-warning">
# 
# 
# 
# Совет: 
# 
#  
# 
# 
# - можно поиграться [порогом](https://machinelearningmastery.com/threshold-moving-for-imbalanced-classification/). Таким образом можно поднять метрику на процент - полтора
#    
# 
#  
#     
#  
# 
#     
#  - полезно настраивать векторайзеры  (тут пригодится pipeline). Это конечно потребует вычислительных мощностей, ведь если даже использовать биграммы число признаков резко увеличится
# 
# 
#       
# 
#     
# - попробовать другие модели. проект своеобразный выбор между вычислительными ограничениями (много примеров, расчеты могут затянуться) и задачей получить хорошую метрику. С этой точки зрения  интересная [моделька](https://medium.com/geekculture/passive-aggressive-algorithm-for-big-data-models-8cd535ceb2e6) (открывается с помощью VPN) [или](https://datafinder.ru/products/passivno-agressivnyy-klassifikator-v-mashinnom-obuchenii). Она считается очень шустрой     
#     
# 
# 
# - использование предбученной модели Берта, выбрав соответствующую модель и используя полученные эмбединги, даже на небольшом тренировочном датасете можно обучить модель, которая на test покажет хорошую метрику. В этом случаи можно сразу получить метрику > 0.95 (при правильно выбранной модели)
# 
# 
# 

# 
# 
# 
# <div class="alert alert-warning">
# <font size="5"><b>Комментарий ревьюера</b></font>
# 
# 
# Совет: 
# 
# 
# А ещё можешь посмотреть какие слова  является наиболее важным для классификации с точки зрения модели. Получаем список слов    
#     
#     
#     
#     .get_feature_names_out().tolist()
#     
#     
#     
# Получаем коэффициенты важности (для логистической регрессии)    
#     
#     .coef_.tolist()[0]
# 
# 
# 
# 
#  
# 
# А потом можно построить такой-то красивый график с помощью     seaborn
# 
# 

# В данном проекте нам необходимо было обучить модель классифицировать комментарии на позитивные и негативные с помощью размеченных данных. Пороговое значение метрики качества F1 - 0.75.
# 
# На этапе подготовки корпуса нами была проведена очистка, токенизация, лемматизация
# 
# Необходимые метрики достигнуты, модель LightGBM, обученная через RandomizedSearchCV, предсказывает с необходимой метрикой: F1 > 0.75.

# In[ ]:





# ## Чек-лист проверки

# - [x]  Jupyter Notebook открыт
# - [ ]  Весь код выполняется без ошибок
# - [ ]  Ячейки с кодом расположены в порядке исполнения
# - [ ]  Данные загружены и подготовлены
# - [ ]  Модели обучены
# - [ ]  Значение метрики *F1* не меньше 0.75
# - [ ]  Выводы написаны
