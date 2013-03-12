__author__ = 'thornag'

from PyQt4 import QtGui

def forest(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#36ab00')
    roomView.color = color

def mountains(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#8b580c')
    roomView.color = color

def path(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#ffaa00')
    roomView.color = color

def cave(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#aaffff')
    roomView.color = color

def water(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#0000ff')
    roomView.color = color

def fields(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#ead441')
    roomView.color = color

def poi(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#ff0000')
    roomView.color = color

def city(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#6e6097')
    roomView.color = color

def danger(roomView):
    color = QtGui.QColor()
    color.setNamedColor('#ff0000')
    roomView.color = color