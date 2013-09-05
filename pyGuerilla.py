"""

@mainpage pyGuerilla SDK

@section Copyright
@code
Copyright (c) 2013, Digital District
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

  Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

  Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
@endcode

@brief Object oriented python wrapper for Guerilla Render (http://www.guerillarender.com)

@details

PyGuerilla provides a more pythonic and smooth python experience than Guerilla python API (lunatic). 
It also tries to workaround bugs or features not implemented in 
like for instance iterators.

PyGuerilla has a suite of unit tests (doctest && nose), see @link dev.txt @endlink.

PyGuerilla is currently in use on two projects at Digital District Montreal 
(http://www.digital-district.fr/ddca) including a major animation feature film. 

Contributing:

The project hosts its issues on Github.

- Sign up for a Github account
- Check out the Github Guides for instructions on how to setup git for your OS
- Make a fork of the main pyGuerilla repository, and start hacking

Examples:

    1- guerilla python (lunatic)

@code
# modification context setup 
g = lua.globals()
doc = g.Document
mod = doc.modify(doc)
# create SceneGraphNode
n = mod.createnode(doc, "SceneGraphNode", "grp")
# create euler transform
t = mod.createnode(n, "TransformEuler", "euler")
# connect nodes
mod.connect(n.Transform, t.Out)
# setup y translation
mod.set(t.TY, 2.0)
# check TY value
print 'euler y translation value', t.TY.get(t.TY)
# NO BONUS --> need to reimplement plugs iterator :(
mod.finish()
@endcode

    2- PyGuerilla

@code
from pyGuerilla import ModificationContext, Node
with ModificationContext() as mod:
    # create SceneGraphNode
    n = Node.createNode('grp', 'SceneGraphNode')
    # attach a Euler transform parented under n
    t = Node.createNode('euler', 'TransformEuler', n)
    # connect nodes
    n.Transform.connect(t.Out)
    # setup y translation
    t.TY.set(2.0)
    # check TY value
    print 'euler y translation value', t.TY.get(t.TY)
    # BONUS --> print all plug names on our transform node
    print [ p.name for p in t.plugs() ]
@endcode

@pre Guerilla >= 0.17.0b27
@author sylvain delhomme <sydhds _@__ gmail __DOT_ com>
"""

import os
import re
import lua

def toLua( obj ):

    '''
    Convert python 'object/value' to lua 'object/value'
    Lunatic can handle anything but python list, tuple, dict or object

    @code
    conversion process ->
    
    userdata:
    * __toLua__
    ** iteritems
    *** iter
    other:
    * N/A

    @endcode

    Examples:

    @code
    >>> toLua(16)
    16
    >>> toLua(3.71)
    3.71
    >>> toLua('bou')
    'bou'
    >>> toLua(Point3(1,2,3))
    {1,2,3}
    >>> t = toLua([1, 2, 5]); print t, t[1], t[2], t[3] # doctest: +ELLIPSIS
    <Lua table at ...> 1 2 5
    >>> t = toLua((1, 7, -5)); print t, t[1], t[2], t[3] # doctest: +ELLIPSIS
    <Lua table at ...> 1 7 -5
    >>> t = toLua({'a': 1, 'b': 7}); print t, t['a'], t['b'] # doctest: +ELLIPSIS
    <Lua table at ...> 1 7
    >>> t = toLua([Point3(1,2,3), Point3(4,5,6)])
    >>> print t, t[1][1], t[1][2], t[1][3], t[2][1], t[2][2], t[2][3] # doctest: +ELLIPSIS 
    <Lua table at ...> 1 2 3 4 5 6
    >>> t = toLua([[Point3(1,2,3)]]); print t, t[1][1][3] # doctest: +ELLIPSIS
    <Lua table at ...> 3
    >>> toLua(lua.globals().types.color.DefaultValue) # doctest: +ELLIPSIS
    <Lua table at ...>

    @endcode
    '''

    lg = lua.globals()
    luaType = lg.type( obj )

    if luaType == 'userdata':

        try:
            return obj.__toLua__()
        except:
            pass

        luaTbl = lua.eval( '{}' )
        try:
            for k, v in obj.iteritems():
                luaTbl[k] = toLua( v )
            return luaTbl
        except:
            pass

        luaTbl = lua.eval( '{}' )
        try:
            for i, v in enumerate( obj ):
                luaTbl[i + 1] = toLua( v )
            return luaTbl
        except:
            # raise an error?
            pass

    else:
        # number, nil, lua table
        # handled by lunatic
        return obj

def fromLua( obj ):

    '''
    Convert lua 'object/value' to python 'object/value'

    @code
    conversion process ->
    * lua class
    **__fromLua__
    * lua table
    ** len == 0
    *** to python dict
    ** len > 0
    ** to python list
    @endcode

    @note
    an empty lua table return an empty python dict

    @todo
    - userdata?

    Examples:

    @code
    >>> fromLua(16)
    16

    >>> fromLua(3.71)
    3.71

    >>> fromLua('bou')
    'bou'

    >>> fromLua(lua.eval('{}'))
    {}

    >>> fromLua(lua.eval('{a=1, b=2}')) == {'a': 1, 'b': 2}
    True

    >>> sorted(fromLua(lua.eval('{1, 2}')))
    [1L, 2L]

    >>> fromLua(lua.globals().point3.create(1, 2, 3)) # doctest: +ELLIPSIS
    <pyGuerilla.Point3 object at ...>

    >>> fromLua(lua.globals().Document) # doctest: +ELLIPSIS
    <pyGuerilla.Document object at ...>

    >>> fromLua(lua.globals()._('RenderPass')) # doctest: +ELLIPSIS
    <pyGuerilla.Node object at ...>

    >>> fromLua(lua.globals()._('RenderPass.RenderPassCamera')) # doctest: +ELLIPSIS
    <pyGuerilla.Plug object at ...>

    >>> fromLua(lua.eval('_"RenderPass"')) # doctest: +ELLIPSIS
    <pyGuerilla.Node object at ...>

    >>> fromLua(lua.eval('{_"RenderPass"}')) # doctest: +ELLIPSIS
    [<pyGuerilla.Node object at ...>]

    >>> print fromLua(Point3(1, 2, 3)); print Point3(1, 2, 3) # doctest: +ELLIPSIS
    <pyGuerilla.Point3 object at ...>

    @endcode
    '''

    # FIXME: Document should derived from Node
    orderedClassKeys = [ 'Document', 'Node', 'Plug', 'point3' ]
    classMap = {
            'Document': Document,
            'Node': Node,
            'Plug': Plug,
            'point3': Point3,
            }

    lg = lua.globals()
    luaType = lg.type( obj )

    className = None
    try:
        className = lg.getclassname( obj )
    except Exception:
        pass

    if className:
        for c in orderedClassKeys:
            if lg.classisclassof( className, c ):
                return classMap[c].__fromLua__( obj )

        raise RuntimeError( 'Unable to find base class for %s' % className )
    else:
        if luaType == 'table':

            # XXX fromLua for keys too?
            # tips: len is always 0 for a dict (in lua)
            if len( obj ) == 0:
                return dict( ( k, fromLua( obj[k] ) ) for k in obj )
            else:
                # lua table starts at index 1 not 0
                return [fromLua( obj[i + 1] ) for i in xrange( len( obj ) )]
        else:
            # number, nil
            # handled by lunatic
            return obj


class ModificationContext( object ):

    '''
    Modification context
    Use it as a context manager (using the 'with' keyword) or
    retrieve the current modification context using static method 'get'

    Examples:

    @code
    with ModificationContext() as m:
        pass
    @endcode

    @code
    # retrieve current modification context
    m = ModificationContext.get()
    @endcode
    '''

    def __init__( self ):

        '''
        Modification context constructor
        '''

        self._luaGlobals = lua.globals()
        # Document instance
        self.doc = Document( self._luaGlobals )

    def __enter__( self ):

        '''
        Enter the runtime context

        Required to support 'with' statement.
        '''

        luaDoc = self.doc._doc
        self._mod = luaDoc.modify( luaDoc )
        return self

    def __exit__( self, type, value, traceback ):

        '''
        Exit the runtime context

        Required to support 'with' statement
        '''

        self._mod.finish()

    def __toLua__( self ):
        '''
        Python -> lua object
        
        @return (lua modifier)
        '''
        return self._mod

    def fromLua( self ):
        '''
        Lua to python object

        @return (ModificationContext)
        '''
        return ModificationContext.get()

    def createNode( self, name, type = 'SceneGraphNode', parent = None ):

        '''
        Create a node

        @param name (str)
        node name
        @param type (str): 
        node type (ex: Camera), default -> SceneGraphNode
        @param parent (Node)
        parent node (default: current Document)
        @return (Node)
        created node

        @todo
        error if trying to create a ArchReference, SystemCamera
        '''

        if parent is None:
            luaParent = self.doc._doc
        else:
            luaParent = parent._node

        if self._luaGlobals.isclass( type ) == False:
            raise ValueError( 'not a valid node type: %s' % type )

        luaNode = self._mod.createnode( luaParent, type, name )
        return Node( str( luaNode ) )

    def createRef( self, name, path, parent = None ):

        '''
        Create a reference

        @param name (str)
        ref name
        @param path (str) 
        ref path
        @param parent (Node)
        parent node (default: current Document)
        @return (tuple)
        reference node (Node) and parent nodes (tuple - SceneGraphNode)

        @todo
        http://www.guerillarender.com/redmine/issues/230
        '''

        ref, roots = self._mod.createref( name, path, parent._node if parent else None )
        return ( fromLua( ref ), fromLua( roots ) )

    def moveNode( self, node, newParentNode ):

        '''
        Move node under newParentNode
        
        @param node (Node)
        node to move
        @param newParentNode (Node)
        new parent node
        @return (bool) 
        True on success else False
        '''

        return self._mod.movenode( node._node, newParentNode._node )

    def deleteNode( self, node ):

        '''
        Delete a node

        @param node (Node)
        node to delete
        
        @todo
        return issue --> http://www.guerillarender.com/redmine/issues/218
        '''

        self._mod.deletenode( node._node )

    def renameNode( self, node, newName ):

        '''
        rename a Node

        @param node (Node)
        node to rename
        @param newName (str)
        node new name

        @todo
        return issue --> http://www.guerillarender.com/redmine/issues/241
        '''

        self._mod.renamenode( node._node, newName )

    # ##
    # plug functions
    # ##

    def createPlug( self, node, name,
            plugType = 'user', dataType = 'string', flags = 0 ):

        '''
        Create a plug 

        @param node (Node)
        create plug for node
        @param name (str)
        name of plug
        @param plugType (str)
        user (default) or hidden
        @param dataType (str)
        type of value for new plug: 
        - int, float, bool, angle, 
        - string
        - color, 
        - enum, filename, directory
        @param flags (int - Plug.flags)
        Plug flag, ex: Plug.NoSerial, 0 (default)
        @return (Plug)
        created plug instance
        
        @throws (AttributeError)
        raise an exception if plug already exists
        
        @code
        >>> n = Node.createNode('foo'); n.createPlug('bar', dataType='angle') # doctest: +ELLIPSIS
        <pyGuerilla.Plug object at ...>
        
        >>> n = Node.createNode('foo'); p = n.createPlug('bar', dataType='color')
        >>> p.set([0,255,255]); print p.get()
        [0L, 255L, 255L]

        >>> n = Node.createNode('foo') 
        >>> p = n.createPlug('bar', dataType=Gtypes('enum', desc=['a', 'b']))
        >>> p.set('a'); print p.get()
        a

        @endcode
        '''

        luaPlugType = 'DynAttrPlug'
        if plugType == 'hidden':
            luaPlugType = 'Plug'

        gtype = Gtypes( dataType ) if isinstance( dataType, Gtypes ) == False else dataType

        hasplug = node.hasPlug( name )

        if not hasplug:
            self._mod.createplug( luaPlugType,
                    node._node,
                    name,
                    flags,
                    toLua( gtype ),
                    toLua( gtype.value ) if gtype.value is not None else gtype.default )
        else:
            raise AttributeError( '%s plug already exists' % name )

        return Plug( name, node )

    def deletePlug( self, plug ):

        '''
        Delete a plug

        @param plug (Plug)
        plug object to delete
        '''

        self._mod.deleteplug( plug._plug )

    def setPlug( self, plug, value ):

        '''
        Set a plug value

        @param plug: plug object
        @param value: new plug value
        '''

        self._mod.set( plug._plug, toLua( value ) )

    def connect( self, inputPlug, outputPlug ):

        '''
        Connect a plug to another

        @param inputPlug (Plug) 
        input plug
        @param outputPlug (Plug) 
        output plug
        '''

        if not inputPlug.isTyped():
            raise RuntimeError( 'Plug is not typed: use addDependency instead' )

        self._mod.connect( inputPlug._plug, outputPlug._plug )

    def disconnect( self, inputPlug, outputPlug ):

        '''
        Disconnect a plug from another plug

        @param inputPlug (Plug)
        input plug to be disconnected
        @param outputPlug (Plug)
        output plug to be disconnected
        '''

        self._mod.disconnect( inputPlug._plug, outputPlug._plug )

    def addDependency( self, inputPlug, outputPlug ):

        '''
        Add dependency of an output plug on an input plug 

        @param inputPlug (Plug) 
        input plug
        @param outputPlug (Plug) 
        output plug        
        '''

        self._mod.adddependency( inputPlug._plug, outputPlug._plug )

    def removeDependency( self, inputPlug, outputPlug = None ):

        '''
        Removes dependency of an output plug off an input plug 
        or all dependencies if outputPlug is None

        @param inputPlug (Plug) 
        input plug
        @param outputPlug (Plug) 
        output plug. If None, remove all dependencies
        '''

        if outputPlug is None:
            self._mod.removealldependencies( inputPlug._plug )
        else:
            self._mod.removedependency( inputPlug._plug, outputPlug._plug )

    def touch( self, plug ):

        '''
        Invalidate a plug value (ie. force re-evaluation)

        @param plug (Plug)
        plug to invalidate
        '''

        self._mod.touch( plug._plug )

    def select( self, nodes, mode = 'add' ):

        '''
        Select nodes

        @param nodes (list - Node)
        nodes to select
        @param mode (str)
        selection mode: replace, remove, add (default)

        @throws (RuntimeError)
        raise the exception if user creates a new document
        and retrieve the current (dummy) modification context

        @todo
        http://www.guerillarender.com/redmine/issues/222
        '''

        # cf todo
        if self._mod.select is None:
            raise RuntimeError( 'Could not access select method, create a modification context first...' )
        else:
            self._mod.select( toLua( nodes ), mode )

    @staticmethod
    def get():

        '''
        Retrieve current modification context

        @return (ModificationContext)
        current modification context; a dummy context is returned if required
        '''

        mc = ModificationContext()
        luaDoc = mc.doc._doc
        mc._mod = luaDoc.getmodifier( luaDoc )
        return mc


class Document( object ):

    '''
    Base object that represents the current Guerilla Scene

    Examples:

    @code
    doc = Document()
    print doc.filename
    @endcode
    '''

    # FIXME: wait for a better solution from Guerilla devs
    VALID_PLUGS = ['Time', 'FirstFrame', 'LastFrame', 'ProjectWidth', 'ProjectHeight', 'ProjectFrameRatio']
    VALID_CHILDREN = ['Preferences']

    def __init__( self, luaGlobals = None ):

        '''
        Document constructor
        '''

        if luaGlobals:
            self._luaGlobals = luaGlobals
        else:
            self._luaGlobals = lua.globals()

        self._doc = self._luaGlobals.Document

    def __getattr__( self, value ):

        '''
        Get plug or Preferences Node

        @return (Plug or Node)
        Preferences node or plug
        '''

        if value in Document.VALID_PLUGS:
            return Plug( value, self )
        elif value in Document.VALID_CHILDREN:
            if value == 'Preferences':
                luaPrefNode = self._luaGlobals.getpreferences()
                return Node( luaPrefNode.getname( luaPrefNode ) )
        else:
            raise AttributeError( 'unknown plug %s (valid plugs: %s)' % ( value, Document.VALID_CHILDREN ) )

    def __toLua__( self ):
        '''
        Python -> lua object

        @return (lua Document)
        '''
        return self._doc

    @classmethod
    def __fromLua__( cls, ldoc ):

        '''
        Lua to python object

        @return (Document)
        '''

        return cls()

    # def plugs(self):

        # '''
        # Iterator over all plugs

        # @return (iterator)
        # iterator of Plug objects
        # '''

        # #refusedKeys = list(self._luaGlobals.nodesRefusedKey)
        # for i in self._doc:
            # attr = getattr(self._doc, i)
            # if self._luaGlobals.isclassof(attr, 'Plug'):
                # yield Plug(i, self)

    def children( self, type = 'Node' ):
        '''
        Iterator over all child node

        @param type (str) 
        only return node with given type, ex. SceneGraphNode, Texture...
        @return (iterator)
        iterator of Nodes
        '''

        # TODO: recursive
        for i in self._doc.Children:
            obj = getattr( self._doc.Children, str( i ) )
            if self._luaGlobals.isclassof( obj, type ):
                yield Node( str( obj.getpath( obj )[0] ) )

    @staticmethod
    def new( warn = True, nodefault = False ):
        '''
        Create an empty new document

        @param warn (bool)
        if True, warn the user
        @param nodefault (bool)
        if True, add default objects such as default cameras
        '''

        # FIXME: use lua globals in self?
        luaGlobals = lua.globals()
        luaGlobals.newdocument( warn, nodefault )

    @property
    def filename( self ):

        '''
        retrieve current scene name

        @return (str)
        scene name or an empty string if file has never been saved
        '''

        scene = self._doc.getfilename( self._doc )
        if scene is None:
            return ''
        else:
            return str( scene )

    def save( self, filename = None, warn = False, addToRecent = True ):

        '''
        Save scene

        @param filename (str)
        if None, save over current file
        @param warn (bool)
        if True, warn the user when overwriting an existing project file
        @param addToRecent (bool)
        if True, add to recent files
        '''

        if filename is None:
            self._luaGloblas.savedocument( None, warn, not addToRecent )
        else:
            self._luaGlobals.savedocumentas( filename, warn, not addToRecent )

    def load( self, filename, warn = True ):

        '''
        Load a guerilla project file (.gproject)

        @param filename (str)
        file to load
        @param warn (bool)
        warn user to save current modified project before loading a new one
        @return (bool)
        True if the file was loaded
        '''

        return self._luaGlobals.loaddocument( filename, warn )

    def loadFile( self, filename ):

        '''
        load glocator or gnode file

        @param filename (str)
        file to load
        @return (list - Node)
        list of Node instances

        @code
        doc = Document()
        nodes = doc.loadFile('$(LIBRARY)/primitives/sphere.glocator')
        print 'created nodes:', [ n.name for n in nodes ]
        @endcode
        '''
        result = self._doc.loadfile( self._doc, filename )
        # FIXME: check result
        resultNodes = []
        for r in result:
            luaNode = result[r]
            resultNodes.append( Node( str( luaNode.getname( luaNode ) ) ) )

        return resultNodes


class Node( object ):

    '''
    Base class for all nodes in Guerilla

    Examples:

    @code
    try:
        n = Node('grp')
    except ValueError:
        print 'node grp does not exist'
    else:
        print 'node name:', n.name
    @endcode    
    '''

    def __new__( cls, *args, **kwargs ):

        '''
        Create class according to lua node type 
        '''

        lg = lua.globals()
        if args:
            name = args[0]
            ln = lg._( name )

            # XXX improve this
            if lg.isclassof( ln, 'Camera' ):
                classType = Camera
            elif lg.isclassof( ln, 'ReferenceBase' ):

                # Guerilla sdk fix -->
                # Reference hierarchy in Guerilla
                # * Node
                # ** ReferenceBase
                # *** DocRef
                # **** Reference
                # ***** HostReference
                # **** ArchReference

                classType = Reference
            else:
                classType = Node
        else:
            raise RuntimeError( 'Please provide a name' )

        self = super( Node, cls ).__new__( classType )
        return self

    def __init__( self, name, luaGlobals = None ):

        '''
        Create an instance of Node
        Raise a ValueError if Node does not exist
        '''

        self._name = name

        if luaGlobals:
            self._luaGlobals = luaGlobals
        else:
            self._luaGlobals = lua.globals()

        self._node = self._luaGlobals._( name )

        if self._node is None:
            raise ValueError( 'node %s does not exist' % name )

    def __str__( self ):

        '''
        Object representation    

        @return (str)
        implemented to return only object name
        @note 
        ensure compatibility with code that works in Maya and Guerilla
        '''

        return self.name

    def __toLua__( self ):
        return self._node

    @classmethod
    def __fromLua__( cls, lnode ):
        return cls( str( lnode.getpath( lnode )[0] ) )

    @property
    def name( self ):

        '''
        Node name

        @return (str) 
        node short name
        '''

        return str( self._node.getname( self._node ) )

    @property
    def longName( self ):

        '''
        Node long name

        @return (str)
        node long name 
        '''

        return str( self._node.getpath( self._node )[0] )

    @property
    def type( self ):

        '''
        Node type

        @return (str)
        node type 
        '''

        return str( self._luaGlobals.getclassname( self._node ) )

    @property
    def parent( self ):

        '''
        Parent of this node 

        @return (Node or Document)
        parent Node or Document
        '''

        luaNode = self._node.getparent( self._node )

        if self._luaGlobals.isclassof( luaNode, 'Document' ):
            return Document()
        else:
            return Node( luaNode.getpath( luaNode )[0] )

    def hasAttr( self, name, type ):

        '''
        Check whether a child node or plug of given type exists

        @param name (str)
        child node or plug name
        @param type (str)
        'Plug' or 'Node'
        '''

        attr = None

        if self._luaGlobals.classisclassof( type, 'Node' ):
            # Children attribute is not created until node gets children
            if self._node.Children is not None:
                attr = getattr( self._node.Children, name )
        else:
            attr = getattr( self._node, name )

        if attr is not None and self._luaGlobals.isclassof( attr, type ):
            return True
        else:
            return False

    def hasPlug( self, name ):

        '''
        Check whether a plug exists or not

        @param name (str)
        plug name
        @return (bool)
        True if plug exists else False
        '''

        return self.hasAttr( name, 'Plug' )

    def hasChild( self, name ):

        '''
        Check whether a child exists or not

        @param name (str)
        child name
        @return (bool)
        True if child exists else False
        '''

        return self.hasAttr( name, 'Node' )

    def plugs( self ):

        '''
        Iterator over all plugs in Node

        @return (iterator) 
        iterator of Plug objects
        '''

        refusedKeys = list( self._luaGlobals.nodesRefusedKey )
        for i in self._node:
            if isinstance( i, str ):
                attr = getattr( self._node, i )
                if i not in refusedKeys and self._luaGlobals.isclassof( attr, 'Plug' ):
                    yield Plug( i, self )

    # def children(self, type='Node', recursive=False):
        # '''
        # iterator over all plugs in Node

        # @param type: only return node with given type, ex. SceneGraphNode, Texture...
        # @param recursive: recursive lookup
        # @return list of Node objects
        # '''

        # nodes = [self._node.Children]
        # while nodes:
            # n = nodes.pop()
            # if n:
                # for i in n:
                    # obj = getattr(self._node.Children, str(i))
                    # if self._luaGlobals.isclassof(obj, type):
                        # yield Node('%s|%s' % (self.name, str(i)))
                    # if recursive and self._luaGlobals.isclassof(obj, 'Node'):
                        # nodes.append(obj)

    def children( self, type = 'Node' ):
        '''
        Iterator over all child node

        @param type (str)
        only return node with given type, ex. SceneGraphNode, Texture...
        @return (iterator)
        iterator of Node objects
        '''

        # XXX remove?
        if self._node.Children is None:
            raise StopIteration

        for i in self._node.Children:
            obj = getattr( self._node.Children, str( i ) )
            if self._luaGlobals.isclassof( obj, type ):
                yield Node( str( obj.getpath( obj )[0] ) )

    def __getattr__( self, value ):

        '''
        Get children or plug
        '''

        if self.hasPlug( value ):
            # self.hasPlug(value)
            return Plug( value, self )
        elif self.hasChild( value ):
            return Node( '%s|%s' % ( self.longName, str( value ) ) )
        else:
            raise AttributeError( "unknown node or plug '%s'" % value )

    def createPlug( self, name, plugType = 'user', dataType = 'string' ):

        '''
        Create a Plug on node
        Use current modification context if available
        see. createPlug function in ModificationContext class
        '''

        mc = ModificationContext.get()
        return mc.createPlug( self, name, plugType, dataType )

    @classmethod
    def createRef( cls, name, path, parent = None ):

        '''
        Create a Reference
        Use current modification context if available
        see. createRef function in ModificationContext class
        '''

        mc = ModificationContext.get()
        return mc.createRef( name, path, parent )

    # @staticmethod
    # def createRef(name, path, parent):

        # '''
        # Create a ArchReference node under parent (not undoable)

        # @note
        # deprecated - do not use this function
        # @todo
        # remove it
        # '''

        # # TODO: parent=None?
        # lg = lua.globals()
        # luaRefNode = lg.ArchReference(parent._node, name, path)
        # return Node(str(luaRefNode))

    @staticmethod
    def createNode( name, type = 'SceneGraphNode', parent = None ):

        '''
        Create a node
        Use current modification context if available

        Examples:
 
        >>> n = Node.createNode('foo'); n.name # doctest: +ELLIPSIS 
        'foo...'
        >>> n = Node.createNode('bar', type='STEREROCAMERA') # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: not a valid node type: STEREOCAMERA
        >>> n = Node.createNode('bar')
        >>> n2 = Node.createNode('cbar', parent=n); n2.longName # doctest: +ELLIPSIS
        'bar...|cbar'
        '''

        # TODO: raise an exception if trying to create an ArchReference
        mc = ModificationContext.get()
        return mc.createNode( name, type, parent )

    def renameNode( self, newName ):

        '''
        Rename a node
        Use current modification context if available

        @param newName (str)
        node new name
        '''

        mc = ModificationContext.get()
        return mc.renameNode( self, newName )

    def loadFile( self, filename ):

        '''
        Load a file content in this node 

        @param filename (str)
        file to load
        @return (list - Node)
        list of created Node instances

        @note
        create Nodes will be parented under current node
        '''

        result = self._node.loadfile( self._node, filename )
        resultNodes = []
        for r in result:
            luaNode = result[r]
            luaNodeLongName = str( luaNode.getpath( luaNode )[0] )
            resultNodes.append( Node( luaNodeLongName ) )

        return resultNodes


class Camera( Node ):

    '''
    Camera class
    '''

    # FIXME: should be TargetPrimitive?

    def setWorldPositionTargetUp( self, position, target, up ):

        '''
        Sets the world position, target and up vector of the node

        @param position (Point3)
        @param target (Point3)
        @param up (Point3)
        '''
        return self._node.setworldpositiontargetup( position._lp, target._lp, up._lp )

    @property
    def worldDirection( self ):
        '''
        Returns the direction to target in world space
        @return (Point3)
        '''

        lp = self._node.getworlddirection( self._node )
        return Point3.fromLua( lp )

    @property
    def worldUp( self ):
        '''
        Returns the node up vector
        @return (Point3)
        '''
        lp = self._node.getworldup( self._node )
        return Point3.fromLua( lp )

    def lookThru( self ):

        '''
        Look through camera. Inactive in nogui mode

        @todo
        Enable code - function is inactive for now
        '''

        self._luaGlobals.pwarning( 'disabled code...' )
        # FIXME: does not work on Guerilla 0.17.0b23, waiting for a fix...
        # if self._luaGlobals.ui is not None:
            # viewport = self._luaGlobals.LUILayoutFocusWindow(
                    # self._luaGlobals.LUILayout,
                    # 'GARenderViewport')
            # if viewport:
                # self._luaGlobals.LUI3dSetCamera(viewport, self._node)


class Reference( Node ):

    def reloadRef( self, newPath = None ):

        # to run this test - run testmod with extraglobs
        # testmod(..., extraglobs={'dvAbcV1': ..., 'dcAbcV2': ...})

        '''
        reload a reference

        Examples:

        @code

        >>> with ModificationContext() as m:
        ...     grp = m.createNode('grp')
        ...     refNodes = m.createRef('aref', dcAbcV1, grp)
        ...     print refNodes[0].ReferenceFileName.get() == dcAbcV1
        ...     refNodes[0].reloadRef(dcAbcV2)
        ...     print refNodes[0].ReferencePathOverride.get() == dcAbcV2
        True
        True

        @encode
        '''

        self._node.reloadref( self._node, newPath )


class TransformModesMeta( type ):

    '''
    TransformModes metaclass
    '''

    def keys( cls ):

        lg = lua.globals()
        for i in lg.SceneGraphNode.TransformModes:
            if isinstance( i, str ):
                yield i

    def __getattr__( cls, key ):

        lg = lua.globals()

        tm = lg.SceneGraphNode.TransformModes[key]
        if tm is None:
            raise AttributeError( 'unknown key %s, valid keys: %s' % ( key, list( cls.keys() ) ) )
        else:
            return tm


class TransformModes( object ):

    '''
    TransformModes
    
    Examples:

    @code
    >>> dict((i, getattr(TransformModes, i)) for i in TransformModes.keys())
    {'Max': 3L, 'PRMan': 1L, 'Local': 0L, 'Maya': 2L}
    >>> TransformModes.foo # doctest: +IGNORE_EXCEPTION_DETAIL +ELLIPSIS
    Traceback (most recent call last):
    AttributeError: 'unknown key %s, valid keys: ...

    @endcode
    '''

    # getattr is defined in the class not in the instance
    # so to define getattr for a class, you need to define getattr
    # in the class of a class -> a metaclass
    __metaclass__ = TransformModesMeta


class Point3( object ):

    '''
    3 dimension point class
    '''

    def __init__( self, x, y, z ):

        self._luaGlobals = lua.globals()
        self._lp = self._luaGlobals.point3.create( x, y, z )

    def __toLua__( self ):
        '''
        Python -> lua object

        @return (lua point3)
        '''
        return self._lp

    @classmethod
    def __fromLua__( cls, lp ):
        '''
        Lua -> python object    

        @return (Point3)
        '''
        return cls( lp[1], lp[2], lp[3] )

    def __neg__( self ):

        return Point3.fromLua( -self._lp )

    def __add__( self, other ):
        return Point3.fromLua( self._lp + other._lp )

    def __sub__( self, other ):
        return Point3.fromLua( self._lp - other._lp )

    def __mul__( self, other ):
        return Point3.fromLua( self._lp * other._lp )

    def __div__( self, other ):
        return Point3.fromLua( self._lp / other._lp )

    def __xor__( self, other ):
        return Point3.fromLua( self._lp ^ other._lp )

    @property
    def x( self ):
        '''
        Point3 first element
        '''

        return self._lp[1]

    @property
    def y( self ):
        '''
        Point3 second element
        '''
        return self._lp[2]

    @property
    def z( self ):
        '''
        Point3 third element
        '''
        return self._lp[3]

    @property
    def value( self ):

        '''
        Return Point3 values

        @return (list)
        '''

        return [self._lp[1], self._lp[2], self._lp[3]]

    @property
    def length( self ):
        '''
        Returns the magnitude of the vector

        @return (float)
        '''

        return self._lp.getlength()

    @property
    def squareLength( self ):
        '''
        Returns the squar magnitude of the vector

        @return (float)
        '''
        return self._lp.getsqlength()

    @property
    def isReal( self ):
        '''
        Returns true if the point is a correct number, false if NAN or INF

        @return (bool)
        '''

        return self._lp.isreal()

    def distance( self, other ):
        '''
        Returns the distance between self and other

        @return (float)
        '''
        return self._lp.distance( other._lp )

    def dot( self, other ):
        '''
        Returns the dot product between self and other

        @return (float)
        '''
        return self._lp.dotproduct( other._lp )

    def max( self, other ):

        '''
        Returns the max of each components

        @return (Point3)
        (max(self.X, other.X), max(self.Y, other.Y), max(self.Z, other.Z)) 
        '''

        if isinstance( other, Point3 ):
            return Point3.fromLua( self._lp.getmax( other._lp ) )
        else:
            return Point3.fromLua( self._lp.getmax( other ) )

    def min( self, other ):

        '''
        Returns the min of each components

        @return (Point3)
        (min(self.X, other.X), min(self.Y, other.Y), min(self.Z, other.Z))
        '''

        if isinstance( other, Point3 ):
            return Point3.fromLua( self._lp.getmin( other._lp ) )
        else:
            return Point3.fromLua( self._lp.getmin( other ) )

    def normalized( self ):
        '''
        Returns the normalized vector

        @return (Point3)
        '''
        return Point3.fromLua( self._lp.getnormalized() )


class PlugMeta( type ):

    '''
    Plug metaclass
    '''

    validFlags = ['ReadOnly',
                'Dynamic',
                'NoSerial',
                'KeepOnCopy',
                'RefReadOnly']

    def flags( cls ):
        return PlugMeta.validFlags

    def __getattr__( cls, key ):

        lg = lua.globals()
        if key in PlugMeta.validFlags:
            return lg.Plug[key]
        else:
            raise AttributeError( 'invalid flags, valid ones: %s' % PlugMeta.validFlags )


class Plug( object ):

    '''
    Base class for all plugs in Guerilla

    Examples:

    @code
    try:
        n = Node('grp')
    except ValueError:
        print 'node grp does not exist'
    else:
        print 'node plugs:'
        print [ p.name for p in n.plugs() ]
    @endcode
    
    @code
    >>> dict((i, getattr(Plug, i)) for i in Plug.flags())
    {'NoSerial': 8L, 'ReadOnly': 64L, 'Dynamic': 4L, 'RefReadOnly': 512L, 'KeepOnCopy': 256L}
    
    @endcode
    '''

    __metaclass__ = PlugMeta

    def __init__( self, name, parent, luaGlobals = None ):

        '''
        Plug constructor
        raise a ValueError if Plug does not exist

        @param name (str)
        plug name
        @param parent (Node)
        parent node
        @param luaGlobals (dict)
        lua globals (default: retrieve lua globals)
        '''

        self._parent = parent

        if luaGlobals:
            self._luaGlobals = luaGlobals
        else:
            self._luaGlobals = lua.globals()

        parentLuaNode = parent._doc if not hasattr( parent, '_node' ) else parent._node
        self._plug = getattr( parentLuaNode, name )

        if self._plug is None:
            raise ValueError( 'plug %s does not exist on node %s' % ( name, parent.name ) )

    def __toLua__( self ):

        '''
        Python -> lua object

        @return (lua plug)
        '''
        return self._plug

    @classmethod
    def __fromLua__( cls, lplug ):

        '''
        Lua to python object

        @return (ModificationContext)
        '''

        # retrieve lua parent node
        lplugParent = lplug.getnode( lplug )
        n = Node( str( lplugParent.getpath( lplugParent )[0] ) )
        # create Plug object
        return Plug( str( lplug.getname( lplug ) ), n )

    @property
    def name( self ):
        '''
        Plug name

        @return (str)
        plug name
        '''
        return str( self._plug.getname( self._plug ) )

    @property
    def parent( self ):
        '''
        Parent node 

        @return (Node)
        parent node
        '''
        luaNode = self._plug.getnode( self._plug )
        return Node( luaNode.getpath( luaNode )[0] )

    def get( self ):
        '''
        Plug value

        @return
        plug value
        '''
        return fromLua( self._plug.get( self._plug ) )

    def set( self, value ):
        '''
        Set plug value. 
        Use current modification context if available

        @param value
        plug value
        '''
        mc = ModificationContext.get()
        mc.setPlug( self, value )

    def isConnected( self ):
        '''
        Check if plug is connected

        @return (bool)
        True if plug is connected to another plug
        @todo 
        http://www.guerillarender.com/redmine/issues/182 resolution
        '''

        isCo = self._plug.isconnected( self._plug )
        return False if isCo is None or isCo == False else True

    def connect( self, plug ):
        '''
        Connect to plug
        Use current modification context if available

        @param plug (Plug)
        plug object
        '''
        mc = ModificationContext.get()
        mc.connect( self, plug )

    def hasDependencies( self ):

        '''
        Check if plug has dependencies

        @return (bool)
        True if plug is has dependencies
        @todo 
        http://www.guerillarender.com/redmine/issues/182 resolution
        '''

        hasDeps = self._plug.hasdependencies( self._plug )
        return False if hasDeps is None or hasDeps == False else True

    def addDependency( self, plug ):
        '''
        Add dependency to plug
        Use current modification context if available

        @param plug (Plug)
        plug object
        '''
        mc = ModificationContext.get()
        mc.addDependency( self, plug )

    def disconnect( self, plug ):
        '''
        Disconnect from plug
        Use current modification context if available

        @param plug (Plug)
        plug object
        '''

        mc = ModificationContext.get()
        mc.disconnect( self, plug )

    def touch( self ):

        '''
        Invalidate (ie. force re-evaluation) value
        Use current modification context if available
        '''

        mc = ModificationContext.get()
        mc.touch( self )

    def isTyped( self ):

        '''
        Check if plug has a type or not

        @return (bool) 
        True if plug is typed else False
        '''

        return self._plug.gettype( self._plug ) != None

    def connections( self, source = True, destination = False ):

        '''
        Retrieve connected plug

        @param source (bool)
        return outputs
        @param destination (bool)
        return input 

        @return (list - Plug)
        return list of connected plug
        '''

        luaPlug = self._plug
        plugs = []

        # XXX: factorize code (cf dependencies method too)

        if source:

            coLuaPlugs = luaPlug.getoutputs( luaPlug ) or []

            for i in coLuaPlugs:

                cLuaPlug = coLuaPlugs[i]
                coLuaPlugParent = cLuaPlug.getnode( cLuaPlug )

                p = Plug( str( cLuaPlug.getname( cLuaPlug ) ),
                        Node( str( coLuaPlugParent.getpath( coLuaPlugParent )[0] ) ) )
                plugs.append( p )

        if destination:

            coLuaPlug = luaPlug.getinput( luaPlug ) or []

            coLuaPlugParent = coLuaPlug.getnode( coLuaPlug )

            p = Plug( str( coLuaPlug.getname( coLuaPlug ) ),
                    Node( str( coLuaPlugParent.getpath( coLuaPlugParent )[0] ) ) )
            plugs.append( p )

        return plugs

    def dependencies( self, source = True, destination = False ):

        '''
        Retrieve dependencies and backdependencies

        @param source (bool)
        return back dependencies
        @param destination (bool)
        return dependencies

        @return (list - Plug)
        return list of connected plug
        '''
        luaPlug = self._plug
        plugs = []

        # XXX: factorize code

        if source:
            backDeps = luaPlug.getbackdependencies( luaPlug ) or []

            for i in backDeps:

                depLuaPlug = backDeps[i]
                depLuaPlugParent = depLuaPlug.getnode( depLuaPlug )

                p = Plug( str( depLuaPlug.getname( depLuaPlug ) ),
                        Node( str( depLuaPlugParent.getpath( depLuaPlugParent )[0] ) ) )

                plugs.append( p )

        if destination:

            deps = luaPlug.getdependencies( luaPlug ) or []

            for i in deps:

                depLuaPlug = deps[i]
                depLuaPlugParent = depLuaPlug.getnode( depLuaPlug )

                p = Plug( str( depLuaPlug.getname( depLuaPlug ) ),
                        Node( str( depLuaPlugParent.getpath( depLuaPlugParent )[0] ) ) )

                plugs.append( p )

        return plugs


class Command( object ):

    '''
    Base class to create a Guerilla command

    Examples:

    @code
    class AddNode(Command):
        @staticmethod
        def action(a1, a2, a3, a4, a5):
            from pyGuerilla import Node
            n = Node.createNode('foo')
    cmd = AddNode('addNode')
    cmd.install()
    @endcode
    '''

    def __init__( self, cmdName, mainMenuName = 'pyGuerilla', subMenuName = '' ):

        '''
        Command constructor

        @param cmdName (str)
        command name
        @param mainMenuName (str)
        main menu name
        @param subMenuName (str)
        sub menu name

        In Guerilla, run the command by clicking:
        mainMenuName -> subMenuName -> cmdName

        @note Command class should be derived
        @note reimplement isenabled and action as staticmethod

        @todo enforce staticmethod http://stackoverflow.com/questions/4474395/staticmethod-and-abc-abstractmethod-will-it-blend
        '''

        self.cmdName = cmdName
        self.mainMenuName = mainMenuName
        self.subMenuName = cmdName if not self.cmdName else subMenuName
        self.lg = lua.globals()
        self.ui = False if self.lg.ui is None else True

    def install( self ):
        # TODO: install command even if self.ui == False
        # FIXME: could not call command using executebyshortname
        if self.ui:
            self.cmd = self.lg.command.create( self.cmdName, None, None )
            self.cmd.isenabled = self.isenabled
            self.cmd.action = self.action
            self.lg.MainMenu.addcommand( self.lg.MainMenu,
                    self.cmd,
                    self.mainMenuName,
                    self.subMenuName )

    @staticmethod
    def isenabled( a1, a2 ):

        '''
        isenabled callback for command
        @todo args name
        '''

        return True

    @staticmethod
    def action( a1, a2, a3, a4, a5 ):

        '''
        action callback for command
        @todo args name
        '''
        pass


class Gtypes( object ):

    '''
    Guerilla types class (for createPlug function)

    Examples:

    @code

    >>> all([t in Gtypes.validTypes for t in ['int', 'float', 'bool']])
    True
    >>> gt = Gtypes('enum', desc=('itemA', ('itemB', 12), 'itemC'))    
    >>> gt = Gtypes('filename')
    >>> gt = Gtypes('directory', desc={'title': 'pandoraBox'})

    @endcode
    '''

    # --> nose tests?
    # >>> gt = Gtypes('color'); toLua(gt).Type
    # 'color'

    validTypes = [ str( t ) for t in lua.globals().types ]
    # validTypeKeys = {
            # 'filename': ['mode', 'title', 'filter', 'directory', 'extension', 'category'],
            # 'directory': ['mode', 'title', 'filter', 'directory', 'extension', 'category'],
            # 'int': ['min', 'max', 'step', 'slidermin', 'slidermax', 'noslider' ],
            # 'float': ['min', 'max', 'step', 'slidermin', 'slidermax', 'noslider' ],
            # }
    descRequired = ( 'enum', 'dynenum' )

    def __init__( self, type, value = None, **kwargs ):

        '''
        Gtypes constructor
        '''

        if type not in Gtypes.validTypes:
            raise ValueError( 'unknown type %s, valid ones: %s' % ( type, Gtypes.validTypes ) )

        self._luaGlobals = lua.globals()

        # save type and value
        self.type = type
        self.value = value

        # guerilla lua type: ex int, float, color
        glt = getattr( self._luaGlobals.types, self.type )
        # is desc provided, required to some type like enum
        desc = kwargs.get( 'desc', None )

        if self._luaGlobals.type( glt ) == 'function':
            if desc:
                self._gLuaType = glt( toLua( desc ) )
            else:
                if self.type in Gtypes.descRequired:
                    raise ValueError( 'Missing desc for type: %s' % self.type )
                else:
                    self._gLuaType = glt( toLua( [] ) )
        else:
            self._gLuaType = glt

        self._luaValue = None

    @property
    def default( self ):

        '''
        default type value
        @return default value
        '''

        return getattr( self._gLuaType, 'DefaultValue' )

    def __toLua__( self ):
        '''
        python Gtypes -> lua guerilla types

        @return (lua types)
        '''
        return self._gLuaType


def blast( camera, imgPath, **kwargs ):

    '''
    blast command (EXPERIMENTAL)

    @param camera (str or Node)
    camera
    @param imgPath (str)
    image fullpath without extension or padding
    @param kwargs (dict)
    optional arguments (default to current value in scene): 
    - width, height
    - firstFrame, lastFrame
    - shadingMode (valid values: 'wireframe', 'filled', 'shaded', 'shadednotexture')
 
    @return (str) 
    image path with padding, ex: /tmp/blast.%05d.png
    @note
    - modify current time
    - blast method is asynchronous
    - http://www.guerillarender.com/redmine/issues/228
    - http://www.guerillarender.com/redmine/issues/239
    - http://www.guerillarender.com/redmine/issues/240

    Examples:

    @code
    >>> import os; import tempfile; blast('Perspective', os.path.join(tempfile.gettempdir(), 'blastImg.%04d.png'))
    '/tmp/blastImg.%04d.png'

    @endcode
    '''

    VALID_ARGS = {
            'width': 'width',
            'height': 'height',
            'firstFrame': 'firstframe',
            'lastFrame': 'lastframe',
            'shadingMode': ''
            }
    VALID_VALUES = {
            'shadingMode': ['wireframe', 'filled', 'shaded', 'shadednotexture']
            }
    # VALID_EXT = ['.png', '.tiff']
    VALID_EXT = ['.png']

    _, ext = os.path.splitext( imgPath )

    if ext not in VALID_EXT:
        raise ValueError( 'not a valid image extension, could only be: %s' % VALID_EXT )

    rgx = re.search( r'''((?P<fc>\.|_|-) # padding should start with . or - or _ 
            %%(?P<padding>\d+)?d         # accept %%d or %%04d 
            \.(?P<ext>%s))$             # extension, ie. '.png' ''' % ext[1:],
            imgPath,
            re.VERBOSE )

    if not rgx:
        raise ValueError( 'not a valid image path, should be like: IMAGE.%%05d.%s' % ext[1:] )

    # get lua globals
    lg = lua.globals()
    doc = Document()

    # prepare dict for blast command
    blastDict = {
            'camera': toLua( camera ),
            'file': imgPath,
            'forceFilename': True,
            'codec': ext[1:],
            }

    for k, v in kwargs.iteritems():
        if k in VALID_ARGS:
            if VALID_VALUES.has_key( k ) and v not in VALID_VALUES:
                continue
            blastDict[VALID_ARGS[k]] = v

    if not blastDict.has_key( 'firstframe' ):
        blastDict['firstframe'] = doc.FirstFrame.get()
    if not blastDict.has_key( 'lastframe' ):
        blastDict['lastframe'] = doc.LastFrame.get()

    # blasting...
    doc.Time.set( blastDict['firstframe'] )
    lg.blast( toLua( blastDict ) )
    #
    # doc.Time.set(cTime)

    return imgPath


def test():

	# doctests
	import doctest
	import pyGuerilla
	print pyGuerilla.__file__

	eg = {
		'dcAbcV1': './tests/data/file1.abc', 
		'dcAbcV2': './tests/data/file2.abc',
	}
	doctest.testmod(pyGuerilla, verbose=True, extraglobs=eg)

	# nose
	import nose
	nose.run(argv=['--verbosity=3', '-s', '--with-isolation', '-w', './tests'])

if __name__ == '__main__':

    test()
