def sanitize_msg_param(param, num_bytes : int = 0, byteorder : str = 'big') -> bytes:
    """
    'Sanitizes' (converts to bytes) a message parameter.

    Defaults to big-endianness and whatever the size of param is.

    This function is meant for internal use in message/protocol files; it's only public because
    I didn't want to copy/paste it a bunch of times.
    """
    if isinstance(param, int): # int to bytes
        if num_bytes == 0:
            num_bytes = (param.bit_length() + 7) // 8
            if param == 0: # don't cut it off if the input is zero
                num_bytes = 1
        return param.to_bytes(num_bytes, byteorder)
    elif isinstance(param, bool):
        if param:
            return sanitize_msg_param(1, num_bytes, byteorder)
        else:
            return sanitize_msg_param(0, num_bytes, byteorder)
    elif isinstance(param, str): # string to bytes
        if param == "": # check for empty string
            return b'' + b'\x00' * num_bytes
        return sanitize_msg_param(str.encode(param, 'utf8'), num_bytes, byteorder)
    elif isinstance(param, bytes):
         # convert to int, run sanitize_msg_param again
        if num_bytes == 0:
            if param == b'': # len == 1 for b'', but we don't want to return b'\x00'
                return b''
            num_bytes = len(param)
        if byteorder == 'little':
            param2 = param[::-1]
        else:
            param2 = param
        val = int.from_bytes(param2[:num_bytes], byteorder)
        return sanitize_msg_param(val, num_bytes, byteorder)
    