import math

import pandas
from hazm import *
import codecs
import csv
import json
import random
from decimal import *

def make_parametr(address, is_pandas=False, filename="clean_data.csv", is_test=False):
    if not is_pandas:
        csvFile = pandas.read_csv(address)
    else:
        csvFile = address

    normalizer = Normalizer()
    tokenizer = WordTokenizer(replace_emails=True, replace_ids=True, replace_links=True,
                              replace_numbers=True, replace_hashtags=True)
    stemmer = Stemmer()
    stopwords = codecs.open('persian', encoding='utf-8').read().split('\n')
    fields = ['Text']
    if not is_test:
        fields.append('TAG')

    with open(filename, 'w') as csvfile2:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile2)
        # writing the fields
        csvwriter.writerow(fields)
    if not is_pandas:
        text = csvFile["Text"]
    else:
        text = csvFile

    n = len(text)
    for i in range(n):
        text_news = normalizer.normalize(text[i])
        text_news = tokenizer.tokenize(text_news)
        m = len(text_news)
        for j in range(m - 1, -1, -1):
            text_news[j] = stemmer.stem(text_news[j])
            if text_news[j] in stopwords:
                text_news.pop(j)

        set_word = set()
        word_count = {}
        for word in text_news:
            word = "a" + word + "a"
            if word in set_word:
                count = word_count[word]
                count = count + 1
                word_count[word] = count
            else:
                set_word.add(word)
                word_count[word] = 1

        json_string = json.dumps(word_count)
        row = [json_string]
        if not is_test:
            tag = csvFile["Category"][i]
            row.append(tag)

        with open(filename, 'a', encoding="utf-8") as csvfile2:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile2)

            csvwriter.writerow(row)


def make_final(address):
    csvFile = pandas.read_csv(address)
    fields = ['Text', 'TAG']
    filename = "test_data.csv"
    with open(filename, 'w') as csvfile2:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile2)
        # writing the fields
        csvwriter.writerow(fields)
    n = len(csvFile)
    sport = {}
    politics = {}
    all_news = {}
    set_sport = set()
    set_politics = set()
    set_all_news = set()
    count_s = 0 ####################
    count_p = 0 ###################
    for i in range(n):
        p = random.uniform(0, 1)
        if p < 0.2:
            filename = "test_data.csv"
            tag = csvFile["TAG"][i]
            row = [csvFile["Text"][i], tag]
            with open(filename, 'a', encoding="utf-8") as csvfile2:
                # creating a csv writer object
                csvwriter = csv.writer(csvfile2)

                csvwriter.writerow(row)

        else:
            tag = csvFile["TAG"][i]
            news = json.loads(csvFile["Text"][i])
            keys = list(news.keys())
            if tag == "Politics":
                count_p = count_p + 1 #######################
                for key in keys:
                    count = news[key]
                    if key in set_all_news:
                        all_count = all_news[key]
                        all_news[key] = all_count + count
                    else:
                        all_news[key] = count
                        set_all_news.add(key)

                    if key in set_politics:
                        count = count + politics[key]
                        politics[key] = count
                    else:
                        set_politics.add(key)
                        politics[key] = count

            elif tag == "Sport":
                count_s = count_s + 1 #####################
                for key in keys:
                    count = news[key]
                    if key in set_all_news:
                        all_count = all_news[key]
                        all_news[key] = all_count + count
                    else:
                        all_news[key] = count
                        set_all_news.add(key)

                    if key in set_sport:
                        count = count + sport[key]
                        sport[key] = count
                    else:
                        set_sport.add(key)
                        sport[key] = count

    fields = ['Text', 'TAG']
    filename = "final_data.csv"
    with open(filename, 'w') as csvfile2:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile2)
        # writing the fields
        csvwriter.writerow(fields)

        json_string = json.dumps(all_news)
        row = [json_string, "All"]
        csvwriter.writerow(row)

        json_string = json.dumps(sport)
        row = [json_string, "Sport"]
        csvwriter.writerow(row)

        json_string = json.dumps(politics)
        row = [json_string, "Politics"]
        csvwriter.writerow(row)

    getcontext().prec = 100
    alpha = Decimal(count_p) / Decimal(count_p + count_s)  ####################
    print(alpha)
    file_name = "alpha.txt"
    with open(file_name, 'w') as text_file:
        text_file.write(str(alpha))

def predict(pandas_df, clean=False):
    if not clean:
        filename = "clean_test_data.csv"
        make_parametr(pandas_df, is_pandas=True, filename=filename, is_test=True)
        pandas_df = pandas.read_csv(filename)
        pandas_df = pandas_df["Text"]

    with open("alpha.txt", "r") as file1:
        alpha = float(file1.readline())

    predicted_labels = []
    sport = {}
    politics = {}
    all_news = {}
    address = "final_data.csv"
    csvFile = pandas.read_csv(address)
    n = len(csvFile)
    for i in range(n):
        tag = csvFile["TAG"][i]
        if tag == "Sport":
            sport = json.loads(csvFile["Text"][i])
        elif tag == "Politics":
            politics = json.loads(csvFile["Text"][i])
        elif tag == "All":
            all_news = json.loads(csvFile["Text"][i])

    sport_key = list(sport.keys())
    # print(len(sport_key))
    politics_key = list(politics.keys())
    # print(len(politics_key))
    all_key = list(all_news.keys())
    # print(len(all_key))
    n = len(pandas_df)
    # ************************************
    total = len(all_key)
    sport_number_word = 0
    politics_number_word = 0
    for key in sport_key:
        sport_number_word = sport_number_word + sport[key]

    for key in politics_key:
        politics_number_word = politics_number_word + politics[key]
    #*****************************************

    for i in range(n):
        p_sport = math.log(1-alpha)
        p_politics = math.log(alpha)


        news = json.loads(pandas_df[i])
        keys = list(news.keys())
        #***************************************
        for key in keys:
            if key in all_key:
                if key in sport_key:
                    sport_count = sport[key] + 1
                else:
                    sport_count = 1

                if key in politics_key:
                    politics_count = politics[key] + 1
                else:
                    politics_count = 1
            else:
                continue

            p_politics = p_politics + (math.log((politics_count / (politics_number_word + total)))) * news[key]
            p_sport = p_sport + (math.log((sport_count / (sport_number_word + total)))) * news[key]

        if p_politics > p_sport:
            tag = "Politics"
        else:
            tag = "Sport"
        #***********************************************

        predicted_labels.append(tag)

    print(alpha)
    # print(Decimal(1-alpha))
    return predicted_labels


def f1(predicted_labels, pandas_df):
    n = len(predicted_labels)
    m = len(pandas_df)
    if m != n:
        print("Lack of information sync")
        return "Lack of information sync"

    sport_tp = 0
    sport_tn = 0
    sport_fp = 0
    sport_fn = 0
    politics_tp = 0
    politics_tn = 0
    politics_fp = 0
    politics_fn = 0

    for i in range(n):
        predicted_label = predicted_labels[i]
        expeted_label = pandas_df[i]
        if predicted_label == "Sport":
            if expeted_label == "Sport":
                sport_tp = sport_tp + 1
                politics_tn = politics_tn + 1
            else:
                sport_fp = sport_fp + 1
                politics_fn = politics_fn + 1

        elif predicted_label == "Politics":
            if expeted_label == "Politics":
                sport_tn = sport_tn + 1
                politics_tp = politics_tp + 1
            else:
                sport_fn = sport_fn + 1
                politics_fp = politics_fp + 1

        else:
            print("unknown tag")
            return "unknown tag"

    sport_f1 = (2 * sport_tp) / ((2 * sport_tp) + sport_fp + sport_fn)
    politics_f1 = (2 * politics_tp) / ((2 * politics_tp) + politics_fp + politics_fn)
    # accuracy = (sport_tn + sport_tp) / (sport_fp + sport_fn + sport_tn + sport_tp)
    # print(sport_tp)
    # print(sport_tn)
    # print(sport_fp)
    # print(sport_fn)
    # print("###############################")
    # print(politics_tp)
    # print(politics_tn)
    # print(politics_fp)
    # print(politics_fn)
    # print("###############################")
    # print(accuracy)
    return sport_f1, politics_f1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # ///// The first phase of training data processing
    # make_parametr("nlp_train.csv")

    # //// Creating the final file to use the predict function and creating a test file
    # address = "clean_data.csv"
    # make_final(address)
    # /////////////////////////////////////// test
    # address = "test_data.csv"
    # csvFile = pandas.read_csv(address)
    # p = predict(csvFile["Text"], True)
    # sport, politics = f1(p, csvFile["TAG"])
    # print(sport)
    # print(politics)
    # /////////////////////////////////////// varzesh3
    # address = "varzesh3.csv"
    # csvFile = pandas.read_csv(address)
    # p = predict(csvFile["Text"])
    # sport, politics = f1(p, csvFile["Category"])
    # print(sport)
    # print(politics)
    # /////////////////////////////////////// tabnak
    # address = "tabnak.csv"
    # csvFile = pandas.read_csv(address)
    # p = predict(csvFile["Text"])
    # sport, politics = f1(p, csvFile["Category"])
    # print(sport)
    # print(politics)
    # //////////////////////////////////// delete empty entekhab
    # address = "entekhab.csv"
    # df = pandas.read_csv(address)
    # list_empty = []
    # n = len(df["Text"])
    # for i in range(n):
    #     x = df["Text"][i]
    #     if type(x) == float:
    #         list_empty.append(i)
    #
    # filename = "entekhab2.csv"
    # with open(filename, 'w', encoding="utf-8") as csvfile2:
    #     # creating a csv writer object
    #     csvwriter = csv.writer(csvfile2)
    #     row = ["Text", "Category"]
    #     csvwriter.writerow(row)
    #     for i in range(n):
    #         if i in list_empty:
    #             continue
    #
    #         row = [df["Text"][i], df["Category"][i]]
    #         csvwriter.writerow(row)
    #///////////////////////////////////////////////////
    # address = "entekhab2.csv"
    # df = pandas.read_csv(address)
    # count = 0
    # print(type(df["Text"][0]))
    # print(len(df["Text"]))
    #//////////////////////////////////////////////////
    # address = "entekhab2.csv"
    # csvFile = pandas.read_csv(address)
    # p = predict(csvFile["Text"])
    # sport, politics = f1(p, csvFile["Category"])
    # print(sport)
    # print(politics)




