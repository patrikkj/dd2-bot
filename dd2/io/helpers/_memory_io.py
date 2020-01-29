# import ctypes
import ctypes as c
import struct
from ctypes import wintypes as w

import win32process

k32 = c.windll.kernel32

OpenProcess = k32.OpenProcess
OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
OpenProcess.restype = w.HANDLE

ReadProcessMemory = k32.ReadProcessMemory
ReadProcessMemory.argtypes = [w.HANDLE, w.LPCVOID, w.LPVOID, c.c_size_t, c.POINTER(c.c_size_t)]
ReadProcessMemory.restype = w.BOOL

GetLastError = k32.GetLastError
GetLastError.argtypes = None
GetLastError.restype = w.DWORD

CloseHandle = k32.CloseHandle
CloseHandle.argtypes = [w.HANDLE]
CloseHandle.restype = w.BOOL
PROCESS_VM_READ = 0x0010
PROCESS_ALL_ACCESS = 0x1F0FFF


# Process handles
def create_process_handle(pid, access):
    return OpenProcess(access, False, pid)

def close_process_handle(process_handle):
    return CloseHandle(process_handle)

def get_process_info(hwnd):
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    base_address = win32process.EnumProcessModules(process_handle)[0]
    CloseHandle(process_handle)
    return pid, base_address


# Pointers
def find_pointer_address(process_handle, base_address, offsets):
    base_address += offsets[-1]
    # Base case
    if len(offsets) == 1:
        return base_address

    data = c.c_uint()
    bytes_read = c.c_ulonglong()
    result = ReadProcessMemory(
        process_handle,         # hProcess              A handle to the process with memory that is being read.
        base_address,           # lpBaseAddress         A pointer to the base address in the specified process from which to read.
        c.byref(data),          # lpBuffer              A pointer to a buffer that receives the contents from the address space of the specified process.
        c.sizeof(data),         # nSize                 The number of bytes to be read from the specified process.
        c.byref(bytes_read)     # lpNumberOfBytesRead   A pointer to a variable that receives the number of bytes transferred into the specified buffer.
    )
    next_address = data.value
    return find_pointer_address(process_handle, next_address, offsets[:-1])


# Reading
def _read_process_memory(process_handle, address, offsets=None, dtype='f', size=None):
    print(f"Called with args: ['address'={hex(address)}, 'offsets'={[hex(o) for o in offsets]}, 'dtype'={dtype}, 'size'={size}]")
    '''
    pid: Process ID
    address: base address
    offsets: Array of n offsets from base address for n-level pointer. 
    dtype: 'f' = Float, 'i' = Integer, 'h' = Hex
    size: Number of 32-bit data entries to read.
    '''
    if offsets:
        if len(offsets) > 1:
            dtype, _cached_dtype = 'h', dtype
            size, _cached_size = None, size
        address += offsets[-1]

    if dtype == 'f':
        data = c.c_float()
    elif dtype == 'i':
        data = c.c_uint()
    elif dtype == 'h':
        data = c.c_uint()
    if size:
         data = c.create_string_buffer(size*4)

    bytes_read = c.c_ulonglong()
    result = ReadProcessMemory(
        process_handle,         # hProcess              A handle to the process with memory that is being read.
        address,                # lpBaseAddress         A pointer to the base address in the specified process from which to read.
        c.byref(data),          # lpBuffer              A pointer to a buffer that receives the contents from the address space of the specified process.
        c.sizeof(data),         # nSize                 The number of bytes to be read from the specified process.
        c.byref(bytes_read)     # lpNumberOfBytesRead   A pointer to a variable that receives the number of bytes transferred into the specified buffer.
    )

    if dtype == 'f':
        result = data.value
    elif dtype == 'i':
        result = data.value
    elif dtype == 'h':
        result = data.value
    if size:
        result = struct.unpack(dtype*size, data)
    
    if len(offsets) > 1:
        next_address = result
        offsets = offsets[:-1]
        return _read_process_memory(process_handle, next_address, offsets=offsets, dtype=_cached_dtype, size=_cached_size)
    return result


def read_variable(process_handle, address, dtype='f'):
    if dtype == 'f':
        data = c.c_float()
    elif dtype == 'i':
        data = c.c_uint()
    elif dtype == 'h':
        data = c.c_uint()
    bytes_read = c.c_ulonglong()
    ReadProcessMemory(
        process_handle,         # hProcess              A handle to the process with memory that is being read.
        address,                # lpBaseAddress         A pointer to the base address in the specified process from which to read.
        c.byref(data),          # lpBuffer              A pointer to a buffer that receives the contents from the address space of the specified process.
        c.sizeof(data),         # nSize                 The number of bytes to be read from the specified process.
        c.byref(bytes_read)     # lpNumberOfBytesRead   A pointer to a variable that receives the number of bytes transferred into the specified buffer.
    )
    return data.value

def read_chunk(process_handle, address, dtype='f', size=4):
    ''' size: Number of 32-bit data entries to read. '''
    data = c.create_string_buffer(size*4)
    bytes_read = c.c_ulonglong()
    ReadProcessMemory(
        process_handle,         # hProcess              A handle to the process with memory that is being read.
        address,                # lpBaseAddress         A pointer to the base address in the specified process from which to read.
        c.byref(data),          # lpBuffer              A pointer to a buffer that receives the contents from the address space of the specified process.
        c.sizeof(data),         # nSize                 The number of bytes to be read from the specified process.
        c.byref(bytes_read)     # lpNumberOfBytesRead   A pointer to a variable that receives the number of bytes transferred into the specified buffer.
    )
    return struct.unpack(dtype*size, data)
