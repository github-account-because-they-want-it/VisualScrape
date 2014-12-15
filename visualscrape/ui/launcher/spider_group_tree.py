'''
Created on Jul 23, 2014
@author: Mohammed Hamdy
'''

from PySide.QtGui import QTreeView, QPushButton, QDialog, QMessageBox, QWidget, \
   QGridLayout
from PySide.QtCore import QAbstractItemModel, QModelIndex, Qt
from dialogs import GroupNameDialog
from collections import defaultdict

class SpiderTreeItem(object):
  
  def __init__(self, nodeName="Spider Groups", spiderNames=[], parent=None):
    self._parent = parent
    self._node_name = nodeName
    self._spider_names = spiderNames
    
  def columnCount(self):
    return 1
    
  def child(self, index):
    if index < len(self._spider_names):
      return self._spider_names[index]
  
  def childCount(self):
    return len(self._spider_names)
  
  def appendChild(self, childItem):
    self._spider_names.append(childItem)
    
  def popChild(self, childIndex):
    self._spider_names.pop(childIndex)
    
  def removeChild(self, child):
    self._spider_names.remove(child)
  
  def insertChildren(self, pos, count, columns):
    if pos > len(self._spider_names) or pos < 0:
      return False
    new_tree_items = [SpiderTreeItem(nodeName="Enter spider name", parent=self) for _ in range(columns)]
    self._spider_names.extend(new_tree_items)
    return True
  
  def childNumber(self):
    if self._parent:
      return self.parent()._spider_names.index(self)
    return 0
    
  def data(self):
    return self._node_name
  
  def setData(self, data):
    self._node_name = data
    
  def parent(self):
    return self._parent
  
  def children(self):
    return self._spider_names
  
  def __unicode__(self):
    return "<SpiderTreeItem {} at {:0x}>".format(self._node_name, id(self))
  
class TreeGroupModel(QAbstractItemModel):
  
  def __init__(self, rootItem=None, parent=None):
    super(TreeGroupModel, self).__init__(parent)
    if not rootItem:
      self._root_item = SpiderTreeItem()
    else:
      self._root_item = rootItem
      
  def headerData(self, section, orientation, role):
    if role == Qt.DisplayRole:
      if orientation == Qt.Horizontal and section == 0:
        return self.tr("Groups")
      elif orientation == Qt.Vertical:
        return self.tr("Group #{}".format(section)) 
    
  def rowCount(self, parentIndex):
    item = self.getItemAt(parentIndex)
    return item.childCount()
  
  def columnCount(self, parentIndex):
    return self._root_item.columnCount()
  
  def data(self, index, role):
    if role == Qt.DisplayRole:
      item = self.getItemAt(index)
      return item.data()
    
  def setData(self, index, value, role):
    if role == Qt.EditRole:
      # I assume here that only spider group name rows are editable
      item = index.internalPointer()
      item.setData(value)
      self.dataChanged.emit(index, index)
      return True
  
  def index(self, row, column, parentIndex):
    # I think this method is here to pack data into different indexes
    if not self.hasIndex(row, column, parentIndex):
      return QModelIndex()
    # get the parent item from the index. 
    if not parentIndex.isValid(): 
      parent_item = self._root_item
    else:
      parent_item = parentIndex.internalPointer()
    child = parent_item.child(row)
    if child:
      return self.createIndex(row, column, child)
    else:
      return QModelIndex()
  
  def parent(self, index):
    # this method is the reverse of index(). It returns indexes to parents, not to children
    if not index.isValid():
      return QModelIndex()
    item = self.getItemAt(index)
    parent = item.parent()
    if parent is self._root_item:
      return QModelIndex()
    else:
      return self.createIndex(parent.childNumber(), 0, parent) 
  
  def addSpiderGroup(self, groupName="New launch group"):
    group_count = self._root_item.childCount()
    self.beginInsertRows(QModelIndex(), group_count - 1, group_count)
    new_group = SpiderTreeItem(groupName, [], parent=self._root_item)
    #new_group.appendChild(SpiderTreeItem("Drag and drop spider(s) here...", [], parent=new_group)) # used to crash before adding []
    self._root_item.appendChild(new_group)
    self.endInsertRows()
    
  def removeGroupsByIndexes(self, indexes):
    groups_indexes = [(index.internalPointer(), index.row()) for index in indexes]
    for group_tr, row in groups_indexes:
      self.beginRemoveRows(QModelIndex(), row, row)
      self._root_item.removeChild(group_tr)
      self.endRemoveRows()
      
  def removeSpidersByIndexes(self, indexes):
    # group spiders by their parent (group) and remove all spiders under same group in one operation
    spider_groups = defaultdict(list)
    for sp_index in indexes:
      spider_groups[sp_index.parent()].append(sp_index.row()) 
    for parent, spider_group in spider_groups.items():
      min_row = min(spider_group)
      max_row = max(spider_group)
      self.beginRemoveRows(parent, min_row, max_row)
      spiders_to_remove = [parent.internalPointer().child(child_row) for child_row in spider_group]
      [parent.internalPointer().removeChild(child) for child in spiders_to_remove]
      self.endRemoveRows()
      
  def flags(self, index):
    if index.isValid(): # not the root
      item = index.internalPointer()
      parent_item = item.parent()
      if parent_item is self._root_item: # only first-level rows (group names) are editable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsSelectable
      else:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    else:
      return 0
  
  def supportedDropActions(self):
    return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction
  
  def dropMimeData(self, mimeData, dropAction, row, column, parentIndex):
    if dropAction == Qt.IgnoreAction:
      return False
    if not parentIndex.isValid(): # guess I don't need this
      return False
    spider_name = mimeData.text()
    if not spider_name:
      return False
    parent = parentIndex.internalPointer()
    child_count = parent.childCount()
    self.beginInsertRows(parentIndex, child_count - 1, child_count)
    parent.appendChild(SpiderTreeItem(spider_name, [], parent=parent))
    self.endInsertRows()
    return True # does this emit dataChanged?. It seems not
  
  def getItemAt(self, index):
    if index.isValid():
      item = index.internalPointer()
      if item:
        return item
    else:
      return self._root_item
    
class SpiderGroupTreeView(QTreeView):
  
  def __init__(self, rootItem=None, parent=None): # the root item might be from disk
    super(SpiderGroupTreeView, self).__init__(parent)
    self.setModel(TreeGroupModel(rootItem))
    self.viewport().setAcceptDrops(True)
    self.setSelectionBehavior(self.SelectItems)
    self.setSelectionMode(self.ExtendedSelection)
    self.setDragDropMode(self.DropOnly)
    self.showDropIndicator()
    
  def dragEnterEvent(self, dee):
    mimedata = dee.mimeData()
    if mimedata.hasText():
      dee.accept()
      
    
      
class ButtonStates(object):
    NO_SELECTION = 1
    GROUPS_SELECTED = 2
    SPIDERS_SELECTED = 3    

class AddRemoveGroupTreeContainer(QWidget):
  """
  Tracks the selection model of the group tree to enable adding and removing spiders/groups.
  Adds a dynamic button and a layout to the group tree
  """
  
  def __init__(self, parent=None):
    super(AddRemoveGroupTreeContainer, self).__init__(parent)
    self._tree_spider_group = SpiderGroupTreeView()
    selection_model = self._tree_spider_group.selectionModel()
    selection_model.selectionChanged.connect(self._updateButtonText)
    self._button_add_remove = QPushButton(self.tr("Add launch group..."))
    self._button_add_remove.clicked.connect(self._updateTree)
    self._button_add_remove.setProperty("_state", ButtonStates.NO_SELECTION)
    layout = QGridLayout()
    layout.addWidget(self._tree_spider_group, 0, 0, 1, 2)
    layout.addWidget(self._button_add_remove, 1, 1)
    self.setLayout(layout)
    
  def _updateButtonText(self, selectedIndexes, deselectedIndexes):
    # this may not work because these are NEWLY selected and deselected. Strange. This only means mostly one index at a time
    if not selectedIndexes:
      self._button_add_remove.setEnabled(True)
      self._button_add_remove.setText(self.tr("Add launch group..."))
      self._button_add_remove.setProperty("_state", ButtonStates.NO_SELECTION)
    else:
      all_groups = all([not index.parent().isValid() for index in selectedIndexes])
      if all_groups:
        self._button_add_remove.setEnabled(True)
        self._button_add_remove.setText(self.tr("Delete groups..."))
        self._button_add_remove.setProperty("_state", ButtonStates.GROUPS_SELECTED)
        return
      all_spiders = all([index.parent().isValid() for index in selectedIndexes])
      if all_spiders:
        self._button_add_remove.setEnabled(True)
        self._button_add_remove.setText(self.tr("Delete spiders..."))
        self._button_add_remove.setProperty("_state", ButtonStates.SPIDERS_SELECTED)
        return
      # I assume now that we have a mixture of spiders and groups. That can be a user mistake and will disable the button
      self._button_add_remove.setEnabled(False)
  
  def _updateTree(self):
    current_state = self._button_add_remove.property("_state")
    selected_indexes = self._tree_spider_group.selectionModel().selectedIndexes()
    selected_texts = [selected_index.data(Qt.DisplayRole) for selected_index in selected_indexes]
    if current_state == ButtonStates.NO_SELECTION:
      # Add a new launch group. First collect current group names.
      group_name_dialog = GroupNameDialog(selected_texts)
      result = group_name_dialog.exec_()
      if result == QDialog.Accepted:
        new_group_name = group_name_dialog.groupName()
        self._tree_spider_group.model().addSpiderGroup(new_group_name)
    elif current_state == ButtonStates.GROUPS_SELECTED:
      accepted = self._askAreYouSure()
      if accepted:
        self._tree_spider_group.model().removeGroupsByIndexes(selected_indexes)
    elif current_state == ButtonStates.SPIDERS_SELECTED:
      accepted = self._askAreYouSure()
      if accepted:
        self._tree_spider_group.model().removeSpidersByIndexes(selected_indexes)
    
  def _askAreYouSure(self):
    dialog_sure = QMessageBox(self)
    dialog_sure.setWindowTitle(self.tr("Confirm"))
    dialog_sure.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    dialog_sure.setIcon(QMessageBox.Warning)
    dialog_sure.setText(self.tr("Are you sure"))
    result = dialog_sure.exec_()
    if result == QMessageBox.Ok:
      return True
    else:
      return False
