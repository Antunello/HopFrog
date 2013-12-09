import numpy as np
class T(tuple):

    def __add__(self, other):
        if len(self) != len(other):
            return NotImplemented
        else:
            return T(tuple(x+y for x, y in zip(self, other)))

    def __sub__(self, other):
        if len(self) != len(other):
            return NotImplemented
        else:
            return T(tuple(x-y for x, y in zip(self, other)))

    def __mul__(self, other):
        if len(self) != len(other):
            return NotImplemented
        else:
            return T(tuple(x*y for x, y in zip(self, other)))
    
    # comparisons
    def __lt__(self, other):
        a = np.array(self)
        b = np.array(other)
        return (a < b).all()

    def __le__(self, other):
        a = np.array(self)
        b = np.array(other)
        return (a <= b).all()

    def __gt__(self, other):
        a = np.array(self)
        b = np.array(other)
        return (a > b).all()

    def __ge__(self, other):
        a = np.array(self)
        b = np.array(other)
        return (a >= b).all()

    def __eq__(self, other):
        a = np.array(self)
        b = np.array(other)
        return (a == b).all()

    def __ne__(self, other):
        a = np.array(self)
        b = np.array(other)
        return (a != b).all()

if __name__ == "__main__":
    a = T((1, 0))
    b = T((3, 2))
    c = T((3, 0))
    print "a =", a, ", b =", b, ", c =", c
    print "a + b =", a+b
    print "a - b =", a-b
    print "a * b =", a*b
    print "a < b -->", a<b
    print "a <= c ->", a<=c
    print "c >= b ->", c>=b
    print "(1, 0) == (1, 0)", T((1, 0)) == T((1, 0))
    print "(1, 0) != (0, 1)", T((1, 0)) != T((0, 1))
    print "(1, 0)*2 :", T((1, 0))*2
