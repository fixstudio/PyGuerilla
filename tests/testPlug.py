"""
Copyright (c) 2013 Digital District
----------------------------------------------------

Nose tests for Plug class

authors: sylvain delhomme <sylvain.delhomme@digital-district.ca>
"""

from pyGuerilla import Document, Node, Plug
from nose.tools import raises

class TestNode(object):

	@classmethod
	def setup_class(cls):
		Document().new(warn=False)

	def testCreation(self):

		n = Node.createNode('foo')
		n.createPlug('bar')
		p = Plug('bar', n)
		assert isinstance(p, Plug)

	@raises(Exception)
	def testDualCreation(self):
		
		n = Node.createNode('foo')
		n.createPlug('bar') 
		n.createPlug('bar') 
	
	def testProperty(self):
	
		plugName = 'bar'
		n = Node.createNode('foo')
		p = n.createPlug('bar')
		assert p.name == plugName
		assert p.parent.name == n.name
		
	def testIsType(self):

		assert not Node('RenderPass').RenderPassCamera.isTyped()
	
	def testConnection(self):

		n1 = Node.createNode('foo', 'SceneGraphNode')
		t1 = Node.createNode('xform', 'TransformEuler', n1)
		n1.Transform.connect(t1.Out)
		assert n1.Transform.isConnected()	
	
	def testGetConnections(self):

		n1 = Node.createNode('foo', 'SceneGraphNode')
		t1 = Node.createNode('xform', 'TransformEuler', n1)
		n1.Transform.connect(t1.Out)
		#assert n1.Transform.isConnected()

		tCo = t1.Out.connections(source=False, destination=True)
		assert tCo[0].name == n1.Transform.name

		nCo = n1.Transform.connections(source=True, destination=False)
		assert nCo[0].name == t1.Out.name

