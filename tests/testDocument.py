"""
Copyright (c) 2013 Digital District
----------------------------------------------------

Nose tests for Document class

authors: sylvain delhomme <sylvain.delhomme@digital-district.ca>
"""

import tempfile
import os
import shutil
from pyGuerilla import Document, Node
from nose.tools import raises

class TestDocument(object):

	folders = []

	@classmethod
	def setup_class(cls):
		Document().new(warn=False)

	@classmethod
	def teardown_class(cls):

		for f in cls.folders:
			shutil.rmtree(f)

	def testGetPreferences(self):
		assert isinstance(Document().Preferences, Node)

	def testPreferences(self):
		Document().Preferences.CommandPort.set(1777)

	@raises(AttributeError)
	def testUnknownAttr(self):
		Document().DummyDummyAttr
	
	def testSaveAndFilename(self):
		
		scenePath = self.getTmpScenePath()
		doc = Document()
		doc.save(scenePath)
		assert doc.filename == scenePath

	def testLoadFilename(self):

		scenePath = self.getTmpScenePath()
		doc = Document()
		doc.save(scenePath)
		doc.new(warn=False)
		doc.load(scenePath, warn=False)
		assert doc.filename == scenePath
	
	# NOT TESTS

	def getTmpScenePath(self):
		
		'''
		self way to get scene path in temp folder
		Scene and folder will be deleted after all test are run 
		'''

		sceneFolder = os.path.join(tempfile.gettempdir(), 
				tempfile.mkdtemp())
		self.folders.append(sceneFolder)
		return os.path.join(sceneFolder, 'blast.gproject')
	
