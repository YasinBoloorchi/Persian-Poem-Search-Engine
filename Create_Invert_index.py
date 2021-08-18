from os import walk
from time import sleep #remove 
from PersianStemmer import PersianStemmer
import json

# open stop words file
stop_words_file = open('./stop_words.txt', 'r')
stop_words = [word.strip() for word in stop_words_file.readlines()]
stop_words_file.close()


# find all files that are in the given path
datasets_path = './Data/Poems-final'
all_addresses = []
for root, dirs, files in walk(datasets_path):  
    all_addresses += [root+'/'+file for file in files]
    
print('All files founded count: ',len(all_addresses))

# for each file read all persian lines and save them in
# a list, and finally save all readed doc in a big list
dataset = {}
doc_id = 0
for address in all_addresses:
    # print('inserting doc id: ',doc_id, 'of', len(all_addresses), end='\r')
    opened_file = open(address).readlines()
    lines = []
    for line in opened_file:
        if line[0] != '\\' and line[0] != '&':
            lines.append(line.strip())

    dataset[doc_id] = {'text':lines, 'address': address}
    doc_id += 1

print('Listed documents count:   ', len(dataset))
# print('An example of an instance in Big list: \n', dataset[200])

def create_invert_index(dataset, stop_words):
    all_words = []
    ps = PersianStemmer()
    dataset_length = len(dataset)

    # find all words in all of the documents
    print('reading all of the words:')
    for doc_id in range(dataset_length):
        print(doc_id, 'of', len(dataset), ' '*10, end='\r')
        for line in dataset[doc_id]['text']:
            words = line.split(' ')
            for word in words:
                if word not in stop_words:
                    all_words.append(ps.run(word))

    print('all words count: ', len(all_words))
    all_words = list(set(all_words))
    all_words.sort()
    print('all words count after set: ', len(all_words))
    # all_words = all_words[:20]


    invert_index = {}
    all_word_len = len(all_words)
    word_counter = 1
    print('indexing each word')
    for word in all_words:
        print('word indexed: ', word_counter, ' of ', all_word_len, end='\r')
        word_counter += 1
        
        invert_index[word] = {'DF': {} ,'TF': 0}
        
        for doc_id in range(len(dataset)):

            for line in dataset[doc_id]['text']:

                if word in line:
                    invert_index[word]['TF'] += 1
                    if doc_id in invert_index[word]['DF']:
                        invert_index[word]['DF'][doc_id]['frequence'] += 1
                    else:
                        invert_index[word]['DF'][doc_id] = {'frequence': 1}

    return invert_index
        

invert_index = create_invert_index(dataset, stop_words)

print('write invert index into file    ')
invert_index_file = open('./invert_index.json', 'w')
json.dump(invert_index, invert_index_file)
invert_index_file.close()
print('invert index created and wrote into a file')

doc_address = {}
for doc_id in dataset:
    doc_address[doc_id] = dataset[doc_id]['address']

print('write documents address to file')
doc_address_file = open('./doc_address.json', 'w')
json.dump(doc_address, doc_address_file)
doc_address_file.close()
