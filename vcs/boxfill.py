"""
# Boxfill (Gfb) module
"""
###############################################################################
# Module:	boxfill (Gfb) module					      #
# Copyright:    2000, Regents of the University of California		      #
#               This software may not be distributed to others without	      #
#               permission of the author.				      #
# Author:       PCMDI Software Team                                           #
#               Lawrence Livermore NationalLaboratory:                        #
#               support@pcmdi.llnl.gov                                        #
# Description:	Python command wrapper for VCS's boxfill graphics method.     #
# Version:      5.0							      #
###############################################################################


from __future__ import print_function
import vcs
import cdtime
from . import VCS_validation_functions
from . import xmldocs
import numpy
import warnings


def process_src(nm, code):

    # Takes VCS script code (string) as input and generates boxfill gm from it

    try:
        gm = Gfb(nm)
    except Exception:
        gm = vcs.elements["boxfill"][nm]
    # process attributes with = as assignement
    for att in ["projection",
                "xticlabels#1", "xticlabels#2",
                "xmtics#1", "xmtics#2",
                "yticlabels#1", "yticlabels#2",
                "ymtics#1", "ymtics#2",
                "xaxisconvert", "yaxisconvert",
                "datawc_tunits",
                "boxfill_type",
                "level_1", "level_2",
                "color_1", "color_2",
                "fillareastyle", "fillareaindices",
                "fillareacolors", "fillareaopacity",
                "fillareapixelspacing", "fillareapixelscale",
                "legend",
                "ext_1", "ext_2",
                "missing",
                "datawc_tunits",
                "datawc_calendar"]:
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
        if nm == "datawc_tunits":
            nm = "datawc_timeunits"
        if nm == "legend":
            if sp[1] != "()":
                gm.legend = sp[1][1:-1]
            continue
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
    idwc = code.find("datawc(")
    if idwc > -1:
        jdwc = code[idwc:].find(")") + idwc
        cd = code[idwc + 7:jdwc]
        vals = cd.split(",")
        gm.datawc_x1 = float(vals[0])
        gm.datawc_y1 = float(vals[1])
        gm.datawc_x2 = float(vals[2])
        gm.datawc_y2 = float(vals[3])
    # idatawc
    idwc = code.find("idatawc(")
    if idwc > -1:
        jdwc = code[idwc:].find(")") + idwc
        cd = code[idwc + 8:jdwc]
        vals = cd.split(",")
        if int(vals[0]) == 1:
            gm.datawc_x1 = cdtime.reltime(
                gm.datawc_x1,
                gm.datawc_timeunits).tocomp(
                gm.datawc_calendar)
        if int(vals[1]) == 1:
            gm.datawc_y1 = cdtime.reltime(
                gm.datawc_x2,
                gm.datawc_timeunits).tocomp(
                gm.datawc_calendar)
        if int(vals[2]) == 1:
            gm.datawc_x2 = cdtime.reltime(
                gm.datawc_y1,
                gm.datawc_timeunits).tocomp(
                gm.datawc_calendar)
        if int(vals[3]) == 1:
            gm.datawc_y2 = cdtime.reltime(
                gm.datawc_y2,
                gm.datawc_timeunits).tocomp(
                gm.datawc_calendar)
    vcs.utils.process_range_from_old_scr(code, gm)
#############################################################################
#                                                                           #
# Boxfill (Gfb) graphics method Class.                                      #
#                                                                           #
#############################################################################
# class Gfb(graphics_method_core):


class Gfb(vcs.bestMatch):

    __doc__ = """The boxfill graphics method (Gfb) displays a two-dimensional
    data array by surrounding each data value by a colored grid box.

    This class is used to define a boxfill table entry used in VCS, or it
    can be used to change some or all of the attributes in an existing
    boxfill table entry.

    .. describe:: General use of a boxfill:

            .. code-block:: python

                # Constructor
                a=vcs.init()
                # Show predefined boxfill graphics methods
                a.show('boxfill')
                # Change the VCS color map
                a.setcolormap("AMIP")
                # Plot data 's' with boxfill 'b' and 'default' template
                a.boxfill(s,b,'default')

    .. describe:: Updating a boxfill:

        .. code-block:: python

            # Updates the VCS Canvas at user's request
            a.update()
            # Set VCS Canvas to automatic update mode
            a.mode=1
            # Use update function to update the VCS Canvas
            a.mode=0

    .. describe:: Create a new instance of boxfill:

        .. code-block:: python

            #  Copies content of 'quick' to 'new'
            box=a.createboxfill('new','quick')
            #  Copies content of 'default' to 'new'
            box=a.createboxfill('new')

    .. describe:: Modifying an existing boxfill:

        .. code-block:: python

            fill=a.getboxfill('quick')

            # Set index using fillarea
            box.fillareaindices=(7,fill,4,9,fill,15)
            # list fillarea attributes
            fill.list()
            # change style
            fill.style='hatch'
            # change color
            fill.color='black'
            # change style index
            fill.index=3

    .. describe:: Overview of boxfill attributes:

        * Listing all the boxfill attribute values:

            .. code-block:: python

                box.list()

        * Setting boxfill attribute values:

            .. code-block:: python

                box.projection='linear'
                lon30={-180:'180W',-150:'150W',0:'Eq'}
                box.xticlabels1=lon30
                box.xticlabels2=lon30
                # Will set them both
                box.xticlabels(lon30, lon30)
                box.xmtics1=''
                box.xmtics2=''
                # Will set them both
                box.xmtics(lon30, lon30)
                box.yticlabels1=lat10
                box.yticlabels2=lat10
                # Will set them both
                box.yticlabels(lat10, lat10)
                box.ymtics1=''
                box.ymtics2=''
                # Will set them both
                box.ymtics(lat10, lat10)
                box.datawc_y1=-90.0
                box.datawc_y2=90.0
                box.datawc_x1=-180.0
                box.datawc_x2=180.0
                # Will set them all
                box.datawc(-90, 90, -180, 180)
                box.xaxisconvert='linear'
                box.yaxisconvert='linear'
                # Will set them both
                box.xyscale('linear', 'area_wt')
                box.level_1=1e20
                box.level_2=1e20
                box.color_1=0
                box.color_2=255
                # Will set them both
                box.colors(0, 255 )
                # 'linear' - compute or specify legend
                box.boxfill_type='linear'
                # 'log10' - plot using log10
                box.boxfill_type='log10'
                # 'custom' - use custom values to display legend evenly
                box.boxfill_type='custom'
                # Hold the legend values
                box.legend=None
                # Show left overflow arrow
                box.ext_1='n'
                # Show right overflow arrow
                box.ext_2='y'
                # Will set them both
                box.exts('n', 'y' )
                box.missing='black'

        * Setting the boxfill levels:

            .. code-block:: python

                # Case 1: Levels are all contiguous:
                box.levels=([0,20,25,30,35,40],)
                box.levels=([0,20,25,30,35,40,45,50])
                box.levels=[0,20,25,30,35,40]
                box.levels=(0.0,20.0,25.0,30.0,35.0,40.0,50.0)

                # Case 2: Levels are not contiguous:
                box.levels=([0,20],[30,40],[50,60])
                box.levels=([0,20,25,30,35,40],[30,40],[50,60])

        * Setting the fillarea color indices:

            .. code-block:: python

                # Three different methods for setting color indices:
                box.fillareacolors=([22,33,44,55,66,77])
                box.fillareacolors=(16,19,33,44)
                box.fillareacolors=None

        * Setting the fillarea style:

            .. code-block:: python

                box.fillareastyle = 'solid'
                box.fillareastyle = 'hatch'
                box.fillareastyle = 'pattern'

        * Setting the fillarea hatch or pattern indices:

            .. code-block:: python

                box.fillareaindices=([1,3,5,6,9,20])
                box.fillareaindices=(7,1,4,9,6,15)

        * Using the fillarea secondary object (Ex):

            .. code-block:: python

                f=createfillarea('fill1')
                #To Create a new instance of fillarea use:
                # Copies 'quick' to 'new'
                fill=a.createfillarea('new','quick')
                # Copies 'default' to 'new'
                fill=a.createfillarea('new')

        .. _boxfill-attribute-descriptions:

        * Attribute descriptions:

            * Universally considered attributes:

                .. py:attribute:: boxfill_type (str)

                    Type of boxfill legend. One of 'linear', 'log10', or 'custom'.
                    See examples above for usage.
                    Relevant attributes per type noted in attribute descriptions.

                .. py:attribute:: missing (int)

                    Color to use for missing value or values not in defined ranges.

            * boxfill_type 'linear'/'log10' relevant attributes:

                .. py:attribute:: level_1 (float)

                    Used in conjunction with boxfill_type linear/log10.
                    Sets the value of the legend's first level

                .. py:attribute:: level_2 (float)

                    Used in conjunction with boxfill_type linear/log10,
                    sets the value of the legend's end level.

                .. py:attribute:: color_1 (float)

                    Used in conjunction with boxfill_type linear/log10,
                    sets the first value of the legend's color range.

                .. py:attribute:: color_2 (float)

                    Used in conjunction with boxfill_type linear/log10.
                    Sets the last value of the legend's color range.

                .. py:attribute:: legend ({float:str})

                    Used in conjunction with boxfill_type linear/log10.
                    replaces the legend values in the dictionary keys with their
                    associated string.

                .. py:attribute:: ext_1 (str)

                    Draws an extension arrow on right side of a boxfill
                    (values less than first range value)

                .. py:attribute:: ext_2 (str)

                    Draws an extension arrow on left side of a boxfill
                    (values greater than last range value)

            * boxfill_type 'custom' relevant attributes:

                .. py:attribute:: levels (list of floats)

                    Used in conjunction with boxfill_type custom.
                    Sets the levels range to use.
                    Can be either a list of contiguous levels, or list of tuples
                    indicating first and last value of the range.

                .. py:attribute:: fillareacolors (list)

                    Used in conjunction with boxfill_type custom.
                    Specifies colors to use for each level.

            * More boxfill attributes:

            %s

            .. pragma: skip-doctest
            """ % xmldocs.graphics_method_core  # noqa

    def rename(self, newname):
        """Renames the boxfill in the VCS name table.

        .. note::

            This function will not rename the 'default' boxfill.
            If rename is called on the 'default' boxfill, newname is associated
            with default in the VCS name table, but the boxfill's name will not
            be changed, and will behave in all ways as a 'default' boxfill.

        :Example:

            .. doctest:: gfb_rename

                >>> b=vcs.createboxfill('bar')
                >>> l=vcs.listelements('boxfill') # list of boxfills
                >>> 'bar' in l # shows l contains new boxfill
                True
                >>> b.rename('foo')
                >>> l=vcs.listelements('boxfill') # new list of boxfills
                >>> 'foo' in l # new name is in list
                True
                >>> 'bar' in l # old name is not
                False

        :param newname: The new name you want given to the boxfill
        :type newname: str
        """
        if newname == "default":
            raise Exception(
                "You cannot overwrite the default boxfill graphic method")
        if newname in list(vcs.elements["boxfill"].keys()):
            raise Exception(
                "Sorry %s boxfill graphic method already exists" %
                newname)
        vcs.elements["boxfill"][newname] = vcs.elements["boxfill"][self.name]
        if self.name == "default":
            warnings.warn(
                "You were trying to rename the 'deafult' boxfill method, it was merely copied not renamed")
        else:
            vcs.elements["boxfill"].pop(self.name)
            self._name = newname
        self = vcs.elements["boxfill"][newname]
        return

    __slots__ = [
        'g_name',
        '_colormap',
        '_name',
        '_xaxisconvert',
        '_yaxisconvert',
        '_levels',
        '_fillareacolors',
        '_fillareastyle',
        '_fillareaindices',
        '_fillareaopacity',
        '_fillareapixelspacing',
        '_fillareapixelscale',
        '_ext_1',
        '_ext_2',
        '_missing',
        '_projection',
        '_xticlabels1',
        '_xticlabels2',
        '_yticlabels1',
        '_yticlabels2',
        '_xmtics1',
        '_xmtics2',
        '_ymtics1',
        '_ymtics2',
        '_datawc_x1',
        '_datawc_x2',
        '_datawc_y1',
        '_datawc_y2',
        '_legend',
        '_boxfill_type',
        '_color_1',
        '_color_2',
        '_level_1',
        '_level_2',
        '_datawc_timeunits',
        '_datawc_calendar',
    ]
    colormap = VCS_validation_functions.colormap
# Removed from doc string
# box.levels(10, 90)  		# Will set them both

    ###########################################################################
    #                                                                         #
    # Initialize the boxfill attributes.                                      #
    #                                                                         #
    ###########################################################################
    def __init__(self, Gfb_name=None, Gfb_name_src='default'):
        if isinstance(Gfb_name_src, Gfb):
            Gfb_name_src = Gfb_name_src.name
        if Gfb_name == "default" and Gfb_name_src != "default":
            raise Exception("You can not alter the 'default' boxfill method")
        if Gfb_name in list(vcs.elements["boxfill"].keys()):
            raise Exception(
                "Error boxfill method '%s' already exists" %
                Gfb_name)
        self._name = Gfb_name
        self.g_name = 'Gfb'

        if Gfb_name == "default":
            self._projection = "linear"
            self._xticlabels1 = "*"
            self._xticlabels2 = "*"
            self._xmtics1 = ""
            self._xmtics2 = ""
            self._yticlabels1 = "*"
            self._yticlabels2 = "*"
            self._ymtics1 = ""
            self._ymtics2 = ""
            self._datawc_y1 = 1.e20
            self._datawc_y2 = 1.e20
            self._datawc_x1 = 1.e20
            self._datawc_x2 = 1.e20
        # End Core Graphics Method attributes
            self._xaxisconvert = "linear"
            self._yaxisconvert = "linear"
            self._ext_1 = False
            self._ext_2 = False
            self._missing = (0.0, 0.0, 0.0, 100.0)
            self._fillareastyle = 'solid'
            self._fillareaindices = [1, ]
            self._fillareaopacity = []
            self._fillareacolors = None
            self._fillareapixelspacing = None
            self._fillareapixelscale = None
            self._levels = ([1.e20, 1.e20])
            self._level_1 = 1.e20
            self._level_2 = 1.e20
            self._color_1 = 0
            self._color_2 = 255
            self._boxfill_type = "linear"
            self._datawc_timeunits = 'days since 2000'
            self._datawc_calendar = cdtime.DefaultCalendar
            self._legend = None
            self._colormap = None
        else:
            src = vcs.elements["boxfill"][Gfb_name_src]
            self._projection = src.projection
            self._xticlabels1 = src.xticlabels1
            self._xticlabels2 = src.xticlabels2
            self._xmtics1 = src.xmtics1
            self._xmtics2 = src.xmtics2
            self._yticlabels1 = src.yticlabels1
            self._yticlabels2 = src.yticlabels2
            self._ymtics1 = src.ymtics1
            self._ymtics2 = src.ymtics2
            self._datawc_y1 = src.datawc_y1
            self._datawc_y2 = src.datawc_y2
            self._datawc_x1 = src.datawc_x1
            self._datawc_x2 = src.datawc_x2
        # End Core Graphics Method attributes
            self._xaxisconvert = src.xaxisconvert
            self._yaxisconvert = src.yaxisconvert
            self._ext_1 = src.ext_1
            self._ext_2 = src.ext_2
            self._missing = src.missing
            self._fillareastyle = src.fillareastyle
            self._fillareaindices = src.fillareaindices
            self._fillareacolors = src.fillareacolors
            self._fillareaopacity = src.fillareaopacity
            self._fillareapixelspacing = src.fillareapixelspacing
            self._fillareapixelscale = src.fillareapixelscale
            self._levels = src.levels
            self._level_1 = src.level_1
            self._level_2 = src.level_2
            self._color_1 = src.color_1
            self._color_2 = src.color_2
            self._boxfill_type = src.boxfill_type
            self._datawc_timeunits = src.datawc_timeunits
            self._datawc_calendar = src.datawc_calendar
            self._legend = src.legend
            self._colormap = src.colormap
        vcs.elements["boxfill"][Gfb_name] = self

    ###########################################################################
    #                                                                         #
    # Set boxfill attributes.                                                 #
    #                                                                         #
    ###########################################################################

    def _getcalendar(self):
        return self._datawc_calendar

    def _setcalendar(self, value):
        value = VCS_validation_functions.checkCalendar(
            self,
            'datawc_calendar',
            value)
        self._datawc_calendar = value
    datawc_calendar = property(_getcalendar, _setcalendar)

    def _gettimeunits(self):
        return self._datawc_timeunits

    def _settimeunits(self, value):
        value = VCS_validation_functions.checkTimeUnits(
            self,
            'datawc_timeunits',
            value)
        self._datawc_timeunits = value
    datawc_timeunits = property(_gettimeunits, _settimeunits)

    def _getboxfilltype(self):
        return self._boxfill_type

    def _setboxfilltype(self, value):
        value = VCS_validation_functions.checkBoxfillType(
            self,
            'boxfill_type',
            value)
        self._boxfill_type = value
    boxfill_type = property(_getboxfilltype, _setboxfilltype)

    def _getlevel_1(self):
        return self._level_1

    def _setlevel_1(self, value):
        value = VCS_validation_functions.checkIntFloat(self, 'level_1', value)
        self._level_1 = value
    level_1 = property(_getlevel_1, _setlevel_1)

    def _getlevel_2(self):
        return self._level_2

    def _setlevel_2(self, value):
        value = VCS_validation_functions.checkIntFloat(self, 'level_2', value)
        self._level_2 = value
    level_2 = property(_getlevel_2, _setlevel_2)

    def _getcolor_1(self):
        return self._color_1

    def _setcolor_1(self, value):
        value = VCS_validation_functions.checkColor(self, 'color_1', value)
        self._color_1 = value
    color_1 = property(_getcolor_1, _setcolor_1)

    def _getcolor_2(self):
        return self._color_2

    def _setcolor_2(self, value):
        value = VCS_validation_functions.checkColor(self, 'color_2', value)
        self._color_2 = value
    color_2 = property(_getcolor_2, _setcolor_2)

    levels = VCS_validation_functions.levels

    fillareacolors = VCS_validation_functions.fillareacolors

    def _getfillareaindices(self):
        return self._fillareaindices

    def _setfillareaindices(self, value):
        if value is not None:
            value = VCS_validation_functions.checkIndicesList(
                self,
                'fillareaindices',
                value)
            self._fillareaindices = value
    fillareaindices = property(_getfillareaindices, _setfillareaindices)

    def _getfillareastyle(self):
        return self._fillareastyle

    def _setfillareastyle(self, value):
        value = VCS_validation_functions.checkFillAreaStyle(
            self,
            'fillareastyle',
            value)
        self._fillareastyle = value
    fillareastyle = property(_getfillareastyle, _setfillareastyle)

    fillareaopacity = VCS_validation_functions.fillareaopacity
    fillareapixelspacing = VCS_validation_functions.fillareapixelspacing
    fillareapixelscale = VCS_validation_functions.fillareapixelscale

    ext_1 = VCS_validation_functions.ext_1
    ext_2 = VCS_validation_functions.ext_2

    def _getmissing(self):
        return self._missing

    def _setmissing(self, value):
        value = VCS_validation_functions.checkColor(self, 'missing', value)
        self._missing = value
    missing = property(_getmissing, _setmissing)

    legend = VCS_validation_functions.legend

    def _getname(self):
        return self._name

    def _setname(self, value):
        value = VCS_validation_functions.checkname(self, 'name', value)
        if value is not None:
            self._name = value
    name = property(_getname, _setname)

    def _getxaxisconvert(self):
        return self._xaxisconvert

    def _setxaxisconvert(self, value):
        value = VCS_validation_functions.checkAxisConvert(
            self,
            'xaxisconvert',
            value)
        self._xaxisconvert = value
    xaxisconvert = property(_getxaxisconvert, _setxaxisconvert)

    def _getyaxisconvert(self):
        return self._yaxisconvert

    def _setyaxisconvert(self, value):
        value = VCS_validation_functions.checkAxisConvert(
            self,
            'yaxisconvert',
            value)
        self._yaxisconvert = value
    yaxisconvert = property(_getyaxisconvert, _setyaxisconvert)

    projection = VCS_validation_functions.projection

    def _getxticlabels1(self):
        return self._xticlabels1

    def _setxticlabels1(self, value):
        value = VCS_validation_functions.checkTicks(self, 'xticlabels1', value)
        self._xticlabels1 = value
    xticlabels1 = property(_getxticlabels1, _setxticlabels1)

    def _getxticlabels2(self):
        return self._xticlabels2

    def _setxticlabels2(self, value):
        value = VCS_validation_functions.checkTicks(self, 'xticlabels2', value)
        self._xticlabels2 = value
    xticlabels2 = property(_getxticlabels2, _setxticlabels2)

    def _getyticlabels1(self):
        return self._yticlabels1

    def _setyticlabels1(self, value):
        value = VCS_validation_functions.checkTicks(self, 'yticlabels1', value)
        self._yticlabels1 = value
    yticlabels1 = property(_getyticlabels1, _setyticlabels1)

    def _getyticlabels2(self):
        return self._yticlabels2

    def _setyticlabels2(self, value):
        value = VCS_validation_functions.checkTicks(self, 'yticlabels2', value)
        self._yticlabels2 = value
    yticlabels2 = property(_getyticlabels2, _setyticlabels2)

    def _getxmtics1(self):
        return self._xmtics1

    def _setxmtics1(self, value):
        value = VCS_validation_functions.checkTicks(self, 'xmtics1', value)
        self._xmtics1 = value
    xmtics1 = property(_getxmtics1, _setxmtics1)

    def _getxmtics2(self):
        return self._xmtics2

    def _setxmtics2(self, value):
        value = VCS_validation_functions.checkTicks(self, 'xmtics2', value)
        self._xmtics2 = value
    xmtics2 = property(_getxmtics2, _setxmtics2)

    def _getymtics1(self):
        return self._ymtics1

    def _setymtics1(self, value):
        value = VCS_validation_functions.checkTicks(self, 'ymtics1', value)
        self._ymtics1 = value
    ymtics1 = property(_getymtics1, _setymtics1)

    def _getymtics2(self):
        return self._ymtics2

    def _setymtics2(self, value):
        value = VCS_validation_functions.checkTicks(self, 'ymtics2', value)
        self._ymtics2 = value
    ymtics2 = property(_getymtics2, _setymtics2)

    def _getdatawc_x1(self):
        return self._datawc_x1

    def _setdatawc_x1(self, value):
        VCS_validation_functions.checkDatawc(self, 'datawc_x1', value)
        self._datawc_x1 = value
    datawc_x1 = property(_getdatawc_x1, _setdatawc_x1)

    def _getdatawc_x2(self):
        return self._datawc_x2

    def _setdatawc_x2(self, value):
        VCS_validation_functions.checkDatawc(self, 'datawc_x2', value)
        self._datawc_x2 = value
    datawc_x2 = property(_getdatawc_x2, _setdatawc_x2)

    def _getdatawc_y1(self):
        return self._datawc_y1

    def _setdatawc_y1(self, value):
        VCS_validation_functions.checkDatawc(self, 'datawc_y1', value)
        self._datawc_y1 = value
    datawc_y1 = property(_getdatawc_y1, _setdatawc_y1)

    def _getdatawc_y2(self):
        return self._datawc_y2

    def _setdatawc_y2(self, value):
        VCS_validation_functions.checkDatawc(self, 'datawc_y2', value)
        self._datawc_y2 = value
    datawc_y2 = property(_getdatawc_y2, _setdatawc_y2)

    def colors(self, color1=0, color2=255):
        self.color_1 = color1
        self.color_2 = color2
    colors.__doc__ = xmldocs.colorsdoc % {"name": "boxfill", "data": "array"}

    def exts(self, ext1='n', ext2='y'):
        self.ext_1 = ext1
        self.ext_2 = ext2
    exts.__doc__ = xmldocs.extsdoc.format(name="boxfill", data="array")
#
# Doesn't make sense to inherit. This would mean more coding in C.
# I put this code back.
#

    def xticlabels(self, xtl1='', xtl2=''):
        self.xticlabels1 = xtl1
        self.xticlabels2 = xtl2
    xticlabels.__doc__ = xmldocs.xticlabelsdoc % {"name": "boxfill", "data": "f('u')"}

    def xmtics(self, xmt1='', xmt2=''):
        self.xmtics1 = xmt1
        self.xmtics2 = xmt2
    xmtics.__doc__ = xmldocs.xmticsdoc.format(name="boxfill")

    def yticlabels(self, ytl1='', ytl2=''):
        self.yticlabels1 = ytl1
        self.yticlabels2 = ytl2
    yticlabels.__doc__ = xmldocs.yticlabelsdoc % {"name": "boxfill", "data": "f('u')"}

    def ymtics(self, ymt1='', ymt2=''):
        self.ymtics1 = ymt1
        self.ymtics2 = ymt2
    ymtics.__doc__ = xmldocs.xmticsdoc.format(name="boxfill")

    def datawc(self, dsp1=1e20, dsp2=1e20, dsp3=1e20, dsp4=1e20):
        self.datawc_y1 = dsp1
        self.datawc_y2 = dsp2
        self.datawc_x1 = dsp3
        self.datawc_x2 = dsp4
    datawc.__doc__ = xmldocs.datawcdoc.format(name="boxfill")

    def xyscale(self, xat='linear', yat='linear'):
        self.xaxisconvert = xat
        self.yaxisconvert = yat
    xyscale.__doc__ = xmldocs.xyscaledoc.format(name='boxfill')

    def getlevels(self, varmin, varmax):
        """Given a minimum and a maximum, will generate levels for the boxfill
        starting at varmin and ending at varmax.

        :Example:

            .. doctest:: boxfill_getlevels

                >>> b=vcs.createboxfill()
                >>> lvls = b.getlevels(0,100) # 257 levels from 0-100
                >>> b.levels = list(lvls) # set boxfill's levels attribute

        :param varmin: The smallest number desired for the boxfill's levels
            attribute.
        :type varmin: float

        :param varmax: The largest number desired for the boxfill's levels
            attribute.
        :type varmin: float

        :return: A numpy array of 257 floats, evenly distributed from varmin to
            varmax.
        :rtype: numpy.ndarray
        """
        if self.boxfill_type == "custom":
            return self.levels

        nlev = float(self.color_2 - self.color_1 + 1)
        autolevels = False

        if numpy.allclose(self.level_1, 1.e20) or numpy.allclose(self.level_2, 1.e20):
            autolevels = True
            low_end = varmin
            high_end = varmax
        else:
            low_end = self.level_1
            high_end = self.level_2

        if self.boxfill_type == "log10":
            low_end = numpy.ma.log10(low_end)
            high_end = numpy.ma.log10(high_end)

        if autolevels:
            # Use nice values for the scale
            scale = vcs.mkscale(low_end, high_end)
            low_end = scale[0]
            high_end = scale[-1]

        dx = (high_end - low_end) / nlev

        if dx == 0:
            high_end += .00001
            return [low_end, high_end]
        float_epsilon = numpy.finfo(numpy.float32).eps
        if float_epsilon > (high_end-low_end):
            float_epsilon = numpy.finfo(numpy.float64).eps
        contourLevels = numpy.arange(low_end, high_end + float_epsilon, dx)

        return contourLevels

    def getlegendlabels(self, levels):
        if self.legend:
            return self.legend

        if numpy.allclose(self.level_1, 1.e20) or numpy.allclose(self.level_2, 1.e20):
            autolevels = True
        else:
            autolevels = False

        if len(levels) > 12:
            scale = vcs.mkscale(levels[0], levels[-1])
            if autolevels:
                return vcs.mklabels(scale)
            else:
                # Create our own scale
                dx = (self.level_2 - self.level_1) / float(len(scale) - 1)
                real_values = [self.level_1, self.level_2]
                float_epsilon = numpy.finfo(numpy.float32).eps
                levels = numpy.arange(levels[0], levels[-1] + float_epsilon, dx)
        else:
            real_values = levels

        # Need to line up the levels and the labels, so we'll massage the label positions
        max_round = 0
        for val in real_values:
            round_pos = 0
            while numpy.round(val, round_pos) != val:
                round_pos += 1
            max_round = max(max_round, round_pos)

        round_values = [numpy.round(level, round_pos) for level in levels]
        round_labels = vcs.mklabels(round_values, "list")

        return {lev: label for lev, label in zip(levels, round_labels)}

    ###########################################################################
    #                                                                         #
    # List out boxfill graphics method members (attributes).                  #
    #                                                                         #
    ###########################################################################
    def list(self):
        if (self.name == '__removed_from_VCS__'):
            raise ValueError('This instance has been removed from VCS.')
        print("---------- Boxfill (Gfb) member (attribute) listings ----------")
        print("graphics method =", self.g_name)
        print("name =", self.name)
        print("projection =", self.projection)
        print("xticlabels1 =", self.xticlabels1)
        print("xticlabels2 =", self.xticlabels2)
        print("xmtics1 =", self.xmtics1)
        print("xmtics2 =", self.xmtics2)
        print("yticlabels1 =", self.yticlabels1)
        print("yticlabels2 =", self.yticlabels2)
        print("ymtics1 = ", self.ymtics1)
        print("ymtics2 = ", self.ymtics2)
        print("datawc_x1 =", self.datawc_x1)
        print("datawc_y1 = ", self.datawc_y1)
        print("datawc_x2 = ", self.datawc_x2)
        print("datawc_y2 = ", self.datawc_y2)
        print("datawc_timeunits = ", self.datawc_timeunits)
        print("datawc_calendar = ", self.datawc_calendar)
        print("xaxisconvert = ", self.xaxisconvert)
        print("yaxisconvert = ", self.yaxisconvert)
        print("boxfill_type = ", self.boxfill_type)
        print("level_1 = ", self.level_1)
        print("level_2 = ", self.level_2)
        print("levels = ", self.levels)
        print("color_1 = ", self.color_1)
        print("color_2 = ", self.color_2)
        print("fillareacolors = ", self.fillareacolors)
        print("fillareastyle = ", self.fillareastyle)
        print("fillareaindices = ", self.fillareaindices)
        print("fillareaopacity = ", self.fillareaopacity)
        print("fillareapixelspacing = ", self.fillareapixelspacing)
        print("fillareapixelscale = ", self.fillareapixelscale)
        print("legend = ", self.legend)
        print("ext_1 = ", self.ext_1)
        print("ext_2 = ", self.ext_2)
        print("missing = ", self.missing)
    list.__doc__ = xmldocs.listdoc.format(name="boxfill", parent="")
    ###########################################################################
    #                                                                         #
    # Script out primary boxfill graphics method in VCS to a file.            #
    #                                                                         #
    ###########################################################################

    def script(self, script_filename, mode='a'):
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

            unique_name = '__Gfb__' + self.name
            fp.write("#----------Boxfill (Gfb) member (attribute) listings ----------\n")
            fp.write("gfb_list=v.listelements('boxfill')\n")
            fp.write("if ('%s' in gfb_list):\n" % self.name)
            fp.write("   %s = v.getboxfill('%s')\n" % (unique_name, self.name))
            fp.write("else:\n")
            fp.write("   %s = v.createboxfill('%s')\n" % (unique_name, self.name))
            # Common core graphics method attributes
            fp.write("%s.projection = '%s'\n" % (unique_name, self.projection))
            fp.write("%s.xticlabels1 = '%s'\n" % (unique_name, self.xticlabels1))
            fp.write("%s.xticlabels2 = '%s'\n" % (unique_name, self.xticlabels2))
            fp.write("%s.xmtics1 = '%s'\n" % (unique_name, self.xmtics1))
            fp.write("%s.xmtics2 = '%s'\n" % (unique_name, self.xmtics2))
            fp.write("%s.yticlabels1 = '%s'\n" % (unique_name, self.yticlabels1))
            fp.write("%s.yticlabels2 = '%s'\n" % (unique_name, self.yticlabels2))
            fp.write("%s.ymtics1 = '%s'\n" % (unique_name, self.ymtics1))
            fp.write("%s.ymtics2 = '%s'\n" % (unique_name, self.ymtics2))
            if isinstance(self.datawc_x1, (int, float)):
                fp.write("%s.datawc_x1 = %g\n" % (unique_name, self.datawc_x1))
            else:
                fp.write("%s.datawc_x1 = '%s'\n" % (unique_name, self.datawc_x1))
            if isinstance(self.datawc_y1, (int, float)):
                fp.write("%s.datawc_y1 = %g\n" % (unique_name, self.datawc_y1))
            else:
                fp.write("%s.datawc_y1 = '%s'\n" % (unique_name, self.datawc_y1))
            if isinstance(self.datawc_x2, (int, float)):
                fp.write("%s.datawc_x2 = %g\n" % (unique_name, self.datawc_x2))
            else:
                fp.write("%s.datawc_x2 = '%s'\n" % (unique_name, self.datawc_x2))
            if isinstance(self.datawc_y2, (int, float)):
                fp.write("%s.datawc_y2 = %g\n" % (unique_name, self.datawc_y2))
            else:
                fp.write("%s.datawc_y2 = '%s'\n" % (unique_name, self.datawc_y2))
            fp.write("%s.xaxisconvert = '%s'\n" % (unique_name, self.xaxisconvert))
            fp.write("%s.yaxisconvert = '%s'\n" % (unique_name, self.yaxisconvert))
            # Unique attribute for boxfill
            fp.write("%s.boxfill_type = '%s'\n" % (unique_name, self.boxfill_type))
            fp.write("%s.level_1 = %g\n" % (unique_name, self.level_1))
            fp.write("%s.level_2 = %g\n" % (unique_name, self.level_2))
            fp.write("%s.levels = %s\n" % (unique_name, self.levels))
            fp.write("%s.color_1 = %g\n" % (unique_name, self.color_1))
            fp.write("%s.color_2 = %g\n" % (unique_name, self.color_2))
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
    script.__doc__ = xmldocs.scriptdocs['boxfill']

###############################################################################
#        END OF FILE							      #
###############################################################################
