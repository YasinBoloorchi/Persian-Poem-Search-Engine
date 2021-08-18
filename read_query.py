from PersianStemmer import PersianStemmer
import json

# create a stemmer function
ps = PersianStemmer()

# open invert index file and put it in dictionary
print('Loading invert index')
invert_index_file = open('./invert_index.json')
invert_index = json.load(invert_index_file)
invert_index_file.close()
print('Invert index loaded')


# open stop words file
stop_words_file = open('./stop_words.txt', 'r')
stop_words = [word.strip() for word in stop_words_file.readlines()]
stop_words_file.close()

# open query file and read it
query_file = open('./query.txt', 'r')
query = query_file.readline()
query_file.close()
query = query.strip().split(' ')

# open documents addresses
doc_address_file = open('./doc_address.json', 'r')
doc_address = json.load(doc_address_file)
doc_address_file.close()


def get_query_words(query, stop_words):
    query_words = []
    for word in query:
        if word not in stop_words:
            query_words.append(ps.run(word))
    return query_words

query_words = get_query_words(query, stop_words)

def get_keys_tf(query_words, invert_index):
    keys_tf = {}
    for word in query_words:
        for key in invert_index.keys():
            if key == word:
                keys_tf[word] = {'TF':invert_index[word]['TF'], 'doc_ids': invert_index[word]['DF'].keys()}

    return keys_tf

keys_tf = get_keys_tf(query_words, invert_index)

# find minimum TF in all of query words
min_tf = ['empty', 10*100]
for word in keys_tf:
    # print(word,keys_tf[word]['TF'])
    if min_tf[1] > keys_tf[word]['TF']:
        min_tf[1] = keys_tf[word]['TF']
        min_tf[0] = word

first_top_results = [doc_id for doc_id in invert_index[min_tf[0]]['DF'].keys()]
# print('first top result: ', first_top_results)

# finding all documents id in all the query words 
all_doc_id_for_words = []
for word in query_words:
    if word in invert_index:
        for doc_id in invert_index[word]['DF'].keys():
            all_doc_id_for_words.append(doc_id)


def doc_repeat_count(all_doc_id_for_words):
    all_doc_id_set = list(set(all_doc_id_for_words))
    doc_id_counts = {}

    for this_doc_id in all_doc_id_set:
        doc_id_counts[this_doc_id] = 0
    
        for doc_id in all_doc_id_for_words:
            if this_doc_id == doc_id:
                doc_id_counts[this_doc_id] += 1
    
    second_top_results = []
    for doc_id in doc_id_counts:
        if doc_id_counts[doc_id] > 1:
            second_top_results.append([doc_id_counts[doc_id], doc_id])

    second_top_results.sort(reverse=True)
    second_top_results = [doc_id[1] for doc_id in second_top_results]
    return second_top_results


second_top_results = doc_repeat_count(all_doc_id_for_words)


print('First result: ', first_top_results)
print('Second result: ', second_top_results)


# calculating final results
if len(first_top_results) <= 10:
    final_results = first_top_results
    final_results += second_top_results
else:
    final_results = second_top_results[:4]
    final_results += first_top_results[:5]
    final_results += second_top_results[3:]

print('Final results: ', final_results[:10])

temp_final_result = []
for doc_id in final_results:
    if doc_id not in temp_final_result:
        temp_final_result.append(doc_id)

final_results = temp_final_result

# just use top 10 results 
final_results = final_results[:10]

# show final results with their addresses
print('\n\n\n Search Results:')
for doc_id in final_results:
    print(doc_id, '-->', doc_address[doc_id], end='\n\n')
    # print('*'*50)
    # res_file = open(doc_address[doc_id], 'r')
    # for line in res_file.readlines():
    #     print(line)

    # print('*'*50)