#!/usr/bin/python

import sys, os
from PyQt5 import QtCore, QtWidgets, QtGui, Qsci, uic
import builtins, keyword

class MainWindow:

    def __init__(self):
        self.ui = uic.loadUi(os.getcwd() + "/resources/ui/main_window.ui")
        self.runnerPath = 'python' #'idle -i -r'
        self.uiEditorPath = 'designer'
        self.imgEditorPath = 'xdg-open'
        self.fileName = ''
        self.ui.searchPanel.hide()
        self.ui.imagePanel.hide()
        self.ui.fontSelectorPanel.hide()
        self.ui.outputPanel.hide()
        file = open(os.getcwd() + "/resources/ui/main_window.ui")
        out = ''
        #out = str(dir(self.ui.fontFamilySelector.__class__))
        self.ui.textEdit.setText(out)

    def conectarEventos(self):
        self.ui.fontSizeSelector.currentTextChanged.connect(self.fontChange)
        self.ui.fontFamilySelector.currentTextChanged.connect(self.fontChange)
        self.ui.actionEjecutar.triggered.connect(self.run)
        self.ui.actionGuardar.triggered.connect(self.save)
        self.ui.actionScript_Python.triggered.connect(self.newPy)
        self.ui.actionInterfaz_Grafica.triggered.connect(self.newUi)
        self.ui.actionGuardar_Como.triggered.connect(self.saveAs)
        self.ui.actionAbrir.triggered.connect(self.open)
        self.ui.actionBuscar.triggered.connect(self.search)
        self.ui.actionBuscarSiguiente.triggered.connect(self.searchNext)
        self.ui.searchText.keyPressEvent = lambda event: MainWindow.searchKeyPress(self.ui.searchText, event, self)
        self.ui.treeView.keyPressEvent = lambda event: MainWindow.treeKeyPress(self.ui.treeView, event, self)
        self.ui.treeView.doubleClicked.connect(self.on_treeView_doubleClicked)


    def searchKeyPress(text, event, self):
        if (event.key() == QtCore.Qt.Key_Escape):
            self.ui.searchPanel.hide()
        QtWidgets.QLineEdit.keyPressEvent(text, event)

    def treeKeyPress(tree, event, self):
        if (event.key() == QtCore.Qt.Key_Delete):
            item = tree.selectedIndexes()[0]
            reply = QtWidgets.QMessageBox.question(self.ui, "Eliminar", "¿Desea eliminar?", QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No);
            if reply == QtWidgets.QMessageBox.Yes:
                path = self.fileSystemModel.filePath(item)
                if not self.fileSystemModel.remove(item):
                    QtWidgets.QMessageBox.critical(self.ui, "Error al borrar", "No se pudo borrar el archivo")
        QtWidgets.QTreeView.keyPressEvent(tree, event)

    def search(self):
        text = ''
        if self.ui.textEdit.hasSelectedText():
            text = self.ui.textEdit.selectedText()
        self.ui.searchText.setText(text)
        self.ui.searchPanel.show()
        self.ui.searchText.setFocus()

    def searchNext(self):
        text = self.ui.searchText.text()
        self.ui.textEdit.findFirst(text, False, False, False, True)

    def on_treeView_doubleClicked(self, item):
        fileName = self.fileSystemModel.filePath(item)
        fn, ext = os.path.splitext(fileName)
        if ext in ['.png', '.jpg', '.gif']:
            self.openImgFile(fileName)
        elif ext == '.ui':
            self.openUiFile(fileName)
        elif ext != '':
            if fileName != self.fileName:
                self.openFile(fileName)
                self.setCurrentFile(fileName)

    def newUi(self):
        self.openUiFile('')

    def newPy(self):
        try:
            fileName = QtWidgets.QFileDialog.getSaveFileName(self.ui, "Save File",'',"Files (*.py)")[0];
            if fileName != '':
                fileName = fileName if fileName.endswith('.py') else  fileName + '.py'
                self.saveFile(fileName)
                self.openFile(fileName)
                self.setCurrentFile(fileName)
                self.setCurrentPath(os.path.dirname(fileName))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.ui, "Error", str(e))

    def saveAs(self):
        try:
            fileName = QtWidgets.QFileDialog.getSaveFileName(self.ui, "Save File",'',"Files (*.py)")[0];
            if fileName != '':
                self.fileName = fileName if fileName.endswith('.py') else  fileName + '.py'
                self.save()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.ui, "Error", str(e))

    def save(self):
        try:
            if self.fileName == '':
                self.saveAs()
            else:
                self.saveFile(self.fileName, self.ui.textEdit.text())
                self.setCurrentFile(self.fileName)
                self.setCurrentPath(os.path.dirname(self.fileName))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.ui, "Error", str(e))

    def saveFile(self, fileName, content=''):
        file = open(fileName, 'w')
        file.write(content)
        file.close()

    def openUiFile(self, fileName):
        self.process = QtCore.QProcess(self)
        self.process.start(self.uiEditorPath + ' "' + fileName + '"')

    def openImgFile(self, fileName):
        self.ui.imageLabel.setPixmap(QtGui.QPixmap(fileName))
        self.ui.imagePanel.show()

    def openFile(self, fileName):
        file = open(fileName, 'r')
        contents = file.read()
        self.ui.textEdit.setText(contents)
        file.close()

    def open(self):
        try:
            fileName = QtWidgets.QFileDialog.getOpenFileName(self.ui, "Open File",'',"Files (*.py)")[0];
            if fileName != '':
                name, ext = os.path.splitext(fileName)
                self.openFile(fileName)
                self.setCurrentFile(fileName)
                self.setCurrentPath(os.path.dirname(fileName))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.ui, "Error", str(e))

    def setCurrentFile(self, fileName):
        self.fileName = fileName
        self.ui.fileName.setText(os.path.basename(fileName))
        self.ui.setWindowTitle(fileName)
        self.ui.actionEjecutar.setEnabled(True)
        self.ui.actionGuardar.setEnabled(True)

    def modelData(self, index, role):
        if role == QtCore.Qt.DecorationRole:
            info = self.fileInfo(index);
            if info.isFile():
                if info.suffix() == "py":
                    return QtGui.QPixmap("../resources/icons/page_white_text.png")
                elif info.suffix() == "ui":
                    return QtGui.QPixmap("../resources/icons/application_form.png")
                elif info.suffix() in ['png', 'jpg', 'gif']:
                    img = QtGui.QPixmap(info.filePath())
                    return img.scaled(16,16)
                else:
                    return QtGui.QPixmap("../resources/icons/page_white.png")
        return QtWidgets.QFileSystemModel.data(self, index, role);

    def setCurrentPath(self, path):
        self.fileSystemModel = QtWidgets.QFileSystemModel(self.ui.treeView)
        self.fileSystemModel.data = lambda index, role: MainWindow.modelData(self.fileSystemModel, index, role)
        root = self.fileSystemModel.setRootPath(path)
        self.ui.treeView.setModel(self.fileSystemModel)
        self.ui.treeView.setRootIndex(root)
        self.ui.treeView.hideColumn(1)
        self.ui.treeView.hideColumn(2)
        self.ui.treeView.hideColumn(3)
        self.ui.treeView.hideColumn(4)

    def run(self):
        if self.fileName != '':
            self.process = QtCore.QProcess(self)
            self.process.readyReadStandardOutput.connect(self.stdoutReady)
            self.process.readyReadStandardError.connect(self.stderrReady)
            self.process.start(self.runnerPath + ' "' + self.fileName + '"')

    def stdoutReady(self):
        text = '>>' + str(self.process.readAllStandardOutput(), 'utf-8')
        self.append(text)

    def stderrReady(self):
        text = str(self.process.readAllStandardError(), 'utf-8')
        self.append(text)

    def append(self, text):
        cursor = self.ui.outputText.textCursor()
        cursor.movePosition(cursor.End)
        text = text.replace("\\n", '\n')
        cursor.insertText(text)
        self.ui.actionSalida.setChecked(True)

    def setupEditor(self):
        #Font
        self.font = QtGui.QFont()
        self.font.setFamily('Inconsolata')
        self.font.setPointSize(12)
        self.ui.textEdit.setFont(self.font)
        self.ui.textEdit.setMarginsFont(self.font)

        #Syntax
        self.lexer = Qsci.QsciLexerPython()
        self.lexer.setFont(self.font)
        self.lexer.setDefaultFont(self.font)

        #Autocomplete
        api = Qsci.QsciAPIs(self.lexer)
        keys = dir(builtins) + keyword.kwlist
        [api.add(key) for key in keys]
        api.prepare()
        self.ui.textEdit.setLexer(self.lexer)
        self.ui.textEdit.setAutoCompletionThreshold(1)
        self.ui.textEdit.setAutoCompletionSource(Qsci.QsciScintilla.AcsAll)

        #Indent
        self.ui.textEdit.setIndentationWidth(4)
        self.ui.textEdit.setTabWidth(4)
        self.ui.textEdit.setIndentationsUseTabs(False)
        self.ui.textEdit.setAutoIndent(True)

        #Current line
        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_SETINDICATORCURRENT, 0, 0)
        self.ui.textEdit.setCaretLineVisible(True)
        self.ui.textEdit.setCaretLineBackgroundColor(QtGui.QColor("#f0f0ff"))

        #Margin
        self.ui.textEdit.setMarginWidth(0, 15)
        self.ui.textEdit.setMarginWidth(1, 15)
        self.ui.textEdit.setMarginLineNumbers(0, False)
        self.ui.textEdit.setMarginLineNumbers(1, True)
        self.ui.textEdit.setFolding(Qsci.QsciScintilla.BoxedTreeFoldStyle)


    def fontChange(self, newFont):
        try:
            self.font.setPointSize(int(newFont))
        except ValueError:
            self.font.setFamily(newFont)
        self.ui.textEdit.setFont(self.font)
        self.lexer.setFont(self.font)
        self.lexer.setDefaultFont(self.font)

    def iniciar(self):
        self.conectarEventos()
        self.setupEditor()
        self.ui.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.lastWindowClosed.connect(app.quit)
    main_window = MainWindow()
    main_window.iniciar()
    sys.exit(app.exec_())
