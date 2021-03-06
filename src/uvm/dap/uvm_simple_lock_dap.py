#//
#//------------------------------------------------------------------------------
#//   Copyright 2007-2011 Mentor Graphics Corporation
#//   Copyright 2007-2011 Cadence Design Systems, Inc.
#//   Copyright 2010-2011 Synopsys, Inc.
#//   Copyright 2013      NVIDIA Corporation
#//   All Rights Reserved Worldwide
#//
#//   Licensed under the Apache License, Version 2.0 (the
#//   "License"); you may not use this file except in
#//   compliance with the License.  You may obtain a copy of
#//   the License at
#//
#//       http://www.apache.org/licenses/LICENSE-2.0
#//
#//   Unless required by applicable law or agreed to in
#//   writing, software distributed under the License is
#//   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#//   CONDITIONS OF ANY KIND, either express or implied.  See
#//   the License for the specific language governing
#//   permissions and limitations under the License.
#//------------------------------------------------------------------------------

from .uvm_set_get_dap_base import uvm_set_get_dap_base
from ..macros.uvm_object_defines import uvm_object_utils
from ..macros.uvm_message_defines import *
from ..base.sv import sv

ERR_MSG1 = "Attempt to set new value on '%s', but the data access policy forbids setting while locked!"

#// Class: uvm_simple_lock_dap
#// Provides a 'Simple Lock' Data Access Policy.
#//
#// The 'Simple Lock' Data Access Policy allows for any number of 'sets',
#// so long as the value is not 'locked'.  The value can be retrieved using
#// 'get' at any time.
#//
#// The UVM uses this policy to protect the ~file name~ value in the
#// <uvm_text_tr_database>.
#//
#class uvm_simple_lock_dap#(type T=int) extends uvm_set_get_dap_base#(T);

class uvm_simple_lock_dap(uvm_set_get_dap_base):
    #
    #   // Used for self-references
    #   typedef uvm_simple_lock_dap#(T) this_type;

    #   // Function: new
    #   // Constructor
    def __init__(self, name="unnamed-uvm_simple_lock_dap"):
        uvm_set_get_dap_base.__init__(self, name)
        self.m_locked = False
        self.m_value = None

    #   // Group: Set/Get Interface
    #
    #   // Function: set
    #   // Updates the value stored within the DAP.
    #   //
    #   // ~set~ will result in an error if the DAP has
    #   // been locked.
    def set(self, value):
        if (self.m_locked):
            uvm_error("UVM/SIMPLE_LOCK_DAP/SAG", sv.sformatf(ERR_MSG1, self.get_full_name()))
        else:
            self.m_value = value

    #   // Function: try_set
    #   // Attempts to update the value stored within the DAP.
    #   //
    #   // ~try_set~ will return a 1 if the value was successfully
    #   // updated, or a 0 if the value can not be updated due
    #   // to the DAP being locked.  No errors will be reported
    #   // if ~try_set~ fails.
    #   virtual function bit try_set(T value);
    #      if (m_locked)
    #        return 0;
    #      else begin
    #         m_value = value;
    #         return 1;
    #      end
    #   endfunction : try_set
    #

    #   // Function: get
    #   // Returns the current value stored within the DAP
    #   //
    def get(self):
        return self.m_value

    #   // Function: try_get
    #   // Retrieves the current value stored within the DAP
    #   //
    #   // ~try_get~ will always return 1.
    #   virtual function bit try_get(output T value);
    #      value = get();
    #      return 1;
    #   endfunction : try_get
    #

    #   // Group: Locking
    #
    #   // Function: lock
    #   // Locks the data value
    #   //
    #   // The data value cannot be updated via <set> or <try_set> while locked.
    def lock(self):
        self.m_locked = True

    #   // Function: unlock
    #   // Unlocks the data value
    #   //
    def unlock(self):
        self.m_locked = False

    #
    #   // Function: is_locked
    #   // Returns the state of the lock.
    #   //
    #   // Returns:
    #   // 1 - The value is locked
    #   // 0 - The value is unlocked
    def is_locked(self):
        return self.m_locked

    #
    #   // Group: Introspection
    #   //
    #   // The ~uvm_simple_lock_dap~ cannot support the standard UVM
    #   // instrumentation methods (~copy~, ~clone~, ~pack~ and
    #   // ~unpack~), due to the fact that they would potentially
    #   // violate the access policy.
    #   //
    #   // A call to any of these methods will result in an error.
    #   virtual function void do_copy(uvm_object rhs);
    #      `uvm_error("UVM/SIMPLE_LOCK_DAP/CPY",
    #                 "'copy()' is not supported for 'uvm_simple_lock_dap#(T)'")
    #   endfunction : do_copy

    #
    #   virtual function void do_pack(uvm_packer packer);
    #      `uvm_error("UVM/SIMPLE_LOCK_DAP/PCK",
    #                 "'pack()' is not supported for 'uvm_simple_lock_dap#(T)'")
    #   endfunction : do_pack

    #
    #   virtual function void do_unpack(uvm_packer packer);
    #      `uvm_error("UVM/SIMPLE_LOCK_DAP/UPK",
    #                 "'unpack()' is not supported for 'uvm_simple_lock_dap#(T)'")
    #   endfunction : do_unpack

    #
    #   // Group- Reporting
    #
    #   // Function- convert2string
    #   virtual function string convert2string();
    #      if (m_locked)
    #        return $sformatf("(%s) %0p [LOCKED]", `uvm_typename(m_value), m_value);
    #      else
    #        return $sformatf("(%s) %0p [UNLOCKED]", `uvm_typename(m_value), m_value);
    #   endfunction : convert2string
    #
    #   // Function- do_print
    #   virtual function void do_print(uvm_printer printer);
    #      super.do_print(printer);
    #      printer.print_int("lock_state", m_locked, $bits(m_locked));
    #      printer.print_generic("value",
    #                            `uvm_typename(m_value),
    #                            0,
    #                            $sformatf("%0p", m_value));
    #
    #   endfunction : do_print
    #
    #endclass // uvm_simple_lock_dap
#
uvm_object_utils(uvm_simple_lock_dap)
