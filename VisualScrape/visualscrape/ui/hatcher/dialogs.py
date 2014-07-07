'''
Created on Jul 5, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import (QWizard, QWizardPage, QDialog, QLabel, QGridLayout,
      QPushButton, QRadioButton, QVBoxLayout,
  QHBoxLayout)
from ui_common import SingleEditCombobox

class NewActionWizard(QWizard):
  pass


class ScrapeAttributeDialog(QDialog):
  
  def __init__(self, attributeDict, existingFields, parent=None):
    super(ScrapeAttributeDialog, self).__init__(parent)
    self._choice_dict = {"field_name":'', "attr_name":'', "attr_value":''}
    self._rdbtn_label_map = {}
    self._field_names = existingFields
    layout = QGridLayout()
    for index, (attr_name, attr_value) in attributeDict:
      rdbtn_attr_name = QRadioButton(attr_name)
      label_attr_value = QLabel(attr_value)
      label_attr_value.setMaximumWidth(120)
      layout.addWidget(rdbtn_attr_name, index, 0)
      layout.addWidget(label_attr_value, index, 1, 1, 2)
      self._rdbtn_label_map[rdbtn_attr_name] = label_attr_value
    label_output_field = QLabel(self.tr("Output Field"))
    self.combo_output_field = SingleEditCombobox(existingFields)
    self._button_ok = QPushButton(self.tr("OK"))
    self._button_ok.clicked.connect(self._collectChoices)
    self._button_cancel = QPushButton(self.tr("Cancel"))
    self._button_cancel.clicked.connect(self.reject)
    index += 1
    layout.addWidget(label_output_field, index, 0)
    layout.addWidget(self.combo_output_field, index, 1, 1, 2)
    index += 1
    layout.addWidget(self._button_ok, index, 1)
    layout.addWidget(self._button_cancel, index, 2)
    self.setLayout(layout)
    self.setWindowTitle(self.tr("Choose Attributes"))
    
  def getChoices(self):
    return self._choice_dict
  
  def _collectChoices(self):
    self._choice_dict["fieldname"] = self.combo_output_field.currentText()
    for (rdbtn, label) in self._rdbtn_label_map:
      if rdbtn.isChecked():
        self._choice_dict["attr_name"] = rdbtn.text()
        self._choice_dict["attr_value"] = label.text()
        break
    self.accept()
    
    
class FieldNameDialog(QDialog):
  def __init__(self, currentFields, parent=None):
    super(FieldNameDialog, self).__init__(parent)
    label_choice = QLabel(self.tr("Choose output field name:"))
    self._chosen_field = None
    self.combobox_field_choice = SingleEditCombobox(currentFields)
    btn_ok = QPushButton(self.tr("OK"))
    btn_ok.clicked.connect(self.accepted)
    btn_cancel = QPushButton(self.tr("Cancel"))
    btn_cancel.clicked.connect(self.rejected)
    layout = QVBoxLayout()
    bottom_layout = QHBoxLayout()
    layout.addWidget(label_choice)
    layout.addWidget(self.combobox_field_choice)
    bottom_layout.addStretch()
    bottom_layout.addWidget(btn_ok)
    bottom_layout.addWidget(btn_cancel)
    layout.addLayout(bottom_layout)
    self.setLayout(layout)
    self.setWindowTitle(self.tr("Choose output field"))
    
  def accept(self):
    self._chosen_field = self.combobox_field_choice.currentText()
    
  def getField(self):
    return self._chosen_field