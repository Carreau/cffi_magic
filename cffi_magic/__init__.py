"""
A module that define a cffi magic for IPython

import to get `%%cffi` cell magic in current namespace

See `%%cffi?` for usage.

Mostly playing with CFFI, feel free to contact me if you want to take over. 
"""

from __future__ import print_function

import re
from cffi import FFI
from random import choice
import string
import logging
import subprocess

from IPython.core.magic import Magics, magics_class, cell_magic

import io
import os

__version__ ='0.0.6'
log = logging.getLogger(__name__)


cargotoml="""
[package]

name = "{name}"
version = "0.0.1"
authors = ["No-one InParticular <nobody@example.com>"]

[lib]
name = "{name}"
crate-type = ["dylib"]

[dependencies]

libc = "0.1"
"""

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
            self.shell.user_ns['%s_ffi' % attr] = mod.ffi

    @cell_magic
    def rust(self, line, cell):
        """
        Rust cffi magic, declaration on first line, rust on the rest. 

        Example:

        ```
            %%rust int calculate(const char *script);

            #![allow(dead_code)]

            extern crate libc;

            use libc::c_char;
            use std::ffi::CStr;
            use std::str;

            // {{{ fn calculate(c_buf: *const c_char) -> i32 {...}
            #[no_mangle]
            pub extern fn calculate(c_buf: *const c_char) -> i32 {
                let buf = unsafe { CStr::from_ptr(c_buf).to_bytes() };
                let slice = str::from_utf8(buf).unwrap();
                calc(slice)
            } // }}}

            fn calc(script: &str) -> i32 {
                let mut accumulator = 0;

                for c in script.chars() {
                    match c {
                        '+' => accumulator += 1,
                        '-' => accumulator -= 1,
                        '*' => accumulator *= 2,
                        '/' => accumulator /= 2,
                        _ => { /* ignore other characters */ }
                    }
                }

                accumulator
            }
        ```
        
        you can now 
        ```
        calculate('+ + + * - /')
        # 2
        ```

        Exmaple 2:

        ```
        %%rust int double(int);

        #[no_mangle]
        pub extern fn double(x: i32) -> i32 {
            x*2
        }

        ```

        now 
        ```
        double(3)  # return 6
        ```
        """
        ffi = FFI()

        rname = '_cffi_%s' % ''.join([choice(string.ascii_letters) for _ in range(10)])
        with io.open('Cargo.toml','wb') as f:
            f.write(cargotoml.format(name=rname).encode('utf-8'))
        try:
            os.mkdir('src')
        except OSError:
            pass
        with io.open('src/lib.rs', 'wb') as f:
            f.write(cell.encode())
        subprocess.call(["cargo", "build",'--release'])
        ffi.cdef(line)
        mod = ffi.dlopen("target/release/lib{name}.dylib".format(name=rname))
        exports =  re.findall('([a-zA-Z_]+)\(', line)
        for attr in exports:
            self.shell.user_ns[attr] = getattr(mod, attr)
            print("injecting `%s` in user ns" % (attr,))
            #self.shell.user_ns['%s_ffi'%attr] = mod.ffi



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
