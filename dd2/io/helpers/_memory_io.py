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

WriteProcessMemory = k32.WriteProcessMemory
WriteProcessMemory.argtypes = [w.HANDLE, w.LPCVOID, w.LPVOID, c.c_size_t, c.POINTER(c.c_size_t)]
WriteProcessMemory.restype = w.BOOL

GetLastError = k32.GetLastError
GetLastError.argtypes = None
GetLastError.restype = w.DWORD

CloseHandle = k32.CloseHandle
CloseHandle.argtypes = [w.HANDLE]
CloseHandle.restype = w.BOOL

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_CREATE_PROCESS = 0x0080
PROCESS_CREATE_THREAD = 0x0002
PROCESS_DUP_HANDLE = 0x0040
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_SET_INFORMATION = 0x0200
PROCESS_SET_QUOTA = 0x0100
PROCESS_SUSPEND_RESUME = 0x0800
PROCESS_TERMINATE = 0x0001
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020

# Process handles
def create_process_handle(pid, access):
    return OpenProcess(access, False, pid)

def close_process_handle(process_handle):
    return CloseHandle(process_handle)

def get_process_info(hwnd):
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    try:
        process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        base_address = win32process.EnumProcessModules(process_handle)[0]
    except Exception as e:
        print(f"Make sure the script is started with administrator privileges.")
    CloseHandle(process_handle)
    return pid, base_address


# Pointers
def find_pointer_address(process_handle, base_address, offsets):
    # print(f"Finding ptr: {hex(base_address)}")
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


# Writing
def write_variable(process_handle, address, data, dtype='f'):
    if dtype == 'f':
        data = c.c_float(data)
    elif dtype == 'i':
        data = c.c_uint(data)
    elif dtype == 'h':
        data = c.c_uint(data)

    bytes_written = c.c_ulonglong()
    result = WriteProcessMemory(
        process_handle,         # hProcess                  A handle to the process with memory that is being written to.
        address,                # lpBaseAddress             A pointer to the base address in the specified process to which data is written.
        c.byref(data),          # lpBuffer                  A pointer to the buffer that contains data to be written in the address space of the specified process.
        c.sizeof(data),         # nSize                     The number of bytes to be written to the specified process.
        c.byref(bytes_written)  # lpNumberOfBytesWritten   A pointer to a variable that receives the number of bytes transferred into the specified process.
    )
    # print(f"Written '{data}' to {hex(address)} successfully ({int.from_bytes(bytes_written, 'little')} bytes).")
    return data.value


def main():
    from dd2.io.helpers import _win_io
    identifier = "Dungeon Defenders 2"
    windows = sorted(_win_io.get_windows(filter_=lambda title: identifier in title))
    main_hwnd = windows[0][0] 

    pid, base_address = get_process_info(main_hwnd)
    process_handle = create_process_handle(pid, PROCESS_ALL_ACCESS)

    # Find pointer address
    # offsets = [0x600, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738]
    offsets = [0x19C, 0xA4, 0x0, 0x015C5750]
    address = find_pointer_address(process_handle, base_address, offsets)
    print(hex(address))

    # read data
    try:
        for _ in range(1000000):
            read_variable(process_handle, address, dtype='f')
            # print(read_variable(process_handle, address, dtype='f'))
            # time.sleep(0.01)
    finally:
        CloseHandle(process_handle)

    print("Finished")
    # Write data
    # write_variable(process_handle, address, 0.5)

if __name__ == "__main__":
    main()
