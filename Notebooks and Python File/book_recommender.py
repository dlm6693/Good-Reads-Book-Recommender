import pandas as pd
import numpy as np
from surprise import SVD
from surprise import dump
from surprise import Reader, Dataset
from surprise.model_selection import cross_validate, train_test_split
import os

def create_user(df):
    user_name = input('Please enter your name: ')
    print("\n Welcome {}! I'm going to recommend some books just for you.\n".format(user_name))
    user_id = max(df.user_id) + 1
    return user_name, user_id

def valid_entries(user_entry, valid_entries):
    if user_entry not in valid_entries:
        return False
    else:
        return True

def check_favorite_authors(df):
    valid_yes_no = ['Y', 'N', 'YES', 'NO']
    is_valid = False
    while is_valid == False:
        favorite_author_ask = (input("Do you have any favorite authors who may have recently written books? (Yes/No) ")).upper()
        if valid_entries(favorite_author_ask, valid_yes_no) == False:
            print("Sorry, that isn't a valid entry, please try again. \n")
        else:
            is_valid = True
            if favorite_author_ask in ['Y', 'YES']:
                favorite_author_ask = True
            else:
                favorite_author_ask = False
    if favorite_author_ask == True:
        keep_checking = True
        while keep_checking == True:
            favorite_author = (input("Name an author, I will check to see if they wrote anything on the top list."))
            if favorite_author.title() in df.author.unique():
                print("{} has written the following books: \n".format(favorite_author))
                for i in list(df.title.loc[df.author == favorite_author].unique()):
                    print(i + "\n")
            else:
                print("Sorry, {} has not written any books that were recently trending on our lists.".format(favorite_author))
            is_valid = False
            while is_valid == False:
                check_again = input("Would you like to check another author? (Yes/No)").upper()
                if valid_entries(check_again, valid_yes_no) == False:
                    print("Sorry, that isn't a valid entry, please try again. \n")
                else:
                    is_valid = True
            if check_again in ['Y', 'YES']:
                keep_checking = True
            else:
                keep_checking = False

def num_reviews():
    x = False
    while x == False:
        num_reviews = input('How many books would you like to review? \n')
        try:
            if 0< int(num_reviews) <=10:
                x = True
                return int(num_reviews)
                break
        except:
            print('Invalid entry. Please try again.')

def new_user_ratings(df, num_reviews, user_name, user_id):
    ratings_list = []
    df_reduced = df[['title', 'author', 'isbn']].drop_duplicates()
    while num_reviews >0:
        book = df_reduced.sample(1)
        print('------------------------')
        print(book.title.item() + ' by ' + book.author.item() + '\n')
        rating = input('How do you rate this book on a scale of 1 to 5? If you are unfamiliar with this title press n. \n')
        if rating == 'n':
            continue
        else:
            rating_dict = {'user_id':user_id, 'isbn':book.isbn.item(), 'rating':rating}
            ratings_list.append(rating_dict)
            num_reviews -= 1
    return ratings_list

def new_recommendations(df, new_ratings):
    df = df[['user_id', 'isbn', 'rating']]
    new_ratings = pd.DataFrame(new_ratings)[['user_id', 'isbn', 'rating']]
    new_df = pd.concat([df, new_ratings]).reset_index(drop=True)
    reader = Reader(rating_scale=(1,5))
    data = Dataset.load_from_df(new_df,reader)
    train, test = train_test_split(data, test_size=.2)
    model = SVD(n_epochs=17, lr_all=.015, reg_all=.125, n_factors=17)
    model.fit(train)
    preds = model.test(test)
    user_id = new_ratings.user_id[0]
    book_list = []
    for x in new_df.isbn.unique():
        book_list.append((x, model.predict(user_id,x)[3]))
    ranked_books = sorted(book_list, key=lambda x: x[1], reverse=True)
    return ranked_books

def num_recs():
    x = False
    while x == False:
        num_recs = input('How many books would you like to be recommended? \n')
        try:
            if 0< int(num_recs) <=10:
                x = True
                return int(num_recs)
                break
        except:
            print('Invalid entry. Please try again.')
    return num_recs

def recs_to_return(recs, df, num_recs):
    df_reduced = df[['title', 'author', 'isbn']].drop_duplicates()
    for i, v in enumerate(recs):
        book = df_reduced.loc[df_reduced.isbn == v[0]]
        print('Recommendation # ' + str(i+1) + ': ' + book.title.item() + ' by ' + book.author.item() +
              ' \n https://isbnsearch.org/isbn/{}'.format(book.isbn.item()))
        print('\n ------------------------')
        num_recs-=1
        if num_recs == 0:
            break
def book_recommender_function(df):
    again = True
    while again == True:
        user_name, user_id = create_user(df)
        check_favorite_authors(df)
        num = num_reviews()
        ratings_list = new_user_ratings(df, num, user_name, user_id)
        ranked_books = new_recommendations(df, ratings_list)
        num_recommendations = num_recs()
        recs_to_return(ranked_books, df, num_recommendations)

        ask = input("Would you like to go again? (Yes/No)").upper()
        if ask in ['Y', 'YES']:
            again = True
            os.system('clear')
        else:
            again = False
            os.system('clear')
            break
