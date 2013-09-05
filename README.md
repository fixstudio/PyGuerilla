PyGuerilla
==========

Python Module abstracting Guerilla Renderer Lua API

PyGuerilla provides a more pythonic and smooth python experience than Guerilla python API (lunatic). 
It also tries to workaround bugs or features not implemented in 
like for instance iterators.

PyGuerilla has a suite of unit tests (doctest && nose).

PyGuerilla is currently in use on two projects at Digital District Montreal 
(http://www.digital-district.fr/ddca) including a major animation feature film. 

Typical usage often looks like this:

    from pyGuerilla import ModificationContext, Document, Node
	
	# Document children
    doc = Document()
    for c in doc.children('Node'):
        print c.name, c.type

    # create a node in a modification context (undo & redo)
    with ModificationContext() as mod:
        n1 = mod.createNode( 'foo', 'SceneGraphNode' )
        print [ p.name for p in n1.plugs ]

        plug = mod.createPlug( n1, 'bar1' )
        print plug.name

        plug2 = mod.createPlug( n1, 'bar2', valueType = 'int' )
        print plug2.name
        mod.set( plug2, 5 ) # or plug2.set(5)

Install
========

Requirements
-------------

Guerilla >= 0.17.0b27
Nose (optional)
Doxygen + doxypy (optional)

Install from source:
-------------

- Clone this repository
- Modify your PYTHONPATH in Guerilla

Doc
========

- edit pydoc.dox and modify INPUT_FILTER to match your config
- doxygen pydoc.dox

Testsuite
========

- see DEV.txt
