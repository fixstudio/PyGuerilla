"""
Copyright (c) 2013 Digital District
----------------------------------------------------

Nose tests for ModificationContext class

authors: sylvain delhomme <sylvain.delhomme@digital-district.ca>
"""

import os

import lua
from pyGuerilla import ModificationContext, Document, Node, toLua, fromLua, Gtypes

from nose.tools import assert_raises, raises

class TestModificationContext(object):
	
	luaFunctions = [
			'createnode', 'createref',
			'select',
			'movenode', 'deletenode', 'renamenode',
			'createplug', 'deleteplug',
			'set', 'connect', 'disconnect',
			'adddependency', 'removedependency',
			'touch',
			]

	@classmethod
	def setup_class(cls):
		Document().new(warn=False)

	# test again http://www.guerillarender.com/redmine/issues/222
	def testInitFromStatic(self):
			
		mod = ModificationContext.get()
		missingFuncs = []
		for f in self.luaFunctions:
			if getattr(toLua(mod), f) == None:
				missingFuncs.append('ModificationContext.%s does not exist' % f)

		assert not missingFuncs, os.linesep.join(missingFuncs)

	def testInitFromWith(self):

		missingFuncs = []
		with ModificationContext() as mod:
			for f in self.luaFunctions:
				if getattr(toLua(mod), f) == None:
					missingFuncs.append('ModificationContext.%s does not exist' % f)
				
			assert not missingFuncs, os.linesep.join(missingFuncs)
	
	def testCreateUnknownNode(self):
		
		with ModificationContext() as mod:
			assert_raises(ValueError, mod.createNode, 'foo', 'dummyDummy')
	
	def testCreateNodes(self):
		
		lg = lua.globals()
		
		luaClasses = [ c for c in fromLua(lg.getclassesbypattern('.+')) if
				lg.classisclassof(c, 'Node') ]
		with ModificationContext() as mod:
			for lc in luaClasses:
				#print lc
				mod.createNode('foo', lc)	
	
	def testCreateRef(self):
		assert False

	def testMoveNode(self):

		with ModificationContext() as mod:
			g = mod.createNode('grp')
			n = mod.createNode('foo')
			
			assert not (n.parent.name == g.name)
			mod.moveNode(n, g)
			assert n.parent.name == g.name
	
	@raises(ValueError)
	def testDeleteNode(self):

		with ModificationContext() as mod:
			n = mod.createNode('foo')
			nodeName = n.name
			mod.deleteNode(n)
			# should raise
			Node(nodeName)

	def testRenameNode(self):
		
		newName = 'fii'
		with ModificationContext() as mod:
			n = mod.createNode('foo')
			mod.renameNode(n, newName)
			assert n.name == newName

	# createPlug, and select value (generic)
	def testPlug(self):

		with ModificationContext() as mod:
			n = mod.createNode('foo')

			for i, t in enumerate(Gtypes.validTypes):
			
				if t in Gtypes.descRequired:
					assert_raises(ValueError, Gtypes, t)
				else:
					gt = Gtypes(t)
					mod.createPlug(n, 'bar%d' % (i*2), dataType=gt)
					mod.createPlug(n, 'bar%d' % ((i*2)+1), dataType=t)
					
			mod.select([n])
	
	# createPlug, setPlug and select (generic)
	def testSetPlug(self):
		
		with ModificationContext() as mod:
			n = mod.createNode('foo')

			for i, t in enumerate(Gtypes.validTypes):	
				if t not in Gtypes.descRequired:
					gt = Gtypes(t)
					p1 = mod.createPlug(n, 'bar%d' % (i*2), dataType=gt)
					mod.setPlug(p1, gt.default)
					p1.get()
		
			mod.select([n])
	
	# create and set plug (enum)
	def testEnumPlug(self):
		
		with ModificationContext() as mod:
			n = mod.createNode('foo')
			p1 = mod.createPlug(n, 'bar1', 
					dataType=Gtypes('enum', desc=['a', 'b', 'c'])
					)
			p1.set('a')
			assert p1.get() == 'a'

			p2 = mod.createPlug(n, 'bar2', 
					dataType=Gtypes('enum', desc=['a', ['b', 12]])
					)
			p2.set('a')
			# XXX
			#assert p2.get() == 0
			p2.set('b')
			assert p2.get() == 12, 'plug value is %s, should be 12' % p2.get()

	def testDeletePlug(self):

		with ModificationContext() as mod:
			n = mod.createNode('foo')
			plugNames = set()
			for i, t in enumerate(Gtypes.validTypes):
				if t in Gtypes.descRequired:
					#TODO should test deleting enum plug
					assert_raises(ValueError, Gtypes, t)
				else:
					gt = Gtypes(t)
					p1 = mod.createPlug(n, 'bar%d' % (i*2), dataType=gt)
					plugNames.add(p1.name)

					mod.deletePlug(p1)
			
			nodePlugNames = [ p.name for p in n.plugs() ]
			for pn in plugNames:
				#TODO: print node type
				assert pn not in nodePlugNames, 'plug %s still in node %s' % (pn,
						n.name)
	
	#def testDependency(self): 
		#pass

	#def touch(self):
		#pass
	

