"""
A module that define a cffi magic for IPython

import to get `%%cffi` cell magic in current namespace

See `%%cffi?` for usage.

Mostly playing with CFFI, feel free to contact me if you want to take over. 
"""

__version__ ='0.0.1'



from cffi import FFI
from random import choice
import string
import logging
log = logging.getLogger(__name__)

from IPython.core.magic import Magics, magics_class, cell_magic


@magics_class
class CFFI(Magics):

    @cell_magic
    def cffi(self, line, cell):
        """
        Put declaration on the fisrt line, implementation in second

        example:

            %%cffis int quad(int);
            int quad(int n){
                return 4*n;
            }


        inject `quad`, and `quad_ffi` in user namespace to be usable directly
        """

        ffi = FFI()

        rname = '_cffi_%s' % ''.join([choice(string.ascii_letters) for _ in range(10)])
        ffi.cdef(line)
        ffi.set_source(rname, cell)
        ffi.compile()
        mod = __import__(rname)
        for attr in dir(mod.lib):
            self.shell.user_ns[attr] = getattr(mod.lib, attr)
            self.shell.user_ns['%s_ffi'%attr] = mod.ffi


try:
    ip = get_ipython()
    ip.register_magics(CFFI)
except NameError:
    log.debug('Not in IPython, cffi_magic will have no effect')


example = """
%%cffi int quint(int);
int quint(int n)
{
    return 5*n;
}

# quint(9) # 45
"""
