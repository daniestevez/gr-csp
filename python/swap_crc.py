#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to <http://unlicense.org>
# 

import numpy
from gnuradio import gr

import pmt
import array

import csp_header

class swap_crc(gr.basic_block):
    """
    docstring for block swap_crc
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="swap_crc",
            in_sig=[],
            out_sig=[])

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('out'))

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return
        packet = array.array("B", pmt.u8vector_elements(msg))
        try:
            header = csp_header.CSP(packet[:4])
        except ValueError as e:
            return
        if not header.crc:
            self.message_port_pub(pmt.intern('ok'), msg_pmt)
        else:
            if len(packet) < 8: # bytes CSP header, 4 bytes CRC-32C
                # malformed
                return
            crc = packet[-4:]
            crc.reverse()
            packet = packet[:-4] + crc
            msg_pmt = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(packet), bytearray(packet)))
            self.message_port_pub(pmt.intern('out'), msg_pmt)

