#//----------------------------------------------------------------------
#//   Copyright 2019-2020 Tuomas Poikela (tpoikela)
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
#//----------------------------------------------------------------------

"""
Contains SystemVerilog (SV) system functions mocked/added
to make the porting SV to Python faster.

"""

import re
import random
import cocotb
#from cocotb_coverage.coverage import *
from cocotb_coverage import crv
from cocotb.triggers import Lock, Timer, Combine, First
from cocotb.utils import get_sim_time, simulator
from cocotb.bus import Bus
from inspect import getframeinfo, stack

# from constraint import Problem

RET_ERR = 1
RET_OK = 0


def uvm_re_match(rex, _str):
    m = re.search(rex, _str)
    if m is not None:
        return RET_OK
    return RET_ERR


def uvm_glob_to_re(_str):
    """
    Converts a glob-style pattern to Python
    regular expression syntax.

    Returns:
        str: Glob converted to regular expression syntax.
    """
    if _str is None or _str == "":
        return ""
    if _str[0] == "/" and _str[-1] == "/":
        return _str
    # TODO replace * with .*
    res = _str.replace('.', '\\.')
    res = res.replace('*', '.*')
    res = res.replace('[', '\\[')
    res = res.replace(']', '\\]')
    res = res.replace('?', '.')
    # TODO add more substitutions
    return res


def uvm_split_string(_str, sep, split_vals):
    res = _str.split(sep)
    for val in res:
        split_vals.append(val)
    return res


class process():

    FINISHED = 0
    RUNNING = 1
    WAITING = 2
    SUSPENDED = 3
    KILLED = 4

    def __init__(self):
        self.status = process.RUNNING
        self.pid = -1


class sv:
    """ Namespace for SV functions """

    @classmethod
    def clog2(cls, value):
        value = value - 1
        res = 0
        while value > 0:
            value = value >> 1
            res += 1
        return res

    @classmethod
    def display(cls, msg, *args):
        form_msg = sv.sformatf(msg, *args)
        print(form_msg)

    @classmethod
    def realtime(cls, unit=None):
        if simulator is None:
            return 0
        elif unit is None:
            return get_sim_time()
        else:
            return get_sim_time(unit)

    @classmethod
    def time(cls, unit=None):
        return cls.realtime(unit)

    @classmethod
    def fwrite(cls, fhandle, msg):
        if hasattr(fhandle, 'write'):
            fhandle.write(msg)
        else:
            print(msg)

    @classmethod
    def isunknown(cls, value):
        # TODO implement this properly
        return False

    @classmethod
    def bits(cls, var):
        if isinstance(var, int):
            return 32
        return 0

    @classmethod
    def fopen(cls, name, mode):
        return open(name, mode)

    @classmethod
    def fclose(cls, handle):
        handle.close()

    @classmethod
    def fdisplay(cls, fhandle, msg, *args):
        form_msg = sv.sformatf(msg, *args)
        form_msg += "\n"  # SV fdisplay behavior
        if fhandle != 0:
            if fhandle != 1:
                fhandle.write(form_msg)
            else:
                print(form_msg)

    @classmethod
    def cast(cls, dest, src, T):
        if isinstance(src, T):
            if hasattr(dest, 'append'):
                dest.append(src)
            return True
        return False

    STR_RE = re.compile(r'%(\d*[bdshxfpt])')
    formats = ["%b", "%0b", "%0d", "%d", "%s", "%0s", "%h", "%0h", "%f",
            "%p", "%0t", "%t", "%x"]

    @classmethod
    def sformatf(cls, msg, *args):
        """         
        This is to make porting faster, but should be switched to native python
        formatting inside UVM code
        Args:
            msg: String to format containing format specifiers.
            args: Values that are used in formatting.
        Returns:
            str: Formatted string
        """
        #formats = {"%t": "%d", "%0t": "%0d"}
        #for s in formats:
        #    msg = msg.replace(s, formats[s])
        #return sformatf(msg, *args)
        # TODO substitute old types %s/%d etc with {}
        #new_msg = cls.STR_RE.sub(r'{:\1}', msg)
        #print("new_msg is " + new_msg)
        for s in cls.formats:
            if s == "%h" or s == "%0h":
                msg = msg.replace(s, "{:X}")
            else:
                msg = msg.replace(s, "{}")
        return msg.format(*args)

    @classmethod
    def random(cls):
        return random.randint(0, SV_MAX_INT_VALUE)

    @classmethod
    def urandom(cls):
        return random.randint(0, SV_MAX_INT_VALUE)

    @classmethod
    def urandom_range(cls, start, stop):
        return random.randint(start, stop)

    @classmethod
    def sv_assert(cls, val, msg=""):
        if not val:
            caller = getframeinfo(stack()[1][0])
            filename = caller.filename
            line = caller.lineno
            print("$error: {},{} Assertion failed. {}".format(filename, line, msg))

    @classmethod
    def value_plusargs(cls, arg_str, arr):
        plusarg_dict = cocotb.plusargs
        for name in plusarg_dict:
            full_arg = name + '='
            for i in range(len(full_arg)):
                if full_arg[i] != arg_str[i]:
                    break
                elif i == len(full_arg) - 1:
                    arr.append(plusarg_dict[name])
                    return plusarg_dict[name]

    @classmethod
    async def fork_join(cls, forks):
        join_list = list(map(lambda t: t.join(), forks))
        await Combine(*join_list)

    @classmethod
    async def fork_join_any(cls, forks):
        join_list = list(map(lambda t: t.join(), forks))
        await First(*join_list)

    @classmethod
    async def fork_join_none(cls, procs):
        res = []
        for proc in procs:
            res.append(cocotb.fork(proc))
        return res


random.seed(0)

SV_MAX_INT_VALUE = (1 << 31) - 1


class sv_obj(crv.Randomized):
    """ sv_obj implement some basic features from SystemVerilog objects like
    constrained randomisation """

    def __init__(self):
        crv.Randomized.__init__(self)
        self._sv_seed = sv.urandom()
        self._sv_rand_obj = []
        random.seed(self._sv_seed)
        self._sv_rand_state = random.getstate()

    def constraint(self, c):
        """ Adds a constraint into the object """
        self.add_constraint(c)


    def rand(self, key, val_list=None):
        """
        Mark given class property as randomized. A call to `sv_obj.randomize()`
        will then randomize this value.

        Args:
            key (str): Name of the property.
            val_list (list|range): Optional constraints for randomisation.
        """
        if hasattr(key, "randomize"):
            if val_list is None:
                self._sv_rand_obj.append(key)
        elif hasattr(self, key) and val_list is None:
            self._sv_rand_obj.append(key)
        else:
            self.add_rand(key, val_list)


    def randomize(self, recurse=True):
        """ 
        Randomizes values in object marked with rand(). Recurses to sub-objects
        randomizing them as well.
        """
        try:
            ok = True
            if recurse:
                for entry in self._sv_rand_obj:
                    obj = entry
                    if hasattr(self, entry):
                        obj = getattr(self, entry)
                    ok = ok and obj.randomize()
            super().randomize()
            return True and ok
        except:
            # TODO this can mask all sorts of errors
            return False


    def randomize_with(self, *constr):
        try:
            ok = True
            for entry in self._sv_rand_obj:
                obj = entry
                if hasattr(self, entry):
                    obj = getattr(self, entry)
                ok = ok and obj.randomize()
            super().randomize_with(*constr)
            return True and ok
        except:
            # TODO this can mask all sorts of errors
            return False


class semaphore():

    def __init__(self, count=1):
        self.max_count = count
        self.count = count
        self.lock = Lock("sem_lock")
        self.locked = False

    
    async def get(self, count=1):
        if self.count > count:
            self.count -= count
            await Timer(0, "NS")
        elif count > self.max_count:
            raise Exception("Tried to get {} > max count {}".format(count,
                self.max_count))
        else:
            await self.lock.acquire()
            self.locked = True
            self.count -= count

    def put(self, count=1):
        if self.count < self.max_count:
            self.count += count
            if self.locked is True:
                self.locked = False
                self.lock.release()

    def try_get(self, count=1):
        if self.count >= count:
            self.count -= count
            return True
        return False


class sv_if(Bus):

    def __init__(self, entity, name, signals,
            optional_signals=[], bus_separator="_", array_idx=None):
        Bus.__init__(self, entity, name, signals, optional_signals,
                bus_separator, array_idx)


def sformatf(fmt, *args):
    return fmt % args


def cat(*args):
    ret = ""
    for a in args:
        ret += a

    return ret



async def wait(cond, ev):
    if not callable(cond):
        raise Exception("wait expects the first arguments to be callable")

    while True:
        if cond():
            break
        else:
            await ev.wait()
            ev.clear()
