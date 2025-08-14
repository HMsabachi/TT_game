import ctypes

lchcrypt = ctypes.WinDLL('lchcrypt_py//lchcrypt.dll')

encrypt_lch = lchcrypt.encrypt_block_lch
encrypt_lch.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_char * 16]
encrypt_lch.restype = ctypes.c_uint64

decrypt_lch = lchcrypt.decrypt_block_lch
decrypt_lch.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_char * 16]
decrypt_lch.restype = ctypes.c_uint64

def encrypt(data, key):
    data = b"\x00"*(8-len(data)%8) + data
    blocks = [int.from_bytes(data[i:i+8]) for i in range(0, len(data), 8)]
    key = (ctypes.c_char * 16)(*key)
    output = b""
    for block in blocks:
        block_ptr = ctypes.pointer(ctypes.c_uint64(block))
        encrypted = encrypt_lch(block_ptr, key)
        output += bytes.fromhex(hex(encrypted)[2:].zfill(16))
    return output

def decrypt(data, key):
    blocks = [int.from_bytes(data[i:i+8]) for i in range(0, len(data), 8)]
    key = (ctypes.c_char * 16)(*key)
    output = b""
    for block in blocks:
        block_ptr = ctypes.pointer(ctypes.c_uint64(block))
        decrypted = decrypt_lch(block_ptr, key)
        output += bytes.fromhex(hex(decrypted)[2:].zfill(16))
    return output

key = b"lch08"
data = b"0123456789abcdefg"
output = encrypt(data,key)
print(output)
output = decrypt(output,key)
print(output)
