import multiprocessing
import sys

import dd2.io as io

this = sys.modules[__name__]

# Format: 
# client -> (service, process, pipe_inlet)
this.services = {}

NEGATIVE = (-1).to_bytes(1, sys.byteorder, signed=True)
ZERO = (0).to_bytes(1, sys.byteorder, signed=True)
POSITIVE = (1).to_bytes(1, sys.byteorder, signed=True)
NOP = (-2).to_bytes(1, sys.byteorder, signed=True)
UP = RIGHT = POSITIVE
DOWN = LEFT = NEGATIVE


def create_service(client):
    pipe_endpoint, pipe_inlet = multiprocessing.Pipe()

    # Create service
    service = KeyboardService(client, pipe_endpoint)

    # Launch separate process
    process = multiprocessing.Process(target=service.run, daemon=True)
    this.services[client] = (service, process, pipe_inlet)

    # Run service
    process.start()    

def kill_service(client):
    process = this.services[client][1]
    if process.is_alive():
        process.terminate()

def set_input_vector(client, input_vector):
    _x = KeyboardService.serialize(input_vector[0])
    _y = KeyboardService.serialize(input_vector[1])
    this.services[client][2].send_bytes(_x + _y)

def set_input_x(client, input_x):
    return set_input_vector(client, (input_x, -2))

def set_input_y(client, input_y):
    return set_input_vector(client, (-2, input_y))


class KeyboardService():
    def __init__(self, client, pipe_endpoint):
        self.pipe_endpoint = pipe_endpoint
        self.client = client
        self.x, self.y = 0, 0

    def create_process_handle(self):        
        # Create process handle with full access to process memory
        pid, _ = io._memory.get_process_info(self.client.hwnd)
        return io._memory.create_process_handle(pid, io._memory.PROCESS_ALL_ACCESS)

    def run(self):
        process_handle = self.create_process_handle()
        while True:
            # Fetch if no action is assigned or there is data to fetch
            if (self.x, self.y) == (0, 0) or self.pipe_endpoint.poll():
                _x, _y = self.fetch()
                if _x != -2:
                    self.x = _x
                if _y != -2:
                    self.y = _y

            # Perform action
            self.client.input_controllers.write_all(
                self.x,
                self.y,
                process_handle=process_handle
            )


    def fetch(self):
        payload = self.pipe_endpoint.recv_bytes()
        return self.deserialize(payload[0:1]), self.deserialize(payload[1:2])

    @staticmethod
    def serialize(value):
        return (value).to_bytes(1, sys.byteorder, signed=True)

    @staticmethod
    def deserialize(bytes_):
        return int.from_bytes(bytes_, sys.byteorder, signed=True)
