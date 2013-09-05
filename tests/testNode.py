"""
Copyright (c) 2013 Digital District
----------------------------------------------------

Nose tests for Node class

authors: sylvain delhomme <sylvain.delhomme@digital-district.ca>
"""

from pyGuerilla import Document, Node, Camera, toLua
from nose.tools import raises

class TestNode(object):

	@classmethod
	def setup_class(cls):
		Document().new(warn=False)
	
	def testNew(self):

		assert isinstance(Node('RenderPass'), Node)
		assert isinstance(Node('Perspective'), Camera)
		# TODO: Reference

	def testProperty(self):

		nodeName1 = 'grp'
		nodeName2 = 'foo'
		nodeType = 'SceneGraphNode'
		n1 = Node.createNode(nodeName1, nodeType)
		n2 = Node.createNode(nodeName2, nodeType, n1)

		assert n1.name == nodeName1
		assert n1.longName == nodeName1
		assert n1.type == nodeType

		assert n2.name == nodeName2
		assert n2.longName == '%s|%s' % (nodeName1, nodeName2)
		assert n2.type == nodeType
	
	def testParent(self):
		
		n = Node.createNode('foo')
		# TODO use hash?
		assert toLua(n.parent) == toLua(Document())

	def testPlugs(self):

		# XXX weak test
		[p.name for p in Node('RenderPass').plugs()]

	def testChildren(self):

		# XXX weak test
		[c.name for c in Node('RenderPass').children()]
	
	@raises(AttributeError)
	def testUnknownPlug(self):
		Node('RenderPass').DummyDummyAttr

