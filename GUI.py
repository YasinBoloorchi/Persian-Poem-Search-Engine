# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!
from PersianStemmer import PersianStemmer
from PyQt5 import QtCore, QtGui, QtWidgets
import json

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, invert_index, stop_words, query, doc_address, ps):
        self.ps = ps
        self.invert_index = invert_index
        self.stop_words = stop_words
        self.query = query
        self.doc_address = doc_address
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.searchButton = QtWidgets.QPushButton(self.centralwidget)
        self.searchButton.setGeometry(QtCore.QRect(300, 200, 161, 51))
        self.searchButton.setObjectName("searchButton")
        self.query_input = QtWidgets.QLineEdit(self.centralwidget)
        self.query_input.setGeometry(QtCore.QRect(220, 100, 321, 61))
        self.query_input.setObjectName("query_input")
        self.searchResult = QtWidgets.QTextBrowser(self.centralwidget)
        self.searchResult.setGeometry(QtCore.QRect(10, 280, 781, 301))
        self.searchResult.setObjectName("searchResult")
        self.logoImage = QtWidgets.QLabel(self.centralwidget)
        self.logoImage.setGeometry(QtCore.QRect(230, 20, 301, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.logoImage.setFont(font)
        self.logoImage.setAlignment(QtCore.Qt.AlignCenter)
        self.logoImage.setObjectName("logoImage")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.searchButton.clicked.connect(self.my_function)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def my_function(self):
        
        def get_query_words(query, stop_words):
            query_words = []
            for word in query:
                if word not in self.stop_words:
                    query_words.append(self.ps.run(word))
            return query_words

        query_words = get_query_words(self.query_input.text().split(' '), self.stop_words)
        print('query words: ', query_words)


        def get_keys_tf(query_words, invert_index):
            keys_tf = {}
            for word in query_words:
                for key in self.invert_index.keys():
                    if key == word:
                        keys_tf[word] = {'TF':self.invert_index[word]['TF'], 'doc_ids': self.invert_index[word]['DF'].keys()}

            return keys_tf

        keys_tf = get_keys_tf(query_words, self.invert_index)

        # find minimum TF in all of query words
        min_tf = ['empty', 10**100]
        for word in keys_tf:
            if min_tf[1] > keys_tf[word]['TF']:
                min_tf[1] = keys_tf[word]['TF']
                min_tf[0] = word

        print('min_tf: ', min_tf)
        
        first_top_results = []
        try:
            first_top_results = [doc_id for doc_id in self.invert_index[min_tf[0]]['DF'].keys()]
        except:
            pass
        
        # finding all documents id in all the query words 
        all_doc_id_for_words = []
        for word in query_words:
            if word in self.invert_index:
                for doc_id in self.invert_index[word]['DF'].keys():
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
        elif len(query_words)==1:
            if len(second_top_results) > 1:
                final_results = first_top_results[:5]
                final_results += second_top_results

            final_results = first_top_results
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
        self.searchResult.clear()
        for doc_id in final_results:
            self.searchResult.append(self.doc_address[doc_id])
            doc_file = open(self.doc_address[doc_id])
            for line in doc_file.readlines():
                if line[0] != '\\' and line[0] != '&':
                    self.searchResult.append(line)
            self.searchResult.append('*'*50)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.searchButton.setText(_translate("MainWindow", "Search"))
        self.logoImage.setText(_translate("MainWindow", "Yasin Search Engine"))

def open_files():
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

    return invert_index, stop_words, query, doc_address


if __name__ == "__main__":
    import sys

    invert_index, stop_words, query, doc_address = open_files()
    
    ps = PersianStemmer()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, invert_index, stop_words, query, doc_address, ps)
    MainWindow.show()
    sys.exit(app.exec_())

