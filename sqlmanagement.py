import re
import sys
import time

import mysql.connector
import pandas as pd
from mysql.connector import FieldType
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIcon, QIntValidator
from PyQt5.QtWidgets import (QApplication, QComboBox, QLineEdit, QListView,
                             QListWidgetItem, QMainWindow, QPushButton,
                             QRadioButton, QTableView, QTableWidget,
                             QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)
from PyQt5.uic import loadUi
from menu2 import host2,user2,password2
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="products",
    autocommit=True
)

cursor=mydb.cursor(buffered=True)


table_name="deneme1"

class SQLManagement(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        uic.loadUi('gui.ui',self)
        x=1

        cursor.execute("SELECT * FROM "+table_name)
        data=pd.DataFrame(cursor.fetchall())
        clmnnames=cursor.column_names
        print(clmnnames)
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"+table_name+"' ORDER BY ORDINAL_POSITION")
        self.column_names2=pd.DataFrame(cursor.fetchall()).values.tolist()

        self.column_names=[]
        for i in self.column_names2:   
            self.column_names.extend(i)
        txt=""
        self.onlyInt = QIntValidator()
        self.onlydouble=QDoubleValidator()
        self.tdgrow=1
        self.tabledatagrab.setColumnCount(2)  
        self.tabledata.setRowCount(len(data))
        self.tabledata.setColumnCount(len(clmnnames))  
        self.btngrab.clicked.connect(self.grab_clicked)
        self.btnadd.setShortcut("F1")
        self.btnupdate.setShortcut("F2")
        self.btngrab.setShortcut("Return")
        self.btnadd.clicked.connect(self.add_clicked)
        self.btnupdate.clicked.connect(self.update_clicked)
        self.input.returnPressed.connect(self.grab_clicked)
        self.loaddata()
        self.z=1
        self.tabledatagrab.setColumnWidth(0,5)
        self.combo.currentTextChanged.connect(self.combo_changed)
        self.tabledata.doubleClicked.connect(self.select_row)
        self.tabledatagrab.doubleClicked.connect(self.select_grabbed_row)
        
        
    def select_grabbed_row(self):
        self.combocontrol()
        cell=self.tabledatagrab.selectedIndexes()[0].data()
        self.combo.addItem(cell)   
        self.tabledatagrab.removeRow(self.tabledatagrab.currentRow())
        self.combo.setCurrentText(cell)
        
        
    def combocontrol(self):
            
        for row in range(self.tabledatagrab.rowCount()):   
            comboitems = [self.combo.itemText(i) for i in range(self.combo.count())]  
            item = self.tabledatagrab.item(row,0)
            
            print(comboitems)
            if item.text() in comboitems:
                print("true")
                self.combo.removeItem(self.combo.findText(item.text()))
                

          
    def combo_fill(self):
        self.tabledatagrab.clear()
        for i in self.column_names:
            self.combo.addItem(i)
            self.combo.setCurrentText(i)
            
            
    def select_row(self):
        self.combo.clear()
        self.tabledatagrab.clear()
        cells=self.tabledata.selectedIndexes()
        zipped=zip(self.column_names,cells)
        celllist=[]
        self.tabledatagrab.setRowCount(len(cells))
        
        for inx,row in enumerate(zipped):



            self.tabledatagrab.setItem(inx,0, QTableWidgetItem(row[0]))
            self.tabledatagrab.setItem(inx,1, QTableWidgetItem(row[1].data()))
            

            

            
        

############################################################
    def combo_changed(self):
        cbx=self.combo.currentText()
        if self.combo.currentText()=="":
            return
        cursor.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"+table_name+"' AND COLUMN_NAME = '"+cbx+"'")
        column_type=cursor.fetchall()[0][0].lower()


        self.input_hide(column_type)



    def update_clicked(self):
        return
       
    def input_hide(self,column_type):
        match column_type:
            case "datetime":
                self.input.setHidden(True)
                self.inputdt.setHidden(False)
                self.inputd.setHidden(True)
                self.input.setValidator(None)
            case "date":
                self.input.setHidden(True)
                self.inputdt.setHidden(True)
                self.inputd.setHidden(False)
                self.input.setValidator(None)
            case "float"|"int":
                self.input.setHidden(False)
                self.inputdt.setHidden(True)
                self.inputd.setHidden(True)
                self.input.setValidator(self.onlyInt)

            case _:
                self.input.setHidden(False)
                self.inputdt.setHidden(True)
                self.inputd.setHidden(True)
                self.input.setValidator(None)
    
        
    def add_clicked(self):
        if self.tabledatagrab.rowCount() == 0:
            return
        ix=0
        clmnadd=""
        clmnvalues=""
        while ix<self.tabledatagrab.rowCount():
            cc=self.tabledatagrab.item(ix,0).text()
            c_clmn=self.tabledatagrab.item(ix,1).text()
            cursor.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"+table_name+"' AND COLUMN_NAME = '"+cc+"'")
            column_type=cursor.fetchall()[0][0].lower()
            print(column_type)
            
            
            clmnadd=clmnadd+self.tabledatagrab.item(ix,0).text()
            match column_type:
                case "float": 
                    if c_clmn.replace("'","") != "":
                        number=float(c_clmn.replace("'",""))
                        clmnvalues=clmnvalues+" "+str(number)+""
                    else:
                        clmnvalues=clmnvalues+"''"
                case "int":
                    if c_clmn.replace("'","") != "":
                        number=int(c_clmn.replace("'",""))
                        clmnvalues=clmnvalues+" "+str(number)+""
                    else:
                        clmnvalues=clmnvalues+"''"
                case _:
                    clmnvalues=clmnvalues+"'"+self.tabledatagrab.item(ix,1).text()+"'"
            if ix!=self.tabledatagrab.rowCount()-1:
                clmnvalues=clmnvalues+","
                clmnadd=clmnadd+","
            ix+=1     

        query="INSERT INTO "+table_name+" ("+clmnadd+") VALUES ("+clmnvalues+")"
        print(query)

        cursor.execute(query)
        print(query)
        
        clmnnames=cursor.column_names
        self.combo.clear()
        print("kolon sayısı")
        print(self.tabledata.columnCount())
        print("kolonlar")
        print(clmnnames)

        self.tabledatagrab.clear()
        self.z=1
        self.tabledatagrab.setRowCount(0)
        self.combo_fill()
        
    def grab_clicked(self):
        cbx=self.combo.currentText()
        if cbx=="":
            return
        cursor.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"+table_name+"' AND COLUMN_NAME = '"+cbx+"'")
        column_type=cursor.fetchall()[0][0].lower()

        if column_type =="datetime":
            txt=self.inputdt.dateTime()
        elif column_type == "date":
            txt=self.inputd.date()
        else:
            txt=self.input.text()
       

        self.tabledatagrab.setRowCount(self.tabledatagrab.rowCount()+1)
        self.input.clear()
        grabitems=[self.tabledatagrab.item(row,0) for row in range(self.tabledatagrab.rowCount())]
        if cbx in grabitems:
            return

        if column_type=="datetime":
            self.tabledatagrab.setItem(self.tabledatagrab.rowCount()-1,1, QTableWidgetItem(txt.toPyDateTime().strftime('%Y-%m-%d %H:%M:%S')))
        elif column_type=="date":
            self.tabledatagrab.setItem(self.tabledatagrab.rowCount()-1,1, QTableWidgetItem(txt.toPyDate().strftime('%Y-%m-%d')))
        else:
            self.tabledatagrab.setItem(self.tabledatagrab.rowCount()-1,1, QTableWidgetItem(txt))
        self.tabledatagrab.setItem(self.tabledatagrab.rowCount()-1,0, QTableWidgetItem(cbx))

        self.combocontrol()


        


        
    def loaddata(self):

        cursor.execute("SELECT * FROM "+table_name)
        clmnnames=cursor.column_names
        
        for i in range(self.tabledata.columnCount()):
            self.tabledata.setHorizontalHeaderItem(i, QTableWidgetItem(clmnnames[i]))


        data=cursor.fetchall()


        for rn,row in enumerate(data):
            x=0
            while x<len(clmnnames):
                self.tabledata.setItem(rn,x, QTableWidgetItem(str(row[x])))
                x+=1
        
        self.combo_fill()
        cbx=self.combo.currentText()
        cursor.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"+table_name+"' AND COLUMN_NAME = '"+cbx+"'")
        column_type=cursor.fetchall()[0][0].lower()
        self.tabledata.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tabledatagrab.setSelectionBehavior(QtWidgets.QTableView.SelectRows)

       
        match column_type:
            case "datetime":
                self.input.setHidden(True)
                self.inputdt.setHidden(False)
                self.inputd.setHidden(True)
                self.input.setValidator(None)
            case "datetime":
                self.input.setHidden(True)
                self.inputdt.setHidden(True)
                self.inputd.setHidden(False)
                self.input.setValidator(None)
            case "float"|"int":
                self.input.setHidden(False)
                self.inputdt.setHidden(True)
                self.inputd.setHidden(True)
                self.input.setValidator(self.onlyInt)

            case _:
                self.input.setHidden(False)
                self.inputdt.setHidden(True)
                self.inputd.setHidden(True)
                self.input.setValidator(None)




if __name__ == '__main__':
    app =QApplication(sys.argv)
window=SQLManagement()
window.show()
try:

    sys.exit(app.exec())
except SystemExit:
    print('Closing Window...')