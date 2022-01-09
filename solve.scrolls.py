import sys
import re
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot


def parsePathAndJob():
    coords = []
    coords_jobs = []
    with open('sample_submission.json', 'r') as file:
        lines = file.readlines()
        jobs = (re.findall(r'[-+]?[\d]+', lines[1]))
        turns = (re.findall(r'[-+]?[\d]+', lines[2]))
        for i in range(0, len(turns), 2):
            coords.append((int(turns[i]), int(turns[i+1])))
        for i in range(0, len(jobs), 2):
            coords_jobs.append((int(jobs[i]), int(jobs[i+1])))
    return coords, coords_jobs


def inputValues(table: QTableWidget):
    with open('table.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rowNum = 0
        for row in reader:
            colNum = 0
            for item in row:
                table.setItem(rowNum, colNum,
                              QTableWidgetItem("{}".format(item)))
                colNum += 1
            rowNum += 1


def printPath(current_path):
    with open('path.txt', 'a') as file:
        file.write('path: ' + current_path + '\n')


def printJob(current_job):
    with open('job.txt', 'a') as file:
        file.write('job: ' + current_job + '\n')


class App(QWidget):
    def printStats(self):
        with open('stats.txt', 'a') as file:
            file.write('p: {}, t: {}, j: {}, SUM = {}\n'.format(
                self.gifts, len(self.turns), len(self.jobs),
                3600/(len(self.turns) + len(self.jobs))*pow(1.1, self.gifts)))

    def __init__(self):
        super().__init__()
        self.title = 'allcups'
        self.left = 0
        self.top = 0
        self.width = 1000
        self.height = 600
        self.initUI()

        # row, column. Both starts with 1, so remember to -1
        self.previous = (49, 57)
        self.current = (49, 57)
        self.suggested_current = (49, 57)
        self.suggested_previous = (49, 57)
        self.vector = (0, 0)

        self.gifts = 0
        self.turns = []
        printPath("### NEWRUN ###")
        self.jobs = []
        printJob("### NEWRUN ###")

        self.reverted_count = 0

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.tableWidget.keyPressEvent = self.myKeyPressEvent

        # Show widget
        self.show()

    def colorTable(self):
        for row in range(101):
            for col in range(101):
                self.colorCell(row, col)

    def colorCell(self, row, col, allowRecolorTurns=False):
        area_type = self.get_area_type(row, col)
        if area_type == 0:
            self.highlight(row, col, QColor(90, 155, 213), allowRecolorTurns)
        elif area_type == 1:
            self.highlight(row, col, QColor(220, 235, 247), allowRecolorTurns)
        elif area_type == 2:
            self.highlight(row, col, QColor(197, 223, 178), allowRecolorTurns)
        elif area_type == 3:
            self.highlight(row, col, Qt.green)
        elif area_type == 4:
            self.highlight(row, col, QColor(253, 217, 98), allowRecolorTurns)
        elif area_type == 9:
            self.highlight(row, col, QColor(196, 89, 17), allowRecolorTurns)
        else:
            pass

    def createTable(self):
        # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(100)
        self.tableWidget.setColumnCount(100)
        inputValues(self.tableWidget)
        self.colorTable()
        self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.verticalHeader().setDefaultSectionSize(21)
        # self.tableWidget.horizontalHeader().setDefaultSectionSize(35)

        self.tableWidget.itemClicked.connect(self.remove_highlight_available)
        self.tableWidget.itemClicked.connect(self.print_on_click)
        self.tableWidget.itemClicked.connect(self.highlight_square_center)
        self.tableWidget.itemClicked.connect(self.highlight_available)

        self.tableWidget.scrollToItem(self.tableWidget.item(
            49, 57), QAbstractItemView.PositionAtCenter)

    @ pyqtSlot()
    def highlight_square_center(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            self.suggested_previous = self.suggested_current
            self.suggested_current = (self.current[0] + self.vector[0],
                                      self.current[1] + self.vector[1])
            if (self.tableWidget.item(self.suggested_current[0], self.suggested_current[1]) != None and
                    self.suggested_current[0] >= 0 and self.suggested_current[1] >= 0):
                self.tableWidget.item(self.suggested_current[0], self.suggested_current[1]).setBackground(
                    Qt.blue)
                self.tableWidget.scrollToItem(self.tableWidget.item(
                    self.suggested_current[0], self.suggested_current[1]), QAbstractItemView.PositionAtCenter)
            if (self.suggested_previous[0] >= 0 and self.suggested_previous[1] >= 0):
                self.colorCell(
                    self.suggested_previous[0], self.suggested_previous[1])

    def get_area_type(self, row, column):
        if (self.tableWidget.item(row, column) != None):
            return int(self.tableWidget.item(row, column).text().split()[0])
        return -1

    @ pyqtSlot()
    def highlight_available(self):
        if (self.suggested_current != None):
            curRow = self.current[0]
            curCol = self.current[1]
            sugRow = self.suggested_current[0]
            sugCol = self.suggested_current[1]
            area_type = self.get_area_type(curRow, curCol)
            if area_type == 0:  # ice
                self.highlight(sugRow, sugCol, Qt.yellow)
            elif area_type == 1 or area_type == 3:  # snow, radius = 1
                for row in range(sugRow - 1, sugRow + 2):
                    for col in range(sugCol - 1, sugCol + 2):
                        self.highlight(row, col, Qt.yellow)
            elif area_type == 2 or area_type == 4:  # road, start or drop, radius = 3
                for row in range(sugRow - 2, sugRow + 3):
                    for col in range(sugCol - 2, sugCol + 3):
                        self.highlight(row, col, Qt.yellow)

    def remove_highlight_available(self):
        curRow = self.suggested_current[0]
        curCol = self.suggested_current[1]
        for row in range(curRow - 3, curRow + 4):
            for col in range(curCol - 3, curCol + 4):
                if (self.tableWidget.item(row, col) != None and
                        self.tableWidget.item(row, col).background() == Qt.yellow):
                    self.colorCell(row, col)

    def highlight(self, row, column, color, allowRecolorTurns=False):
        if (self.tableWidget.item(row, column) != None):
            if (self.tableWidget.item(row, column).background() != Qt.green or allowRecolorTurns):
                self.tableWidget.item(row, column).setBackground(color)

    def enhance_area(self, row, column):
        area_type = self.get_area_type(row, column)
        if area_type == 0:
            self.tableWidget.item(row, column).setText('1')
        elif area_type == 1:
            self.tableWidget.item(row, column).setText('2')
        self.colorCell(row, column)
        # self.jobs.append("[{}, {}]".format(row + 1, column + 1))
        # they invert axis
        self.jobs.append("[{}, {}]".format(column, row))
        printJob(', '.join(self.jobs))

    def myKeyPressEvent(self, event):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            row = currentQTableWidgetItem.row()
            column = currentQTableWidgetItem.column()
            self.enhance_area(row, column)

    def contextMenuEvent(self, event):
        self.revert_turn()

    def revert_turn(self):
        self.turns.pop()
        self.remove_highlight_available()
        self.colorCell(
            self.suggested_current[0], self.suggested_current[1])
        self.colorCell(
            self.current[0], self.current[1], True)
        text = self.tableWidget.item(self.current[0], self.current[1]).text()
        self.tableWidget.item(self.current[0], self.current[1]).setText(
            text[0:text.rfind(' [')])
        self.suggested_current = self.suggested_previous
        self.current = self.previous
        self.highlight_available()

    @ pyqtSlot()
    def print_on_click(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            self.previous = self.current
            self.current = (currentQTableWidgetItem.row(),
                            currentQTableWidgetItem.column())
            self.calc_vector()
            curRow = self.current[0]
            curCol = self.current[1]
            self.highlight(curRow, curCol, Qt.green)
            # they don't invert axis!
            turn = "[{}, {}]".format(self.vector[1], self.vector[0])
            self.turns.append(turn)
            self.tableWidget.item(curRow, curCol).setText(
                self.tableWidget.item(curRow, curCol).text() + ' ' + turn)
            printPath(', '.join(self.turns))
            if self.get_area_type(curRow, curCol) == 4:
                self.gifts += 1
            self.printStats()

    def calc_vector(self):
        self.vector = (self.current[0] - self.previous[0],
                       self.current[1] - self.previous[1])

    def highlight_parsed_path(self):
        start = (49, 57)
        previous = start
        current = start
        pathAndJob = parsePathAndJob()
        for cell in pathAndJob[1]:
            self.enhance_area(cell[1], cell[0])
        for cell in pathAndJob[0]:
            previous = current
            current = (current[0] + cell[1], current[1] + cell[0])
            if self.tableWidget.item(current[0], current[1]) != None:
                vector = (current[0] - previous[0],
                          current[1] - previous[1])
                turn = "[{}, {}]".format(vector[1], vector[0])
                self.tableWidget.item(current[0], current[1]).setText(
                    self.tableWidget.item(current[0], current[1]).text() + ' ' + turn)
                self.highlight(current[0], current[1], Qt.darkGreen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    if len(sys.argv) >= 2:
        ex.highlight_parsed_path()
    sys.exit(app.exec_())
