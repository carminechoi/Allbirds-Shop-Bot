import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import aaa
import ShopInfo
from urllib.request import urlopen
from multiprocessing import cpu_count, Pool, Process
from functools import partial
import threading
#import MainWindow


class App(QDialog):

    def __init__(self, keyword, typeRadio, typePrice):
        super().__init__()
        #self.title = 'PyQt5 simple window'
        self.left = 800
        self.top = 100
        self.width = 1024
        self.height = 768
        self.is_valid_search = True
        #self.label = QLabel()
        #self.mov = QLabel()

        self.keyword = keyword
        self.type = typeRadio
        self.price = typePrice
        #placeholder
        self.itemDict = {}
        self.bckbtn = QPushButton("Back", self)
        self.bckbtn.resize(100, 32)
        self.bckbtn.move(750, 650)

        self.products = aaa.getProducts()
        pool = Pool(cpu_count())
        self.testProducts = [x for x in pool.map(partial(aaa.findKeyword, keyword=keyword, type=typeRadio,
                                                         price=typePrice), self.products) if x is not None]

        # check if products is empty, if it is go back to search page
        if not self.testProducts:
            self.is_valid_search = False

        #self.testProducts = pool.map(aaa.findKeyword(products, keyword, typeRadio)
        ShopInfo.ShoppingKeys["Products"] = self.testProducts
        print(self.testProducts[0])
        result_list = pool.map(getProdJsonList, self.testProducts)
        self.prodDict = {}
        for prod in result_list:
            self.prodDict[prod[0]] = [prod[1], prod[2]]

        print("Done")
        self.initUI()

    def loading(self):
        pass
        msg = QMessageBox()
        #alabel = self.loadingScreen()
        #msg.setLayout(alabel)
        msg.setText("Please wait for items to load.")
        msg.exec()

    def processProducts(self):
        print('run')
        products = aaa.getProducts()
        pool = Pool(cpu_count())
        self.testProducts = [x for x in pool.map(partial(aaa.findKeyword, keyword=self.keyword, type=self.type), products)
                             if x is not None]
        # self.testProducts = pool.map(aaa.findKeyword(products, keyword, typeRadio)
        ShopInfo.ShoppingKeys["Products"] = self.testProducts
        print(self.testProducts[0])
        result_list = pool.map(getProdJsonList, self.testProducts)
        self.prodDict = {}
        for prod in result_list:
            self.prodDict[prod[0]] = [prod[1], prod[2]]

    def initUI(self):
        # self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)

        #self.createTable()
        #tableLayout = QHBoxLayout()
        #tableLayout.addWidget(self.table)
        #self.setLayout(tableLayout)


        self.tabLayout = QTabWidget()
        layout = QVBoxLayout()
        tab1 = QWidget()
        tab2 = QWidget()

        self.createTable()

        tablelayout = QHBoxLayout()
        tablelayout.setContentsMargins(5, 5, 5, 5)
        tablelayout.addWidget(self.table)

        searchLayout = QVBoxLayout()
        searchLayout.addLayout(tablelayout)
        searchLayout.addWidget(self.bckbtn)

        tab1.setLayout(searchLayout)

        self.table2 = QTableWidget(0, 5)
        self.createAddToCartTable(1)

        table2layout = QHBoxLayout()
        table2layout.setContentsMargins(5, 5, 5, 5)
        table2layout.addWidget(self.table2)

        orderbutton = QPushButton('Order', self)
        orderbutton.clicked.connect(lambda: self.order())
        table2layout.addWidget(orderbutton)

        tab2.setLayout(table2layout)


        self.tabLayout.addTab(tab1, "Items")
        self.tabLayout.addTab(tab2, "Cart")

        self.tabLayout.currentChanged.connect(self.createAddToCartTable)

        layout.addWidget(self.tabLayout)
        self.setLayout(layout)

        #self.loadingScreen()

        self.show()


    def createTable(self):
        headerTitles = ("Name", "Image", "Size", "Quantity", "Price", "Add to Cart")
        length = len(self.testProducts)
        print(length)
        self.table = QTableWidget(length, 6)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        QTableWidget.setHorizontalHeaderLabels(self.table, headerTitles)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

        for i in range(length):
            self.itemDict[i] = []
            for k in range(6):
                if(k==0):
                    self.table.setItem(i, k, QTableWidgetItem(self.testProducts[i]['title']))
                    self.itemDict[i].append(self.testProducts[i]['title'])
                    #print(self.testProducts[i])
                elif (k==1):
                    label = QLabel()
                    pixmap = QPixmap()
                    try:
                        pixmap.loadFromData(self.prodDict[self.testProducts[i]['title']][1])
                        #print("loaded")
                    except:
                        pixmap.load('brgr.png')

                    label.setPixmap(pixmap.scaledToWidth(350))
                    self.table.setCellWidget(i, k, label)

                elif (k==2):
                    sizes = aaa.getSizes(self.testProducts[i])
                    styleComboBox = QComboBox()
                    styleComboBox.addItems(sizes)
                    self.table.setCellWidget(i, k, styleComboBox)
                    self.itemDict[i].append(styleComboBox)
                elif (k==3):
                    quantityBox = QSpinBox(self.table)
                    quantityBox.setValue(0)
                    pSize = str(self.itemDict[i][1].currentText())
                    #print(self.prodDict[self.testProducts[i]['title']][0]['product']['variants'])
                    maxQuantity = 0
                    # get variants from prodDict which has quantity amount
                    for var in self.prodDict[self.testProducts[i]['title']][0]['product']['variants']:
                        if pSize == var['option1']:
                            maxQuantity = var['inventory_quantity']
                            break
                    quantityBox.setMaximum(maxQuantity)
                    self.table.setCellWidget(i, k, quantityBox)
                    self.itemDict[i].append(quantityBox)
                elif (k==4):
                    self.table.setItem(i, k, QTableWidgetItem(self.testProducts[i]['variants'][0]['price']))
                    self.itemDict[i].append(self.testProducts[i]['variants'][0]['price'])
                elif (k==5):
                    button = QPushButton('Add to Cart', self.table)
                    button.clicked.connect(lambda: self.on_click())
                    self.table.setCellWidget(i, k, button)
                    #self.table.setItem(i, k, QTableWidgetItem(button))
                else:
                    self.table.setItem(i, k, QTableWidgetItem("oof"))
        #print(self.itemDict)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        print(self.itemDict)


    def createAddToCartTable(self, tabIndex):
        print("Tab Clicked, Index: "+str(tabIndex))
        if(tabIndex!=1):
            return
        while(self.table2.rowCount() > 0):
            self.table2.removeRow(0)
        headerTitles = ("Name", "Size", "Quantity", "Price", "Remove From Cart")
        header = self.table2.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        QTableWidget.setHorizontalHeaderLabels(self.table2, headerTitles)
        #self.table2.setSelectionMode(QAbstractItemView.NoSelection)

        length = len(ShopInfo.ShoppingKeys["Cart"])
        print(length)
        initRowPos = self.table2.rowCount()
        if length > initRowPos:
            for i in range(length-initRowPos):
                print("yes")
                rowPos = self.table2.rowCount()
                self.table2.insertRow(rowPos)
                self.table2.setItem(rowPos, 0, QTableWidgetItem(ShopInfo.ShoppingKeys["Cart"][rowPos]['title']))
                self.table2.setItem(rowPos, 1, QTableWidgetItem(ShopInfo.ShoppingKeys["Sizes"][rowPos]))
                self.table2.setItem(rowPos, 2, QTableWidgetItem(str(ShopInfo.ShoppingKeys["Quantities"][rowPos])))
                self.table2.setItem(rowPos, 3, QTableWidgetItem(ShopInfo.ShoppingKeys["Prices"][rowPos]))
                button = QPushButton('Remove From Cart', self.table2)
                button.clicked.connect(lambda: self.remove_cart())
                self.table2.setCellWidget(rowPos, 4, button)

        self.table2.resizeRowsToContents()
        self.table2.resizeColumnsToContents()


    def order(self):
        print("ORDERING")
        print(ShopInfo.ShoppingKeys["Cart"])
        print(ShopInfo.ShoppingKeys["Sizes"])
        print(ShopInfo.ShoppingKeys["Quantities"])
        aaa.CompleteShopping()

    #pyqtSlot()
    def on_click(self):
        button = qApp.focusWidget()
        index = self.table.indexAt(button.pos())
        if self.itemDict.get(index.row())[2].value() == 0:
            print("Did not add to cart. Please choose quantity.")
            return
        if self.testProducts[index.row()] in ShopInfo.ShoppingKeys["Cart"]:
            print("Already in Cart")
            return
        print(self.itemDict.get(index.row())[0] + ' Added to Cart')
        ShopInfo.ShoppingKeys["Cart"].append(self.testProducts[index.row()])
        ShopInfo.ShoppingKeys["Sizes"].append(str(self.itemDict.get(index.row())[1].currentText()))
        ShopInfo.ShoppingKeys["Quantities"].append(self.itemDict.get(index.row())[2].value())
        ShopInfo.ShoppingKeys["Prices"].append(self.itemDict.get(index.row())[3])


    def remove_cart(self):
        button = qApp.focusWidget()
        index = self.table2.indexAt(button.pos())
        print(ShopInfo.ShoppingKeys["Cart"][index.row()]['title'] + " removed")
        try:
            del ShopInfo.ShoppingKeys["Cart"][index.row()]
            del ShopInfo.ShoppingKeys["Sizes"][index.row()]
            del ShopInfo.ShoppingKeys["Quantities"][index.row()]
            del ShopInfo.ShoppingKeys["Prices"][index.row()]
            self.table2.removeRow(index.row())
            self.createAddToCartTable(1)
            self.show()
        except:
            print("Unable to remove")

    # change quantity cap
    def on_size_change(self):
        pass

    def loadingScreen(self):
        label = QLabel("Loading . . .")
        vbox = QVBoxLayout()
        vbox.addWidget(label)

        movie = QMovie("./PacLoader.gif")
        mov = QLabel()
        mov.setMovie(movie)
        movie.start()
        vbox.addWidget(mov)
        return vbox

        #self.show()

def getProdJsonList(prod):
    # tuple (name, json, image)
    prod = (prod['title'], aaa.getProductJson(prod['handle']), urlopen(prod['images'][0]['src']).read())
    return prod


'''
    def loadingScreen(self):
        vbox = QVBoxLayout()
        label = self.changeLabel("Loading . . .")
        #vbox.addStretch(1)
        vbox.addWidget(label)

        movie = QMovie("./PacLoader.gif")
        mov = QLabel()
        mov.setMovie(movie)
        #mov.setGeometry(450, 150, 200, 200)
        # self.mov.move(500, 400)
        movie.start()
        #vbox.addStretch(1)
        vbox.addWidget(mov)

        self.setLayout(vbox)
        
    def showOption(self):
        pass

    def showImage(self, src):
        print("Loading...")
        self.imagePop = PopupImage(src)
        #self.imagePop.show()


class PopupImage(QDialog):
    def __init__(self,src):
        super().__init__()
        self.src = src
        self.layout = QVBoxLayout()
        self.initUI()
        self.setLayout(self.layout)
        self.show()

    def initUI(self):
        self.label = QLabel()
        self.pixmap = QPixmap()

        try:
            data = urlopen(self.src).read()
            self.pixmap.loadFromData(data)
            print("loaded")
            # pixmap.loadFromData(self.testProducts[i]['images'][0]['src'])
        except:
            self.pixmap.load('brgr.png')

        self.label.setPixmap(self.pixmap.scaledToWidth(600))
        # self.setGeometry(200, 200, 600, 600)
        self.layout.addWidget(self.label)
        # self.initUI()
'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App("Nike","footwear")
    sys.exit(app.exec_())

