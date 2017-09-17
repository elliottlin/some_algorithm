try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

def custom_hash(key):
    result = 5381
    multiplier = 33

    if isinstance(key, int):
        return key
    
    for char in key:
        result = 33 * result + ord(char)
        
    return result
class HashMap():
    
    def __init__(self, size = 128, hash_func = custom_hash ):
        self._size = size
        self._init_size = self._size
        self._used_slots = 0
        self._dummy_slots = 0
        self._max_threshold = 0.60
        
        self._hash = hash_func
        
        # Holds all the keys
        self._keys = [None] * self._size
        
        # Holds all the values
        self._values = [None] * self._size
        
       
    ########## public ############# 
    def put(self,key, value):
        """
            Given a key and value, add it to the hash table.
            Key should be int or string or unicode.
        """
        self._raise_if_not_acceptable_key(key)
        
        """
            Check status before put.
        """
        self._check_table_status()
        
        """
            add or update returns a position with 2 conditions
                1. position match the key
                2. an empty position for new adding/ not found
        """
        position = self._add_or_update(key)
        
        """
            Once, get the legal/valid position,
            put value into it.
        """
        self._set_item_at_pos(position, key, value)
        
    def get(self, key):
        """
            Given a key and value, add it to the hash table.
            Key should be int or string or unicode.
        """
        self._raise_if_not_acceptable_key(key)
        
        """
            add or update returns a position with 2 conditions
                1. position match the key
                2. an empty position for new adding/ not found
        """
        position = self._get_position_or_not_found(key)
        
        if position is None:
            raise KeyError(key)
        else:
            return self._values[position]

    def delete(self, key):
        """
            Deletes the key if present.
            KeyError is raised if key is missing.
        """
        self._raise_if_not_acceptable_key(key)
        position = self._get_position_or_not_found(key)
        
        if position is None:
            raise KeyError(key)
        else:
            self._delete_item(position)

    ########## private #############
    
    def _add_or_update(self, key):
        position, status = self._check_and_return_valid_key_pos(key)
        
        if status == "FOUND":
            return position
        elif status == "EMPTY":
            # add, return a valid position for adding
            return position
        else:
            return None
        
    def _get_position_or_not_found(self, key):
        position, status = self._check_and_return_valid_key_pos(key)
        
        if status == "FOUND":
            return position
        elif status == "EMPTY":
            return None
        else:
            return None
            
    
    def _check_and_return_valid_key_pos(self, key):
        """
            The status can be used for
                1. postion for creating new one/ missed searching
                2. postion that matches the key
        """
        
        # hash first
        hash_key = self._hash(key)
        
        # calculate index in memory
        position = self._calculate_position(hash_key)
        
        # search position of valid key
        (position, status) = self._search_probed_key(key, position)
        
        return (position, status)
    
    
    def _search_probed_key(self, key, position):
        """
            Check key equals to the key at position( keys[position] )
            Otherwise, probe to next
        """
        if self._keys[position] == key:
            return (position, "FOUND")
        elif self._keys[position] is None:
            # end of search 
            return (position, "EMPTY")
        else:
            # probe next
            probed_position = self._probing(position)
            return self._search_probed_key(key, probed_position)
    
    def _probing(self, current_position):
        # Algorithm is copied from CPython http://hg.python.org/cpython/file/52f68c95e025/Objects/dictobject.c#l69
        return ((5+current_position)+1) % self._size
    
    def _check_table_status(self):
        if self._shoud_expand():
            self._resize()
        else:
            pass

    def _shoud_expand(self):
        return (float(self._used_slots + self._dummy_slots)/self._size) >= self._max_threshold
    
    def _resize(self):
        old_keys = self._keys
        old_values = self._values
        
        # new size
        self._size = self._size * 2 + 1
        
        # create new block of memory and clean up old  keys position
        self._keys = [None] * self._size
        self._values = [None] * self._size
        self._used_slots = 0
        self._dummy_slots = 0
        
        self._reposition(old_keys, old_values)
    
    def _set_item_at_pos(self, pos, key, value):
        self._keys[pos] = key
        self._values[pos] = value
        self._used_slots += 1
        
    def _delete_item(self, position):
        self._keys[position] = None
        self._values[position] = None
        
        self._dummy_slots += 1
                    
    def _calculate_position(self, hashvalue):
        return hashvalue % self._size
    
    def _reposition(self, keys, values):
        """
            Reposition all the keys and values.
            This is called whenever load factor or threshold has crossed the limit.
        """
        for (key, value) in zip(keys, values):
            if key is not None:
                position, status = self._check_and_return_valid_key_pos(key)

                if status == "EMPTY":
                    self._set_item_at_pos(position, key, value)

    def _raise_if_not_acceptable_key(self, key):
        if not isinstance(key, (basestring, int)):
            raise TypeError("Key should be int or string or unicode")