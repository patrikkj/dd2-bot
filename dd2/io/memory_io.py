from .helpers import _memory_io
import numpy as np


class MemoryData():
    def __init__(self, variable, process_handle, base_address):
        self.variable = variable
        self.process_handle = process_handle
        self.base_address = base_address

        self.pointer_address = None
        self.value = None
        
        self.update()
        self.read_noupdate()
    

    def update(self):
        self.pointer_address = _memory_io.find_pointer_address(self.process_handle, self.base_address, self.variable.full_offset)
        # print(f"Update MemoryData pointer addr: {hex(self.pointer_address)}")

    # Reading
    def read(self):
        self.update()
        return self.read_noupdate()

    def read_noupdate(self):
        self.value = _memory_io.read_variable(self.process_handle, self.pointer_address, dtype=self.variable.dtype)
        return self.variable.transform(self.value) if self.variable.transform else self.value

    # Writing
    def write(self, value):
        self.update()
        return self.write_noupdate(value)

    def write_noupdate(self, value):
        _value = self.variable.inv_transform(value) if self.variable.inv_transform else value
        _memory_io.write_variable(self.process_handle, self.pointer_address, _value, dtype=self.variable.dtype)


class MemoryDataBlock():
    def __init__(self, process_handle, base_address, *variables, numpify=False):
        self.process_handle = process_handle
        self.base_address = base_address
        self.variables = variables

        self.block_address = None
        self.value = None
        self.numpify = numpify

        # Verify that variables are contained by a single memory struct
        self.block_offset = self.variables[0].block_offset
        if len(set(v.block_offset for v in self.variables)) != 1:
            raise ValueError("All variables in MemoryDataBlock must point to the same memory struct.")
        self.block_offset = (0, ) + self.block_offset

    
    def update(self, process_handle=None):
        # for i in range(1, len(self.block_offset) + 1):
        #     sub_arr = self.block_offset[-i:]
        #     addr = _memory_io.find_pointer_address(self.process_handle, self.base_address, sub_arr)
        #     print(f"Offsets: {[hex(o) for o in sub_arr]}")
        #     print(f"Address: {hex(addr)}")
        process_handle = process_handle if process_handle else self.process_handle
        self.block_address = _memory_io.find_pointer_address(process_handle, self.base_address, self.block_offset)
        # print(f"Update MemoryData block addr: {hex(self.block_address)}")

    # Reading
    def read(self, *variables, numpify=None):
        numpify = numpify if numpify else self.numpify
        self.update()
        data = tuple(self.read_noupdate(v) for v in variables)
        return np.array(data) if numpify else data

    def read_all(self, numpify=None):
        return self.read(*self.variables, numpify=numpify)

    def read_noupdate(self, variable):
        return _memory_io.read_variable(self.process_handle, self.block_address + variable.final_offset, dtype=variable.dtype)

    # Writing
    def write(self, *pairs, process_handle=None):
        self.update(process_handle=process_handle)
        # print(self.block_address)
        for variable, value in pairs:
            self.write_noupdate(variable, value, process_handle=process_handle)

    def write_all(self, *values, process_handle=None):
        return self.write(*zip(self.variables, values), process_handle=process_handle)

    def write_noupdate(self, variable, value, process_handle=None):
        process_handle = process_handle if process_handle else self.process_handle
        _memory_io.write_variable(process_handle, self.block_address + variable.final_offset, value, dtype=variable.dtype)


class MemoryDataGroup():
    def __init__(self, *pointers, numpify=False):
        self.pointers = pointers
        self.numpify = numpify
    
    def read_noupdate(self):
        data = tuple(pointer.read_noupdate() for pointer in self.pointers)
        return np.array(data) if self.numpify else data

    def update(self):
        return tuple(pointer.update() for pointer in self.pointers)

    def read(self):
        data = tuple(pointer.read() for pointer in self.pointers)
        return np.array(data) if self.numpify else data

