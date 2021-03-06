# Adapted for numpy/ma/cdms2 by convertcdms.py
# Marker (Tm) module
###############################################################################
#                                                                             #
# Module:       marker (Tm) module                                            #
#                                                                             #
# Copyright:    2000, Regents of the University of California                 #
#               This software may not be distributed to others without        #
#               permission of the author.                                     #
#                                                                             #
# Author:       PCMDI Software Team                                           #
#               Lawrence Livermore NationalLaboratory:                        #
#               support@pcmdi.llnl.gov                                        #
#                                                                             #
# Description:  Python command/1d
# wrapper for VCS's marker secondary object.     #
#                                                                             #
# Version:      4.0                                                           #
#                                                                             #
###############################################################################
#
#
#
from __future__ import print_function
from . import VCS_validation_functions
import vcs
import genutil
from .xmldocs import scriptdocs, listdoc


def process_src(nm, code):

    # Takes VCS script code (string) as input and generates oneD gm from it
    try:
        gm = Tm(nm)
    except Exception:
        gm = vcs.elements["marker"][nm]
    # process attributes with = as assignement
    for att in ["projection", ]:
        i = code.find(att)
        if i == -1:
            continue
        j = code[i:].find(",") + i
        if j - i == -1:  # last one no comma
            j = None
        scode = code[i:j]
        sp = scode.split("=")
        nm = sp[0].strip()
        nm = nm.replace("#", "")
        try:
            # int will be converted
            setattr(gm, nm, int(sp[1]))
        except Exception:
            try:
                # int and floats will be converted
                setattr(gm, nm, eval(sp[1]))
            except Exception:
                # strings
                try:
                    setattr(gm, nm, sp[1])
                except Exception:
                    pass  # oh well we stick to default value
        # Datawc
        for att in ["mtyp", "msize", "mci", "vp", "wc"]:
            i = code.find(" %s(" % att)
            if i > -1:
                j = code[i:].find(")") + i
                cd = code[i + len(att) + 2:j]
                vals = cd.split(",")
                values = []
                # print "ATT:",att,vals
                for v in vals:
                    try:  # int first
                        values.append(int(v))
                    except Exception:
                        try:
                            values.append(float(v))
                        except Exception:
                            values.append(v)
                try:
                    if att == "mtyp":
                        gm.type = values
                    elif att == "msize":
                        gm.size = values
                    elif att == "mci":
                        gm.color = values
                    elif att == "vp":
                        gm.viewport = values
                    elif att == "wc":
                        gm.worldcoordinate = values
                    else:
                        raise Exception("Unkwnow marker attribute: %s" % att)
                except Exception:
                    pass
        for att in ["x", "y"]:
            i = code.find(" %s(" % att)
            if i == -1:
                i = code.find(",%s(" % att)
            if i > -1:
                v = genutil.get_parenthesis_content(code[i:])
                setattr(gm, att, eval(v))


#############################################################################
#                                                                           #
# Marker (Tm) Class.                                                        #
#                                                                           #
#############################################################################
class Tm(vcs.bestMatch):

    """
    The Marker object allows the manipulation of marker type, size, and color index.

    This class is used to define an marker table entry used in VCS, or it
    can be used to change some or all of the marker attributes in an
    existing marker table entry.

    Markers are intended to be sized consistently across all plots and legends,
    indepenent of plot size or world coordinate range.  The size attribute
    sets the screen size (in "deci-pixels", see below) of the marker.


    .. describe:: Useful Functions:

        .. code-block:: python

            # VCS Canvas Constructor
            a=vcs.init()
            # Show predefined marker objects
            a.show('marker')
            # Updates the VCS Canvas at user's request
            a.update()
            a=vcs.init()

    .. describe:: Create a new instance of marker:

        .. code-block:: python

            # Copies content of 'red' to 'new'
            mk=a.createmarker('new','red')
            # Copies content of 'default' to 'new'
            mk=a.createmarker('new')

    .. describe:: Modify an existing marker:

        .. code-block:: python

            mk=a.getmarker('red')

    .. describe:: Overview of marker attributes:

        * List all the marker attribute values:

            .. code-block:: python

                mk.list()
                # Range from 1 to 256
                mk.color=100
                # Range from 1 to 300 (screen size, in "deci-pixels", i.e. marker size * 10 = size in pixels)
                mk.size=100

        * Specify the marker type:

            .. code-block:: python

                # Same as mk.type=1
                mk.type='dot'
                # Same as mk.type=2
                mk.type='plus'
                # Same as mk.type=3
                mk.type='star'
                # Same as mk.type=4
                mk.type='circle'
                # Same as mk.type=5
                mk.type='cross'
                # Same as mk.type=6
                mk.type='diamond'
                # Same as mk.type=7
                mk.type='triangle_up'
                # Same as mk.type=8
                mk.type='triangle_down'
                # Same as mk.type=9
                mk.type='triangle_left'
                # Same as mk.type=10
                mk.type='triangle_right'
                # Same as mk.type=11
                mk.type='square'
                # Same as mk.type=12
                mk.type='diamond_fill'
                # Same as mk.type=13
                mk.type='triangle_up_fill'
                # Same as mk.type=14
                mk.type='triangle_down_fill'
                # Same as mk.type=15
                mk.type='triangle_left_fill'
                # Same as mk.type=16
                mk.type='triangle_right_fill'
                # Same as mk.type=17
                mk.type='square_fill'

        * Set the graphics priority on the canvas

            .. code-block:: python

                mk.priority=1
                # FloatType [0,1]x[0,1]
                mk.viewport=[0, 1.0, 0,1.0]
                # FloatType [#,#]x[#,#]
                mk.worldcoordinate=[0,1.0,0,1.0]

        * Example x and y coordinates:

            .. code-block:: python

                # List of FloatTypes
                mk.x=[[0,.1,.2], [.3,.4,.5]]
                # List of FloatTypes
                mk.y=[[.5,.4,.3], [.2,.1,0]]

        .. pragma: skip-doctest
        """
    __slots__ = [
        's_name',
        '_name',
        '_color',
        '_priority',
        '_type',
        '_size',
        '_viewport',
        '_worldcoordinate',
        '_x',
        '_y',
        '_projection',
        '_colormap',
    ]
    colormap = VCS_validation_functions.colormap

    def _getname(self):
        return self._name

    def _setname(self, value):
        value = VCS_validation_functions.checkname(self, 'name', value)
        if value is not None:
            self._name = value
    name = property(_getname, _setname)

    def _getfillareacolors(self):
        return self._color

    def _setfillareacolors(self, value):
        if isinstance(value, int):
            value = [value, ]
        if value is not None:
            value = VCS_validation_functions.checkColorList(
                self,
                'color',
                value)
        self._color = value
    color = property(_getfillareacolors, _setfillareacolors)

    def _gettype(self):
        return self._type

    def _settype(self, value):
        if not isinstance(value, (list, tuple)) and value is not None:
            value = [value, ]
        if value is not None:
            value = VCS_validation_functions.checkMarkersList(
                self,
                'type',
                value)
        self._type = value
    type = property(_gettype, _settype)

    def _getsize(self):
        return self._size

    def _setsize(self, value):
        if VCS_validation_functions.isNumber(value):
            value = [value, ]
        if value is not None:
            value = VCS_validation_functions.checkListOfNumbers(
                self,
                'size',
                value,
                minvalue=0,
                maxvalue=300)
        self._size = value
    size = property(_getsize, _setsize)

    def _getpriority(self):
        return self._priority

    def _setpriority(self, value):
        value = VCS_validation_functions.checkInt(
            self,
            'priority',
            value,
            minvalue=0)
        self._priority = value
    priority = property(_getpriority, _setpriority)

    def _getprojection(self):
        return self._projection

    def _setprojection(self, value):
        value = VCS_validation_functions.checkProjection(
            self,
            'projection',
            value)
        self._projection = value
    projection = property(_getprojection, _setprojection)

    def _getwc(self):
        return self._worldcoordinate

    def _setwc(self, value):
        value = VCS_validation_functions.checkListOfNumbers(
            self,
            'worldcoordinate',
            value,
            maxelements=4)
        self._worldcoordinate = value
    worldcoordinate = property(_getwc, _setwc)

    def _getvp(self):
        return self._viewport

    def _setvp(self, value):
        value = VCS_validation_functions.checkListOfNumbers(
            self,
            'viewport',
            value,
            maxelements=4,
            minvalue=0.,
            maxvalue=1.)
        self._viewport = value
    viewport = property(_getvp, _setvp)

    def _getx(self):
        return self._x

    def _setx(self, value):
        if value is None:
            self._x = None
            return
        if not isinstance(value, (list, tuple)):
            raise ValueError(
                'x must be a tuple or list of values. You sent: %s' %
                value)
        try:
            # first we'll see if it is simply a list of values
            value = VCS_validation_functions.checkListOfNumbers(
                self,
                'x',
                value)
        except Exception:
            # ok it was not, so it maybe a list of list of numbers ?
            val = []
            for v in value:
                tmp = VCS_validation_functions.checkListOfNumbers(self, 'x', v)
                val.append(tmp)
            value = val
        # ok it worked
        self._x = value
    x = property(_getx, _setx)

    def _gety(self):
        return self._y

    def _sety(self, value):
        if value is None:
            self._y = None
            return
        if not isinstance(value, (list, tuple)):
            raise ValueError(
                'y must be a tuple or list of values. You sent: %s' %
                value)
        try:
            # first we'll see if it is simply a list of values
            value = VCS_validation_functions.checkListOfNumbers(
                self,
                'y',
                value)
        except Exception:
            # ok it was not, so it maybe a list of list of numbers ?
            val = []
            for v in value:
                tmp = VCS_validation_functions.checkListOfNumbers(self, 'y', v)
                val.append(tmp)
            value = val
        # ok it worked
        self._y = value
    y = property(_gety, _sety)

    def __init__(self, Tm_name, Tm_name_src='default'):
        if (Tm_name is None):
            raise ValueError('Must provide a marker name.')
        self._name = Tm_name
        self.s_name = 'Tm'
        if Tm_name == "default":
            self._type = ["dot", ]
            self._size = [1.0, ]
            self._color = [1, ]
            self._priority = 1
            self._viewport = [0., 1., 0., 1.]
            self._worldcoordinate = [0., 1., 0., 1.]
            self._x = None
            self._y = None
            self._projection = "default"
            self._colormap = None
        else:
            if isinstance(Tm_name_src, Tm):
                Tm_name_src = Tm_name_src.name
            if Tm_name_src not in vcs.elements['marker']:
                raise ValueError(
                    "The marker object '%s' does not exists" %
                    Tm_name_src)
            src = vcs.elements["marker"][Tm_name_src]
            for att in ['colormap', 'projection', 'color', 'size',
                        'type', 'viewport', 'worldcoordinate', 'priority', 'x', 'y']:
                setattr(self, att, getattr(src, att))
        # Ok now we need to stick in the elements
        vcs.elements["marker"][Tm_name] = self

    def list(self):
        if (self.name == '__removed_from_VCS__'):
            raise ValueError('This instance has been removed from VCS.')
        print("---------- Marker (Tm) member (attribute) listings ----------")
        print("secondary method =", self.s_name)
        print("name =", self.name)
        print("type =", self.type)
        print("size =", self.size)
        print("color =", self.color)
        print("priority =", self.priority)
        print("viewport =", self.viewport)
        print("worldcoordinate =", self.worldcoordinate)
        print("x =", self.x)
        print("y =", self.y)
        print("projection =", self.projection)
        print("colormap =", self.colormap)
    list.__doc__ = listdoc.format(name="marker", parent="")

    def script(self, script_filename=None, mode=None):
        if (script_filename is None):
            raise ValueError(
                'Error - Must provide an output script file name.')

        if (mode is None):
            mode = 'a'
        elif (mode not in ('w', 'a')):
            raise ValueError(
                'Error - Mode can only be "w" for replace or "a" for append.')

        # By default, save file in json
        scr_type = script_filename.split(".")
        if len(scr_type) == 1 or len(scr_type[-1]) > 5:
            scr_type = "json"
            if script_filename != "initial.attributes":
                script_filename += ".json"
        else:
            scr_type = scr_type[-1]
        if scr_type == '.scr':
            raise vcs.VCSDeprecationWarning("scr script are no longer generated")
        elif scr_type == "py":
            mode = mode + '+'
            py_type = script_filename[
                len(script_filename) -
                3:len(script_filename)]
            if (py_type != '.py'):
                script_filename = script_filename + '.py'

            # Write to file
            fp = open(script_filename, mode)
            if (fp.tell() == 0):  # Must be a new file, so include below
                fp.write("#####################################\n")
                fp.write("#                                 #\n")
                fp.write("# Import and Initialize VCS     #\n")
                fp.write("#                             #\n")
                fp.write("#############################\n")
                fp.write("import vcs\n")
                fp.write("v=vcs.init()\n\n")

            unique_name = '__Tm__' + self.name
            fp.write("#----------Marker (Tm) member (attribute) listings ----------\n")
            fp.write("tm_list=v.listelements('marker')\n")
            fp.write("if ('%s' in tm_list):\n" % self.name)
            fp.write("   %s = v.getmarker('%s')\n" % (unique_name, self.name))
            fp.write("else:\n")
            fp.write("   %s = v.createmarker('%s')\n" % (unique_name, self.name))
            fp.write("%s.type = %s\n" % (unique_name, self.type))
            fp.write("%s.size = %s\n" % (unique_name, self.size))
            fp.write("%s.color = %s\n\n" % (unique_name, self.color))
            fp.write("%s.priority = %d\n" % (unique_name, self.priority))
            fp.write("%s.viewport = %s\n" % (unique_name, self.viewport))
            fp.write("%s.worldcoordinate = %s\n" % (unique_name, self.worldcoordinate))
            fp.write("%s.x = %s\n" % (unique_name, self.x))
            fp.write("%s.y = %s\n" % (unique_name, self.y))
            fp.write("%s.projection = '%s'\n" % (unique_name, self.projection))
            if self.colormap is not None:
                fp.write("%s.colormap = %s\n\n" % (unique_name, repr(self.colormap)))
            else:
                fp.write("%s.colormap = %s\n\n" % (unique_name, self.colormap))
        else:
            # Json type
            mode += "+"
            f = open(script_filename, mode)
            vcs.utils.dumpToJson(self, f)
            f.close()
    script.__doc__ = scriptdocs['marker']
