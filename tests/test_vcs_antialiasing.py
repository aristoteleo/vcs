import unittest
import vcs


class TestVCSAntialias(unittest.TestCase):

    def testAntiAliasing(self):
        x = vcs.init()
        # Calling `open` creates the vtkRenderWindow and calls `Render`. This call will evaulate the systems
        # capabilities and set antialiasing to the requested value as long as its less than or equal the maximum
        # value supported by the system. A scenario exists where vcs will set the initial value to 8 and
        # the system isn't capable of this and the first call to getantialiasing after open will result in
        # 0 being returned.
        # x.open()

        # test it is on by default
        self.assertEqual(x.getantialiasing(), 8)

        # test we can set it
        x.setantialiasing(3)
        self.assertEqual(x.getantialiasing(), 3)
        # test we can set it off
        x.setantialiasing(0)
        self.assertEqual(x.getantialiasing(), 0)
