'''
Created on Jun 18, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QDialog, QFileDialog, QGridLayout, QLabel, QPushButton, QComboBox,\
  QStringListModel, QMessageBox, QLineEdit, QCheckBox, QApplication
from PySide.QtCore import Qt
from visualscrape.lib.export import FileExporter
import os
from PySide.QtCore import Signal

class ExportDialog(QDialog):
  """Allows the choice of format and browsing to a save location
     Call data() after exec_()"""
  
  def __init__(self, parent=None):
    super(ExportDialog, self).__init__(parent)
    self._output_folder = None
    self.setModal(True)
    layout_main = QGridLayout()
    label_choose_format = QLabel(self.tr("Choose format"))
    self.combo_choose_format = QComboBox()
    self.combo_choose_format.setModel(QStringListModel(FileExporter.FORMATS_AVAILABLE))
    label_saveto = QLabel(self.tr("Save location"))
    button_saveto = QPushButton(self.tr("Browse ..."))
    button_saveto.clicked.connect(self._openFolderChoiceDialog)
    self.label_output = QLabel()
    button_export = QPushButton(self.tr("Export"))
    button_export.clicked.connect(self.accept)
    button_cancel = QPushButton(self.tr("Cancel"))
    button_cancel.clicked.connect(self.reject)
    row = 0; col = 0;
    layout_main.addWidget(label_choose_format, row, col, 1, 2)
    col += 2
    layout_main.addWidget(self.combo_choose_format, row, col, 1, 2)
    row += 1; col -= 2;
    layout_main.addWidget(label_saveto, row, col, 1, 2)
    col += 2
    layout_main.addWidget(button_saveto, row, col, 1, 2)
    row += 1; col -= 2;
    layout_main.addWidget(self.label_output, row, col, 1, 4)
    row += 1; col += 2
    layout_main.addWidget(button_export, row, col)
    col += 1
    layout_main.addWidget(button_cancel, row, col)
    self.setWindowTitle(self.tr("Export Parameters"))
    self.setLayout(layout_main)
    
  def data(self):
    if self._output_folder is None: return None
    else:
      return ExportInfo(self.combo_choose_format.currentText(), self._output_folder)
  
  def _openFolderChoiceDialog(self):
    folder = QFileDialog.getExistingDirectory(self, caption=self.tr("Choose output directory"))
    if not folder:
      self.label_output.setText("<font style='color:red;'>" + self.tr("Please choose an output folder") 
                                + "</font>")
    else: 
      self.label_output.setText(folder)
      self._output_folder = folder
    
class ExportInfo(object):
    def __init__(self, fmt, loc):
      self.format = fmt
      self.location = loc
      
    
class AlreadyExistsDialog(QMessageBox):
  """
  Access it's ret property to get a result as a constant
  """
  OVERWRITE = 1
  CANCEL = 2
  def __init__(self, fname, parent=None):
    super(AlreadyExistsDialog, self).__init__(parent)
    self.setText(self.tr("{0} already exists".format(os.path.normpath(fname))))
    self.setStandardButtons(QMessageBox.Cancel)
    self.button_overwrite = self.addButton(self.tr("Overwrite"), QMessageBox.ActionRole)
    self.setWindowTitle(self.tr("Warning"))
    
  def _result(self):
    if self.clickedButton() == self.button_overwrite:
      return self.OVERWRITE
    else: return self.CANCEL
    
  ret = property(_result)
  
class FindReplaceDialog(QDialog):
  """A find and replace dialog that has a search-as-I-type option
     The caller should keep a reference to this dialog, or delete it
     explicitly"""
  find_text_changed = Signal(str)
  replace_committed = Signal(str, str)
  find_cancelled = Signal()
  
  def __init__(self, parent=None):
    super(FindReplaceDialog, self).__init__(parent)
    layout = QGridLayout()
    # prepare the widgets
    label_find = QLabel(self.tr("Find"))
    self.lineedit_find = QLineEdit()
    label_replace = QLabel(self.tr("Replace"))
    self.lineedit_replace = QLineEdit()
    self.checkbox_dynamic_find = QCheckBox(self.tr("Search as I type"))
    self.button_find = QPushButton(self.tr("Find"))
    self.button_replace = QPushButton(self.tr("Replace"))
    button_cancel = QPushButton(self.tr("Cancel"))
    # connect the signals
    self.lineedit_find.textEdited.connect(self._findEdited)
    self.button_find.clicked.connect(self._emitFind)
    self.checkbox_dynamic_find.stateChanged.connect(self._dynamicFindChanged)
    self.button_replace.clicked.connect(self._emitReplacement)
    button_cancel.clicked.connect(self._cancel)
    # setup the layout
    row = 0; col = 0;
    layout.addWidget(label_find, row, col)
    col += 1;
    layout.addWidget(self.lineedit_find, row, col)
    row += 1; col -= 1
    layout.addWidget(label_replace, row, col)
    col += 1
    layout.addWidget(self.lineedit_replace, row, col)
    row += 1; col -= 1;
    layout.addWidget(self.checkbox_dynamic_find, row, col, 1, 2)
    row += 1
    layout.addWidget(self.button_find, row, col)
    col += 1
    layout.addWidget(self.button_replace, row, col)
    row += 1; col -= 1
    layout.addWidget(button_cancel, row, col, 1, 2)
    self.setLayout(layout)
    self.setWindowTitle(self.tr("Find/Replace"))
    
  def keyPressEvent(self, kpe):
    if kpe.key() == Qt.Key.Key_Enter:
      self._emitFind()
    else:
      super(FindReplaceDialog, self).keyPressEvent(kpe)
    
  def _findEdited(self, text):
    if self.checkbox_dynamic_find.isChecked():
      self.find_text_changed.emit(text)
    else: pass
    
  def _emitFind(self):
    self.find_text_changed.emit(self.lineedit_find.text())
    
  def _dynamicFindChanged(self, state):
    print state
    if self.button_find.isEnabled():
      self.button_find.setEnabled(False)
    else: self.button_find.setEnabled(True)
    
  def _emitReplacement(self):
    # don't emit a replacement with empty fields
    if not self.lineedit_find.text() or not self.lineedit_replace.text():
      QApplication.beep()
    else:
      self.replace_committed.emit(self.lineedit_find.text(), self.lineedit_replace.text())
    
  def _cancel(self):
    self.find_cancelled.emit()
    self.hide()
    
  def closeEvent(self, ce):
    self._cancel()