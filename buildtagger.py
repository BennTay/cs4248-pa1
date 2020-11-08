# python3.5 buildtagger.py <train_file_absolute_path> <model_file_absolute_path>
# python buildtagger.py sents.train model-file
# Author: Benn Tay Guobin (A0167647N)
import os
import math
import sys
import datetime
import json

TAG_COUNTS = 'tag_counts'
WORD_COUNTS = 'word_counts'
WORD_TAG_COUNTS = 'word_tag_count'
TAG_TAG_COUNTS = 'tag_tag_count'
WORD_TAG_PROBS = 'word_tag_probs'
TAG_TAG_PROBS = 'tag_tag_probs'
UNK = 'unknown_word'

def train_model(train_file_name, model_file_name):
    # write your code here. You can add functions as well.
    print('Training file: ', train_file_name)
    print('Model file: ', model_file_name)

    p_dict = {}
    p_dict[TAG_COUNTS] = {}
    p_dict[WORD_COUNTS] = {}
    p_dict[WORD_TAG_COUNTS] = {}
    p_dict[TAG_TAG_COUNTS] = {}
    p_dict[WORD_TAG_PROBS] = {}
    p_dict[TAG_TAG_PROBS] = {}

    with open(train_file_name, 'r') as train_file:
        for sentence in train_file:
            sentence_tokens = sentence.split()
            sentence_tokens.insert(0, '<s>/<s>')
            sentence_tokens.append('<e>/<e>')
            
            for i in range(len(sentence_tokens) - 1):

                token1 = sentence_tokens[i][::-1].split('/', maxsplit=1)
                word1 = token1[1][::-1]
                tag1 = token1[0][::-1]

                token2 = sentence_tokens[i+1][::-1].split('/', maxsplit=1)
                tag2 = token2[0][::-1]

                # Count the number of times a word occurs
                if word1 in p_dict[WORD_COUNTS]:
                    p_dict[WORD_COUNTS][word1] += 1
                else:
                    p_dict[WORD_COUNTS][word1] = 1

                # Count the number of times a word with the given tag appears
                if word1 in p_dict[WORD_TAG_COUNTS]:
                    if tag1 in p_dict[WORD_TAG_COUNTS][word1]:
                        p_dict[WORD_TAG_COUNTS][word1][tag1] += 1
                    else:
                        p_dict[WORD_TAG_COUNTS][word1][tag1] = 1
                else:
                    p_dict[WORD_TAG_COUNTS][word1] = {}
                    p_dict[WORD_TAG_COUNTS][word1][tag1] = 1

                # Count the number of times a tag appears
                if tag1 in p_dict[TAG_COUNTS]:
                    p_dict[TAG_COUNTS][tag1] += 1
                else:
                    p_dict[TAG_COUNTS][tag1] = 1

                # Count the number of times a tag appears after a given tag
                if tag1 in p_dict[TAG_TAG_COUNTS]:
                    if tag2 in p_dict[TAG_TAG_COUNTS][tag1]:
                        p_dict[TAG_TAG_COUNTS][tag1][tag2] += 1
                    else:
                        p_dict[TAG_TAG_COUNTS][tag1][tag2] = 1
                else:
                    p_dict[TAG_TAG_COUNTS][tag1] = {}
                    p_dict[TAG_TAG_COUNTS][tag1][tag2] = 1

            if '<e>' in p_dict[TAG_COUNTS]:
                p_dict[TAG_COUNTS]['<e>'] += 1
            else:
                p_dict[TAG_COUNTS]['<e>'] = 1
    
    # Laplace smoothing
    num_w = len(p_dict[WORD_COUNTS])
    num_t = len(p_dict[TAG_COUNTS])

    for word in p_dict[WORD_TAG_COUNTS]:
        p_dict[WORD_TAG_PROBS][word] = {}
        for tag in p_dict[TAG_COUNTS]:
            if tag in p_dict[WORD_TAG_COUNTS][word]:
                p_dict[WORD_TAG_PROBS][word][tag] = math.log(((p_dict[WORD_TAG_COUNTS][word][tag] + 1) / (p_dict[TAG_COUNTS][tag] + num_t)), 10)
            else:
                p_dict[WORD_TAG_PROBS][word][tag] = -sys.maxsize
        
    p_dict[WORD_TAG_PROBS][UNK] = {}
    for tag in p_dict[TAG_COUNTS]:
        p_dict[WORD_TAG_PROBS][UNK][tag] = math.log((1 / (p_dict[TAG_COUNTS][tag] + num_t)), 10)

    for pre_tag in p_dict[TAG_TAG_COUNTS]:
        p_dict[TAG_TAG_PROBS][pre_tag] = {}
        for post_tag in p_dict[TAG_TAG_COUNTS][pre_tag]:
            p_dict[TAG_TAG_PROBS][pre_tag][post_tag] = math.log(((p_dict[TAG_TAG_COUNTS][pre_tag][post_tag] + 1) / (p_dict[TAG_COUNTS][pre_tag] + num_t)), 10)

    for pre_tag in p_dict[TAG_COUNTS]:
        if pre_tag not in p_dict[TAG_TAG_PROBS]:
            p_dict[TAG_TAG_PROBS][pre_tag] = {}
        for post_tag in p_dict[TAG_COUNTS]:
            if post_tag not in p_dict[TAG_TAG_PROBS][pre_tag]:
                p_dict[TAG_TAG_PROBS][pre_tag][post_tag] = math.log((1 / (p_dict[TAG_COUNTS][pre_tag] + num_t)), 10)

    with open(model_file_name, 'w') as model_file:
        json_obj = json.dumps(p_dict, indent=2)
        model_file.write(json_obj)

    print('Finished...')

if __name__ == "__main__":
    # make no changes here
    train_file = sys.argv[1]
    model_file = sys.argv[2]
    start_time = datetime.datetime.now()
    train_model(train_file, model_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
