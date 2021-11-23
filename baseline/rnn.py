"""GRU
"""
import pickle
import os
import numpy as np
from sklearn import metrics
from imblearn.over_sampling import RandomOverSampler

import torch

import utils


def build_model(params):
    print('Loading Data...')
    data = utils.data_loader(dpath=params['dpath'], lang=params['lang'])
    train_indices, val_indices, test_indices = utils.data_split(data)

    # load train
    input_data = {
        'docs': [data['docs'][item] for item in train_indices],
        'labels': [data['labels'][item] for item in train_indices],
    }
    if params['over_sample']:
        ros = RandomOverSampler(random_state=33)
        sample_indices = list(range(len(input_data['docs'])))
        sample_indices, _ = ros.fit_resample(sample_indices, input_data['labels'])
        input_data = {
            'docs': [input_data['docs'][item] for item in sample_indices],
            'labels': [input_data['labels'][item] for item in sample_indices],
        }

    # too large data to fit memory, remove some
    # training data size: 200000
    if len(input_data['docs']) > 200000:
        np.random.seed(33)
        indices = list(range(len(input_data['docs'])))
        np.random.shuffle(indices)
        indices = indices[:200000]
        input_data = {
            'docs': [input_data['docs'][item] for item in indices],
            'labels': [input_data['labels'][item] for item in indices],
        }

    # load valid

    # load test
    print('Loading Test data')
    test_data = {
        'docs': [data['docs'][item] for item in test_indices],
        'labels': [data['labels'][item] for item in test_indices],
        params['domain_name']: [input_data[params['domain_name']][item] for item in test_indices],
    }

    print('Testing.............................')
    input_feats = lr_vect.transform_test(input_data['docs'])
    pred_label = clf.predict(input_feats)
    fpr, tpr, _ = metrics.roc_curve(
        y_true=input_data['labels'], y_score=clf.predict_proba(input_feats)[:, 1],
    )

    with open(params['result_path'], 'a') as wfile:
        wfile.write('{}...............................\n'.format(datetime.datetime.now()))
        wfile.write('Performance Evaluation for the task: {}\n'.format(params['dname']))
        wfile.write('F1-weighted score: {}\n'.format(
            metrics.f1_score(y_true=input_data['labels'], y_pred=pred_label, average='weighted')
        ))
        wfile.write('AUC score: {}\n'.format(
            metrics.auc(fpr, tpr)
        ))
        wfile.write(metrics.classification_report(
            y_true=input_data['labels'], y_pred=pred_label, digits=3) + '\n')
        wfile.write('\n')

        wfile.write('Fairness Evaluation\n')
        wfile.write(
            utils.fair_eval(
                true_labels=input_data['labels'],
                pred_labels=pred_label,
                domain_labels=input_data[params['domain_name']]
            ) + '\n'
        )

        wfile.write('...............................\n\n')
        wfile.flush()


if __name__ == '__main__':
    review_dir = '../data/review/'
    hate_speech_dir = '../data/hatespeech/'
    model_dir = '../resources/model/'
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    model_dir = model_dir + os.path.basename(__file__) + '/'
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    result_dir = '../resources/results/'
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    data_list = [
        # ['review_amazon_english', review_dir + 'amazon/amazon.tsv', 'english'],
        # ['review_yelp-hotel_english', review_dir + 'yelp_hotel/yelp_hotel.tsv', 'english'],
        # ['review_yelp-rest_english', review_dir + 'yelp_rest/yelp_rest.tsv', 'english'],
        # ['review_twitter_english', review_dir + 'twitter/twitter.tsv', 'english'],
        ['review_trustpilot_english', review_dir + 'trustpilot/united_states.tsv', 'english'],
        ['review_trustpilot_french', review_dir + 'trustpilot/france.tsv', 'french'],
        ['review_trustpilot_german', review_dir + 'trustpilot/german.tsv', 'german'],
        ['review_trustpilot_danish', review_dir + 'trustpilot/denmark.tsv', 'danish'],
        ['hatespeech_twitter_english', hate_speech_dir + 'English/corpus.tsv', 'english'],
        ['hatespeech_twitter_spanish', hate_speech_dir + 'Spanish/corpus.tsv', 'spanish'],
        ['hatespeech_twitter_italian', hate_speech_dir + 'Italian/corpus.tsv', 'italian'],
        ['hatespeech_twitter_portuguese', hate_speech_dir + 'Portuguese/corpus.tsv', 'portuguese'],
        ['hatespeech_twitter_polish', hate_speech_dir + 'Polish/corpus.tsv', 'polish'],
    ]

    for data_entry in tqdm(data_list):
        print('Working on: ', data_entry)

        parameters = {
            'result_path': os.path.join(result_dir, os.path.basename(__file__) + '.txt'),
            'model_dir': model_dir,
            'dname': data_entry[0],
            'dpath': data_entry[1],
            'lang': data_entry[2],
            'max_feature': 10000,
            'over_sample': False,
        }

        build_model(parameters)
