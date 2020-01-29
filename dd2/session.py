import threading

instance=None

class Session(dict):

    #  CLIENTS / GAMECLIENTS
    # --- --- --- --- --- ---
    # 'clients'           : list of client tuples of the form [(hwnd, title), ... ]
    #                                         client_2 : gameclient_hwnd_2, ... }
    # 'client_hwnds'      : list of window handles for detected game clients
    # 'client_count'      : number of detected game clients
    # 'client_active'     : (launcher_hwnd, window_title)


    #    GAME
    # --- --- --- 
    # 'state'             : One of the states listed in 'state.py'
    # 'wave'              : Tuple of the form (current, total) or None


    #      CHARACTERS
    # --- --- --- --- --- ---
    # 'characters'        : dict of the form {"hwnd_1" : [char1, char2, ... ], 
    #                                        "hwnd_2" : [char1, char2, ... ], ... }
    #                       IMPLEMENT LATER



    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- 
    #                               METHODS                                   
    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- 
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
    
    def __setitem__(self, key, value):
        '''Implements thread-safe writing to session'''
        with self.lock:
            return super().__setitem__(key, value)

    def set(self, key, value):
        print(f"Setting {key} to: {value}")
        return self.__setitem__(key, value)

    def display(self):
        nested_print(self)


def get():
    global instance
    if instance is None:
        instance = Session()
    return instance

def traverse_dict(iterable, sep=': ', level=0):
    if isinstance(iterable, dict):
        iterable = iterable.items()

    for tup in iterable:
        # If its a single element, treat it 
        # as an empty key with a value
        if not isinstance(tup, tuple):
            tup = "", tup
            sep = ""

        for cls, symbols in ((dict, "{}"), (list, "[]")):
            if isinstance(tup[1], cls):
                yield tup[0], symbols[0], sep, level 
                yield from traverse_dict(tup[1], level=level+1)
                yield "", symbols[1], "", level
                break
        else:
            yield tup[0], tup[1], sep, level   

def nested_print(dict_, indent=4, sep=": "):
    print("{")
    for k, v, sep, level in traverse_dict(dict_, sep=sep, level=1):
        k = f'"{k}"' if k and isinstance(k, str) else k
        v = f'"{v}"' if v and isinstance(v, str) and v not in "{[]}" else v
        print(f'{level*indent*" "}{k}{sep}{v}')
    print("}")