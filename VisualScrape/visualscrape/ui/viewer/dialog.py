'''
Created on Jun 18, 2014
@author: Mohammed Hamdy
'''
from PySide.QtGui import QDialog, QFileDialog, QGridLayout, QLabel, QPushButton, QComboBox,\
  QStringListModel, QMessageBox
from visualscrape.lib.export import FileExporter
import os

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
    self.setWindowTitle("Export Parameters")
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
    
  def _result(self):
    if self.clickedButton() == self.button_overwrite:
      return self.OVERWRITE
    else: return self.CANCEL
    
  ret = property(_result)
  
class FindReplaceDialog(QDialog):
  
  def __init__(self, parent=None):
    pass