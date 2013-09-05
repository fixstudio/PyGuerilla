===========
Doctests
===========

== in Guerilla Console ==

import pyGuerilla
reload(pyGuerilla)
# print pyGuerilla.__file__

eg = {
	'dcAbcV1': 'PATH_TO_v002.abc', 
	'dcAbcV2': 'PATH_TO_v008.abc',
}
import doctest
doctest.testmod(pyGuerilla, verbose=False, extraglobs=eg)

===========
Nose
===========

== linux terminal ==

cd PATH_TO_MY_REPO/pyGuerilla
guerilla --nogui /usr/lib/python2.6/site-packages/nose/core.py

Limitations: no arguments...

== Guerilla Console ==

import nose
nose.run(argv=['--verbosity=3', 
	'--with-isolation', 
	'-w', 'PATH_TO_MY_REPO/pyGuerilla/tests'])

or (to see the output)

import nose
nose.run(argv=['--verbosity=6', '-s', 
	'--with-isolation', 
	'-w', 'PATH_TO_MY_REPO/pyGuerilla/tests'])

or (just one test named testCreateNodes in test_mod.py)

# nose
import nose; reload(nose)
nose.run(argv=[
	'--verbosity=3', 
	'-s', '--with-isolation', 
	'-w', 
	'PATH_TO_MY_REPO/pyGuerilla/tests', 
	'test_mod.py:TestModificationContext.testCreateNodes'])

== writing nose tests ==

Add a python script into 'tests' folder

Insert some code like:

def setup_module():
   	# run before any test modules within the package
	pass 

def teardown_module():
	# run after all of the modules are run
    pass

def test1():
	# will fail
	assert False

# class name and methods must start with Test/test for test discovery
class TestDummy(object):

	@classmethod
	def setup_class(cls):
		# only run once
		pass

	@classmethod
	def teardown_class(cls):
		# only run once
		pass

	def setup(self):
		# run multiple times, once for each test method
		pass

	def teardown(self):
		# run multiple times, once for each test method
		pass

	def test1(self):
		# ok
		assert True

	def test2(self):
		# will fail
		assert False

	# not a test
	def doSomething(self):
		pass
