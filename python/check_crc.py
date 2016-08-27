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
import struct

import crc32c
import csp_header

class check_crc(gr.basic_block):
    """
    docstring for block check_crc
    """
    def __init__(self, include_header, verbose):
        gr.basic_block.__init__(self,
            name="check_crc",
            in_sig=[],
            out_sig=[])

        self.include_header = include_header
        self.verbose = verbose
        
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('ok'))
        self.message_port_register_out(pmt.intern('fail'))

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return
        packet = array.array("B", pmt.u8vector_elements(msg))
        try:
            header = csp_header.CSP(packet[:4])
        except ValueError as e:
            if self.verbose:
                print e
            return
        if not header.crc:
            if self.verbose:
                print "CRC not used"
            self.message_port_pub(pmt.intern('ok'), msg_pmt)
        else:
            if len(packet) < 8: # bytes CSP header, 4 bytes CRC-32C
                if self.verbose:
                    print "Malformed CSP packet (too short)"
                return
            crc = crc32c.crc(packet[:-4] if self.include_header else packet[4:-4])
            packet_crc = struct.unpack(">I", packet[-4:])[0]
            if crc == packet_crc:
                if self.verbose:
                    print "CRC OK"
                self.message_port_pub(pmt.intern('ok'), msg_pmt)
            else:
                if self.verbose:
                    print "CRC failed"
                self.message_port_pub(pmt.intern('fail'), msg_pmt)
