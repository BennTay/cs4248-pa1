# python3.5 runtagger.py <test_file_absolute_path> <model_file_absolute_path> <output_file_absolute_path>
# python runtagger.py sents.test model-file sents.out
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
START = '<s>'
END = '<e>'

class WordToken:
    def __init__(self, word, tag_list=None):
        self.word = word
        self.tags = []
        self.best_tag = None
        self.emission_probs = {}
        self.transition_probs = {}
        
        if word == START:
            self.tags.append(START)
            self.best_tag = START
        elif word == END:
            self.tags.append(END)
            self.best_tag = END
        else:
            self.tags = tag_list

    def max_transition(self, next):
        max = -sys.maxsize
        for curr in self.transition_probs:
            p = self.transition_probs[curr][next]
            if p > max:
                max = p
        return max

    def back_track(self, next):
        max = -sys.maxsize
        max_tag = None
        for curr in self.transition_probs:
            p = self.transition_probs[curr][next]
            if p > max:
                max = p
                max_tag = curr
        if self.word != END:
            self.best_tag = max_tag

    def get_answer(self):
        return self.word + '/' + self.best_tag

def tag_sentence(test_file_name, model_file_name, out_file_name):
    # write your code here. You can add functions as well.
    p_dict = {}
    sentence_list = []

    with open(model_file_name, 'r') as model_file:
        p_dict = json.loads(model_file.read())

    tag_list = []

    for tag in p_dict[TAG_COUNTS]:
        tag_list.append(tag)
    tag_list.remove(START)

    with open(test_file_name, 'r') as test_file:
        startToken = WordToken(START)
        endToken = WordToken(END)

        for sentence in test_file:
            sentence_tokens = sentence.split()
            wordToken_seq = []
            wordToken_seq.append(startToken)
            for word in sentence_tokens:
                if word in p_dict[WORD_COUNTS]:
                    wordToken_seq.append(WordToken(word, tag_list=tag_list))
                else:
                    wordToken_seq.append(WordToken(UNK, tag_list=tag_list))
            wordToken_seq.append(endToken)

            for i in range(len(wordToken_seq)):
                curr_token = wordToken_seq[i]

                if curr_token.word == START:
                    next_token = wordToken_seq[i+1]
                    curr_token.transition_probs[START] = {}
                    for next_tag in next_token.tags:
                        curr_token.transition_probs[START][next_tag] = p_dict[TAG_TAG_PROBS][START][next_tag]

                elif curr_token.word == END:
                    prev_token = wordToken_seq[i-1]
                    curr_token.emission_probs[END] = prev_token.max_transition(END)
                else:
                    next_token = wordToken_seq[i+1]
                    prev_token = wordToken_seq[i-1]

                    for curr_tag in curr_token.tags:
                        curr_token.emission_probs[curr_tag] = prev_token.max_transition(curr_tag) + p_dict[WORD_TAG_PROBS][curr_token.word][curr_tag]

                        curr_token.transition_probs[curr_tag] = {}
                        for next_tag in next_token.tags:
                            curr_token.transition_probs[curr_tag][next_tag] = curr_token.emission_probs[curr_tag] + p_dict[TAG_TAG_PROBS][curr_tag][next_tag]



            for i in range(len(wordToken_seq)-2, -1, -1):
                wordToken_seq[i].back_track(wordToken_seq[i+1].best_tag)

            wordToken_seq.pop(0)
            wordToken_seq.pop(len(wordToken_seq)-1)

            sentence = ''
            for word_token in wordToken_seq:
                sentence += word_token.get_answer()
                sentence += ' '
            sentence = sentence[:-1]
            sentence += '\n'
            sentence_list.append(sentence)

    with open(out_file_name, 'w') as out_file:
        for sentence in sentence_list:
            out_file.write(sentence)
    
    print('Finished...')

if __name__ == "__main__":
    # make no changes here
    test_file = sys.argv[1]
    model_file = sys.argv[2]
    out_file = sys.argv[3]
    start_time = datetime.datetime.now()
    tag_sentence(test_file, model_file, out_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
