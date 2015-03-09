import sys
import cPickle
from PyQt4 import QtGui, QtCore

class config(object):
    def __init__(self, mode):
        self.mode = mode
        
    def __repr__(self):
        return "%s" % (self.mode)

class modeclass(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(modeclass, self).__init__(parent)
        self.list = []
        for mode in (
        ("Source"),
        ("Destination"),
        ("Filter"),
        ("Log Paths")):
            self.list.append(config(mode))
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.list)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            config = self.list[index.row()]
            return QtCore.QVariant(config.mode)
        elif role == QtCore.Qt.UserRole: 
            config = self.list[index.row()]
            return config
        return QtCore.QVariant()

    def removeRow(self, position):
        self.list = self.list[:position] + self.list[position+1:]
        self.reset()

class drophere(QtGui.QLabel):
    def __init__(self, parent=None):
        super(drophere, self).__init__(parent)
        self.setMinimumSize(400,400)
        self.setText("Drop Here")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-config"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-config"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        bstream = data.retrieveData("application/x-config",
            QtCore.QVariant.ByteArray).toByteArray()
        stri=''
        i=96
        while(bstream[i]!="'"):
            stri=stri+bstream[i]
            i+=1
        self.setText(str(stri))
        event.accept()


class listdrag(QtGui.QListView):
    def ___init__(self, parent=None):
        super(listdrag, self).__init__(parent)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-config"):
            event.setDropAction(QtCore.Qt.QMoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        selected = self.model().data(index,QtCore.Qt.UserRole)
        bstream = cPickle.dumps(selected)
        mimeData = QtCore.QMimeData()
        
        
        mimeData.setData("application/x-config", bstream)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, self.rectForIndex(index))
        drag.setPixmap(pixmap)

        drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)
        result = drag.start(QtCore.Qt.MoveAction)
        if result:
            self.model().removeRow(index.row())

    def mouseMoveEvent(self, event):
        self.startDrag(event)
        
class testDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(testDialog, self).__init__(parent)
        self.setWindowTitle("Syslog-ng editor")
        layout = QtGui.QGridLayout(self)

        self.model = modeclass()
        self.list1 = listdrag()
        self.list1.setModel(self.model)
        self.dropbox = drophere()

        layout.addWidget(self.list1,1,0)
        layout.addWidget(self.dropbox,0,1,2,2)

if __name__ == '__main__':
    APP = QtGui.QApplication(sys.argv)
    ex = testDialog()
    ex.show()
    sys.exit(APP.exec_())
