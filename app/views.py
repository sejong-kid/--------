from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Article, InverseTable,ContentInverseTable
from django.forms.models import model_to_dict
import os
from collections import Counter
# !pip install konlpy
from konlpy.tag import Kkma,Okt,Komoran,Hannanum
# Create your views here.
import pandas as pd
import pickle
import operator
from django.db.models import Q 
from functools import reduce
import numpy as np
import keras
from pykospacing import Spacing
import pandas as pd
import pickle
import gensim
import time
from gensim.models.fasttext import FastText
from django.core.paginator import Paginator
with open('data14000_코모란','rb') as f:
    data14000 = pickle.load(f)
with open('14000개꼬꼬마데이타_nouns','rb') as f:
    data14000_train = pickle.load(f)
from more_itertools import locate
import re
import datetime
komoran = Komoran()
kkma = Kkma()
hannanum = Hannanum()
okt = Okt()
all_article_length = len(Article.objects.all())
def index(request):
    return render(request, 'app/index.html')
def search(request):
    key = request.GET.get('key')
    mode = request.GET.get('mode')
    category = request.GET.get('category')
    return render(request, 'app/page2.html',{'key':key,'category':category,'mode':mode})
def read_json(request):
    time_ = time.time()
    key = request.GET.get('key')
    mode = request.GET.get('mode')
    print(mode,'mode')
    날짜기준 = '오늘 / 어제 / 이번 주 / 지난 주 / 이번달 / 지난달 / 2달 전 / 3달 전 / 4달 전 / 5달 전 / 6개월 이상 / 1년 이상'.split(' / ')

    category = request.GET.get('category')
    categorys = ['채용','업체모집','주민의견수렴','교육','행사','의회및시청일정','합격자_당첨_결과']
    if mode !='content':
        mode='title'
    ori_key = key
    today = datetime.datetime.today()
    if key =='':
        if category=='all':
            cc= 1 
            article_list = []
            for i in Article.objects.all():
                date = i.date
                s_date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
                s_date = (today-s_date_).days
                title = i.title
                writer = i.writer
                href = i.href
                if s_date==0:
                    date_ = 날짜기준[0]
                elif s_date==1:
                    date_=날짜기준[1]
                else:
                    w_d = (today-datetime.timedelta(today.weekday())-s_date_).days
                    if w_d<=0:
                        date_=날짜기준[2]
                    elif 0<w_d<8:
                        date_ = 날짜기준[3]
                    else:
                        if (today-datetime.timedelta(today.day-1)-s_date_).days<=0:
                            date_ = 날짜기준[4]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 1):
                            date_=날짜기준[5]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 2):
                            date_=날짜기준[6]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 3):
                            date_=날짜기준[7]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 4):
                            date_=날짜기준[8]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 5):
                            date_=날짜기준[9]
                        elif (today.year, today.month)==ch_calender(s_date_,mode='range',range_=[6,12]):
                            date_=날짜기준[10]
                        else:
                            date_=날짜기준[-1]
                article_dic={'article_num':cc+1,'title':title, 'writer':writer, 'href':href, 'updated':date_,'s_date':s_date}
                article_list.append(article_dic)
                cc+=1
            return JsonResponse(sorted(article_list, key=lambda x:x['s_date']), safe=False)
        else:
            article_list = []
            cc= 1
            for i in Article.objects.filter(채용='1'):
                title = i.title
                writer = i.writer
                href = i.href
                date = i.date
                s_date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
                s_date = (today-s_date_).days
                if s_date==0:
                    date_ = 날짜기준[0]
                elif s_date==1:
                    date_=날짜기준[1]
                else:
                    w_d = (today-datetime.timedelta(today.weekday())-s_date_).days
                    if w_d<=0:
                        date_=날짜기준[2]
                    elif 0<w_d<8:
                        date_ = 날짜기준[3]
                    else:
                        if (today-datetime.timedelta(today.day-1)-s_date_).days<=0:
                            date_ = 날짜기준[4]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 1):
                            date_=날짜기준[5]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 2):
                            date_=날짜기준[6]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 3):
                            date_=날짜기준[7]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 4):
                            date_=날짜기준[8]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 5):
                            date_=날짜기준[9]
                        elif (today.year, today.month)==ch_calender(s_date_,mode='range',range_=[6,12]):
                            date_=날짜기준[10]
                        else:
                            date_=날짜기준[-1]
                article_dic={'article_num':cc+1,'title':title, 'writer':writer, 'href':href, 'updated':date_,'s_date':s_date}
                article_list.append(article_dic)
                cc+=1
            return JsonResponse(sorted(article_list, key=lambda x:x['s_date']), safe=False)
    else:
        key_by_window = []
        key = list(change_key(key).keys())
        key_length = len(key)
        print(key)
        length = all_article_length
        globa_list = []
        score = {}
        for token in key:
            print(1)
            if mode == 'title':
                print('title')
                if len(InverseTable.objects.filter(word=token))==1:
                    record = InverseTable.objects.get(word=token)
                    idf = np.log(length/(1+record.frequency))
                    location=eval(record.location)
                    for x in location:
                        globa=x[0]
                        local = x[1]
                        if globa not in score.keys():
                            globa_list.append(globa)
                            score[globa]=(1+np.log(1+local))*idf
                        else:
                            score[globa]+=(1+np.log(1+local))*idf 
            else:
                print('contetn')
                if  len(ContentInverseTable.objects.filter(word=token))==1:
                    record = ContentInverseTable.objects.get(word=token)
                    idf = np.log(length/(1+record.frequency))
                    location=eval(record.location)
                    for x in location:
                        globa =x[0]
                        local = x[1]
                        if globa not in score.keys():
                            globa_list.append(globa)
                            score[globa]=(1+np.log(1+local))*idf
                        else:
                            score[globa]+=(1+np.log(1+local))*idf 
        if category=='all':
            cc=0
            article_list = []
            print(1333)
            for g in globa_list:
                article = Article.objects.get(id = g+1)
                date = article.date
                s_date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
                s_date = (today-s_date_).days
                if s_date==0:
                    date_ = 날짜기준[0]
                elif s_date==1:
                    date_=날짜기준[1]
                else:
                    w_d = (today-datetime.timedelta(today.weekday())-s_date_).days
                    if w_d<=0:
                        date_=날짜기준[2]
                    elif 0<w_d<8:
                        date_ = 날짜기준[3]
                    else:
                        if (today-datetime.timedelta(today.day-1)-s_date_).days<=0:
                            date_ = 날짜기준[4]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 1):
                            date_=날짜기준[5]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 2):
                            date_=날짜기준[6]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 3):
                            date_=날짜기준[7]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 4):
                            date_=날짜기준[8]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 5):
                            date_=날짜기준[9]
                        elif (today.year, today.month)==ch_calender(s_date_,mode='range',range_=[6,12]):
                            date_=날짜기준[10]
                        else:
                            date_=날짜기준[-1]
                title = article.title
                # for windows in key_by_window:
                #     for window in windows:
                #         if window in title:
                #             score[g]+=1
                writer = article.writer
                href = article.href
                scores = score[g]
                article_dic={'article_num':cc+1,'title':title, 'writer':writer, 'href':href, 'updated':date_,'score':scores}
                article_list.append(article_dic)
                cc+=1
            print(time.time()-time_)
            # print(score)
            xxxx= sorted(article_list,key=lambda x:-x['score'])
            print(xxxx)
            return JsonResponse(xxxx, safe=False)
        elif category !='all':
            # for g in globa_list:
                # for windows in key_by_window:
                #     for window in windows:
                #         if window in Article.objects.get(id=int(g)).title:
                #             score[globa]+=1
            score_sorted = [(x,y) for x,y in sorted(score.items(), key = lambda x:-x[1])]
            article_list = []
            cc=0
            cc=0
            article_list = []
            for inde, sc in score_sorted:
                if article.채용 ==1:
                    article = Article.objects.get(id=inde)
                    date = Article.objects.get(id = inde).date
                    s_date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
                    s_date = (today-s_date_).days
                if s_date==0:
                    date_ = 날짜기준[0]
                elif s_date==1:
                    date_=날짜기준[1]
                else:
                    w_d = (today-datetime.timedelta(today.weekday())-s_date_).days
                    if w_d<=0:
                        date_=날짜기준[2]
                    elif 0<w_d<8:
                        date_ = 날짜기준[3]
                    else:
                        if (today-datetime.timedelta(today.day-1)-s_date_).days<=0:
                            date_ = 날짜기준[4]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 1):
                            date_=날짜기준[5]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 2):
                            date_=날짜기준[6]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 3):
                            date_=날짜기준[7]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 4):
                            date_=날짜기준[8]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 5):
                            date_=날짜기준[9]
                        elif (today.year, today.month)==ch_calender(s_date_,mode='range',range_=[6,12]):
                            date_=날짜기준[10]
                        else:
                            date_=날짜기준[-1]
                    title = Article.objects.get(id = inde).title
                    writer = Article.objects.get(id = inde).writer
                    href = Article.objects.get(id = inde).href
                    article_dic={'article_num':cc+1,'title':title, 'writer':writer, 'href':href, 'updated':date_}
                    article_list.append(article_dic)
                    cc+=1
            print('1')
            print(time.time()-time_)
            return JsonResponse(article_list, safe=False)


def upload_inverse(request):
    # vocab_title_table = pd.read_excel('형태소분석기_앙상블/02역색인테이블만들기/vocab_title_table.xlsx').iloc[:,1:]
    # vocab_content_table = pd.read_excel('형태소분석기_앙상블/02역색인테이블만들기/vocab_content_table.xlsx').iloc[:,1:]
    with open('형태소분석기_앙상블/02역색인테이블만들기/vocab_title_table','rb') as f:
        vocab_title_table = pickle.load(f)
    with open('형태소분석기_앙상블/02역색인테이블만들기/vocab_con_table','rb') as f:
        vocab_content_table = pickle.load(f)
    for i in range(len(vocab_title_table)):
        print(i/len(vocab_title_table))
        InverseTable(word=vocab_title_table['vocab'].iloc[i],frequency=vocab_title_table['idf'].iloc[i],location=vocab_title_table['location'].iloc[i]).save()
    for i in range(len(vocab_content_table)):
        print(i/len(vocab_content_table))
        ContentInverseTable(word=vocab_content_table['vocab'].iloc[i],frequency=vocab_content_table['idf'].iloc[i],location=vocab_content_table['location'].iloc[i]).save()
    return HttpResponse(1)
def a(record,vocab, vocab_length=500, tf_log = 10):
    ze = np.zeros((vocab_length,))
    record=re.sub('[^ㄱ-힣]', ' ',record).split()
    for key, value in Counter(record).items():
        if key in vocab:
            ind = vocab.index(key)
            if tf_log == 'e':
                ze[ind]=1+np.log(value)
            elif tf_log=='10':
                ze[ind]=1+np.log10(value)
            else:
                ze[ind]=1+np.log2(value)
    return ze
def upload(request):
    print(os.getcwd())
    dir_list = '관람 대회 업체 의견수렴 의회 채용 합격자 행사 전체교육 전문교육 청소년 주민자치'.split()
    data =data14000_train['nouns']
    for c,dir_ in enumerate(dir_list):
        모델 = keras.models.load_model('files/%s라벨링_꼬꼬마.h5'%dir_,compile = False)
        with open('files/new_labelling_file_%s라벨링_꼬꼬마_vocab'%dir_,'rb') as f:
            vocab = pickle.load(f)
        with open('files/new_labelling_file_%s라벨링_꼬꼬마_idf'%dir_,'rb') as f:
            idf = pickle.load(f)
        tf = data.apply(lambda x:a(str(x),vocab = vocab))
        tf_idf = tf.apply(lambda x:x*idf )
        tf_idf = pd.DataFrame(dict(tf_idf).values())
        pre_list = []
        for i in 모델.predict(tf_idf):
            if i>0.5:
                pre_list.append(1)
            else:
                pre_list.append(0)
        if c == 0:
            데이타 = pd.concat([data14000, pd.DataFrame({'%s'%dir_:pre_list})],axis = 1)
        else:
            데이타 = pd.concat([데이타, pd.DataFrame({'%s'%dir_:pre_list})],axis = 1)
    for record_num in range(len(데이타)):
        title = 데이타.iloc[record_num,:]['title']
        content = 데이타.iloc[record_num,:]['content']
        date = 데이타.iloc[record_num,:]['date']
        href = 데이타.iloc[record_num,:]['href']
        writer = 데이타.iloc[record_num,:]['writer']
        nouns = [x for x in 데이타.iloc[record_num,:]['title_nouns'] if len(x)>1]
        # content_nouns = [x for x in 데이타.iloc[record_num,:]['content_nouns'] if len(x)>1]
        관람 = 데이타.iloc[record_num,:]['관람']
        대회 = 데이타.iloc[record_num,:]['대회']
        업체 = 데이타.iloc[record_num,:]['업체']
        의견수렴 = 데이타.iloc[record_num,:]['의견수렴']
        의회 = 데이타.iloc[record_num,:]['의회']
        채용 = 데이타.iloc[record_num,:]['채용']
        합격자 = 데이타.iloc[record_num,:]['합격자']
        행사 = 데이타.iloc[record_num,:]['행사']
        전체교육 =데이타.iloc[record_num,:]['전체교육']
        전문교육 = 데이타.iloc[record_num,:]['전문교육']
        청소년 = 데이타.iloc[record_num,:]['청소년']
        주민자치 = 데이타.iloc[record_num,:]['주민자치']
        Article(title=title,content=content,date =date,writer=writer, href=href,title_noun = nouns, 채용=채용,합격자=합격자,의회=의회, 행사=행사,관람=관람, 대회=대회, 의견수렴=의견수렴, 업체=업체, 전체교육=전체교육, 전문교육=전문교육,청소년=청소년,주민자치=주민자치).save()
        print(record_num/len(데이타))
    return HttpResponse(1)
def change_key(sentence):
    t= time.time()
    sentence=re.sub('[^ㄱ-힣 ]',' ',str(sentence))

    sentence_okt = [x for x in okt.nouns(sentence) if len(x)>1]
    sentence_komoran = [x for x in komoran.nouns(sentence) if len(x)>1]
    sentence_han = [x for x in hannanum.nouns(sentence) if len(x)>1]

    sentence_okt_gt4 = [x for x in sentence_okt if len(x)>3]
    sentence_komoran_gt4 = [x for x in sentence_komoran if len(x)>3]
    sentence_han_gt4 = [x for x in sentence_han if len(x)>3]

    sentence_okt_gt4_scattered_by_hannanum = []
    sentence_okt_gt4_scattered_by_komoran = []
    for token in  sentence_okt_gt4:
        a=  komoran.nouns(token)
        b=  hannanum.nouns(token)
        if len(a)!=1:
            sentence_okt_gt4_scattered_by_komoran+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_okt_gt4_scattered_by_hannanum+=[x for x in b if len(x)>1]
    sentence_komoran_gt4_scattered_by_hannanum = []
    sentence_komoran_gt4_scattered_by_okt = []
    for token in  sentence_komoran_gt4:
        a=  okt.nouns(token)
        b=  hannanum.nouns(token)
        if len(a)!=1:
            sentence_komoran_gt4_scattered_by_okt+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_komoran_gt4_scattered_by_hannanum+=[x for x in b if len(x)>1]
    sentence_hannanum_gt4_scattered_by_okt = []
    sentence_hannanum_gt4_scattered_by_komoran = []
    for token in  sentence_han_gt4:
        a=  komoran.nouns(token)
        b=  okt.nouns(token)
        if len(a)!=1:
            sentence_hannanum_gt4_scattered_by_komoran+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_hannanum_gt4_scattered_by_okt+=[x for x in b         if len(x)>1]

    sentence_okt_gt4_scattered_by_hannanum_set = set(Counter(sentence_okt_gt4_scattered_by_hannanum).keys()) 
    sentence_okt_gt4_scattered_by_komoran_set = set(Counter(sentence_okt_gt4_scattered_by_komoran).keys())
    hannanum_차집합 = list(sentence_okt_gt4_scattered_by_hannanum_set-sentence_okt_gt4_scattered_by_komoran_set)
    komoran_차집합 = list(sentence_okt_gt4_scattered_by_komoran_set-sentence_okt_gt4_scattered_by_hannanum_set)
    교집합 = list(sentence_okt_gt4_scattered_by_komoran_set&sentence_okt_gt4_scattered_by_hannanum_set)
    okt_dic = {}
    for i in 교집합:
        if Counter(sentence_okt_gt4_scattered_by_hannanum)[i]>Counter(sentence_okt_gt4_scattered_by_komoran)[i]:
            okt_dic[i]=Counter(sentence_okt_gt4_scattered_by_hannanum)[i]
        else:
            okt_dic[i]=Counter(sentence_okt_gt4_scattered_by_komoran)[i]
    for i in hannanum_차집합:
        okt_dic[i] = Counter(sentence_okt_gt4_scattered_by_hannanum)[i]
    for i in komoran_차집합:
        okt_dic[i] = Counter(sentence_okt_gt4_scattered_by_komoran)[i]
        
    sentence_komoran_gt4_scattered_by_okt_set = set(Counter(sentence_komoran_gt4_scattered_by_okt).keys()) 
    sentence_komoran_gt4_scattered_by_hannanum_set = set(Counter(sentence_komoran_gt4_scattered_by_hannanum).keys())
    okt_차집합 = list(sentence_komoran_gt4_scattered_by_okt_set-sentence_komoran_gt4_scattered_by_hannanum_set)
    hannanum_차집합 = list(sentence_komoran_gt4_scattered_by_hannanum_set-sentence_komoran_gt4_scattered_by_okt_set)
    교집합 = list(sentence_komoran_gt4_scattered_by_hannanum_set&sentence_komoran_gt4_scattered_by_okt_set)
    komoran_dic = {}
    for i in 교집합:
        if Counter(sentence_komoran_gt4_scattered_by_okt)[i]>Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]:
            komoran_dic[i]=Counter(sentence_komoran_gt4_scattered_by_okt)[i]
        else:
            komoran_dic[i]=Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]
    for i in okt_차집합:
        komoran_dic[i] = Counter(sentence_komoran_gt4_scattered_by_okt)[i]
    for i in hannanum_차집합:
        komoran_dic[i] = Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]

    sentence_hannanum_gt4_scattered_by_okt_set = set(Counter(sentence_hannanum_gt4_scattered_by_okt).keys()) 
    sentence_hannanum_gt4_scattered_by_komoran_set = set(Counter(sentence_hannanum_gt4_scattered_by_komoran).keys())
    okt_차집합 = list(sentence_hannanum_gt4_scattered_by_okt_set-sentence_hannanum_gt4_scattered_by_komoran_set)
    komoran_차집합 = list(sentence_hannanum_gt4_scattered_by_komoran_set-sentence_hannanum_gt4_scattered_by_okt_set)
    교집합 = list(sentence_hannanum_gt4_scattered_by_komoran_set&sentence_hannanum_gt4_scattered_by_okt_set)
    han_dic = {}
    for i in 교집합:
        if Counter(sentence_hannanum_gt4_scattered_by_okt)[i]>Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]:
            han_dic[i]=Counter(sentence_hannanum_gt4_scattered_by_okt)[i]
        else:
            han_dic[i]=Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]
    for i in okt_차집합:
        han_dic[i] = Counter(sentence_hannanum_gt4_scattered_by_okt)[i]
    for i in komoran_차집합:
        han_dic[i] = Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]

    for x,y in list(Counter(sentence_okt).items()):
        if len(x)<7:
            if x in okt_dic.keys():
                okt_dic[x]+=y
            else:
                okt_dic[x]=y
    for x,y in list(Counter(sentence_komoran).items()):
        if len(x)<7:
            if x in komoran_dic.keys():
                komoran_dic[x]+=y
            else:
                komoran_dic[x]=y
    for x,y in list(Counter(sentence_han).items()):
        if len(x)<7:
            if x in han_dic.keys():
                han_dic[x]+=y
            else:
                han_dic[x]=y

    final_dic = {}
    for i in list(Counter(list(han_dic.keys()) + list(komoran_dic.keys()) + list(okt_dic.keys())).keys()):
        a=0
        b=0
        c=0
        if i in han_dic.keys():
            a = han_dic[i]
        if i in komoran_dic.keys():
            b = komoran_dic[i]
        if i in okt_dic.keys():
            c = okt_dic[i]
        final_dic[i]=max([a,b,c])
    print(final_dic, sentence,sep='\n\n\n')
    print(time.time()-t)
    return final_dic
def ch_calender(date, differ='', mode='none',range_=[6,12]):
    if mode == 'none':
        year = date.year
        month = date.month+differ 
        if 24>=month >12:
            month -=12
            year +=1
        if month >24:
            month -=24
            year +=2
        return (year, month)
    else:
        l = []
        st = range_[0]
        fi = range_[1]
        for i in range(st,fi):
            year = date.year
            month = date.month+i
            if 24>=month >12:
                month -=12
                year +=1
            if month >24:
                month -=24
                year +=2
            l.append((year,month))
        return l 
