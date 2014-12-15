'''
Created on Jul 23, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QDialog, QLabel, QLineEdit, QPushButton, QGridLayout

class GroupNameDialog(QDialog):
  """
  Check exec state and if accepted call groupName() to access the result
  """
  def __init__(self, currentGroupNames=[], parent=None):
    super(GroupNameDialog, self).__init__(parent)
    self._current_groupnames = [groupname.lower() for groupname in currentGroupNames]
    self.setModal(True)
    self.setWindowTitle(self.tr("Group name"))
    label_prompt = QLabel(self.tr("Enter new launch group name:"))
    self._lineedit__groupname = QLineEdit()
    self._label_warning = QLabel()
    self._label_warning.setStyleSheet("""
      QLabel {
        color: rgb(213, 17, 27);
        font-weight: bold;
      }
    """)
    self._button_ok = QPushButton(self.tr("OK"))
    button_cancel = QPushButton(self.tr("Cancel"))
    self._button_ok.clicked.connect(self._checkGroupName)
    button_cancel.clicked.connect(self.reject)
    layout = QGridLayout()
    row = 0; col = 0;
    layout.addWidget(label_prompt, 0, 0, 1, 4)
    row += 1
    layout.addWidget(self._lineedit__groupname, row, col, 1, 4)
    row += 1; col += 2
    layout.addWidget(self._button_ok, row, col)
    col += 1
    layout.addWidget(button_cancel, row, col)
    self.setLayout(layout)
    
  def _checkGroupName(self):
    entered_name = self._lineedit__groupname.text().lower()
    if entered_name in self._current_groupnames:
      self._label_warning.setText("Group name already exists!")
    else:
      self._label_warning.clear()
      self.accept()
  
  def groupName(self):
    return self._lineedit__groupname.text()
