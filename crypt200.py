import socket, collections, re, time, select

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

host, port, size, timeout = "54.209.5.48", 12345, 2048, 1.5
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

phase2_dict = { 252: "tired of making up bogus answers",
                249: "this is where the answer goes",
                234: "easiest answer",
                239: "winning for the win",
                233: "not not wrong",
                237: "more answers here"
            }

def decode_ceasar(char, shift):
    res = (ord(char) - shift)
    if res > 122:
        res -= 26
    elif res < 97:
        res += 26

    if res > 96 and res < 123:
        return chr(res)
    return char

def find_stepsize(psifer2):
    possibles = [i for i, x in enumerate(psifer2) if x == ' ']
    for pos in possibles:
        if psifer2[pos*2] == 'h':
            return pos

def decode_transpose(psifer2):
    stepsize = find_stepsize(psifer2)
    box = [[] for i in range(stepsize)]
    for i in range(len(psifer2)):
        box[i % stepsize].append(psifer2[i])
    for i in range(len(box)):
        box[i] = ''.join(box[i])
    return ''.join(box)

def poll_server():
    last = time.time()
    total_data = []
    m = None
    while not m:
        data = s.recv(size)
        total_data.append(data)
        m = re.search('psifer text:.*\n', data)
    return m.group(0)[13:]

def find_coinc(psifer3,cmax):
    coinc_count = {}
    for i in range(1,cmax):
        coinc = 0
        for j in range(len(psifer3)):
            if j+i < len(psifer3):
                if psifer3[j] == psifer3[j+i]:
                    coinc += 1
        coinc_count[i] = coinc

    return coinc_count
        
def sub_vkey(psifer3,keys):
    if not keys:
        return
    key = keys[0]
    val_p3 = [(ord(x)-65) for x in psifer3 if x != ' ']
    val_key = [ord(x)-65 for x in key]
    for i in range(len(val_p3)):
        val_p3[i] -= val_key[i % len(key)]
        if val_p3[i] > 25:
            val_p3[i] -= 26
        elif val_p3[i] < 0:
            val_p3[i] += 26

    tmp = ''.join([chr(x + 65) for x in val_p3])
    if tmp[0:4] != 'THIS':
        return sub_vkey(psifer3,keys[1:])
    #return ' '.join(tmp[i:i+5] for i in xrange(0,len(tmp),5))
    return tmp

phase2success = False
# Phase 1        
psifer1 = poll_server()
print "Shift Cipher:"
print psifer1
ceasar_shift = ord(psifer1[0]) - ord('t')
print "Making educated guess shift is:", ceasar_shift % 26
decoded1 = ''.join([decode_ceasar(let,ceasar_shift) for let in psifer1])
key1 = re.search('\w+\n',decoded1).group(0)
"Sending key for part 1: ", key1
s.send(key1)

# Phase 2
print "Transposition ciphertext:"
psifer2 = poll_server()[:-1]
print psifer2
key2 = phase2_dict[len(psifer2)]
print "Sending key for part 2: ", key2
s.send(key2 + '\n')

# Phase 3
print "Vigenere Cipher:"
psifer3 = poll_server()[:-1]
spaceless_ps3 = psifer3.replace(' ','')
print spaceless_ps3
VEG_KEYS = [ 'TOBRUTE', 'FORCE', 'WORDS', 'DNARI']

#print psifer3
print "*" * 72
decoded3 = sub_vkey(psifer3,VEG_KEYS)
key3 = re.search('RIGHTHERE\w+OK', decoded3).group(0)[9:-2]
print "Sending key3: ", key3
s.send(key3 + '\n')

psifer4 = s.recv(size)
print psifer4
#print len(spaceless_ps3)
#print find_coinc(spaceless_ps3,21)

#factors = [x for x in range(1,len(spaceless_ps3)/2 + 1) if len(spaceless_ps3) % x == 0 and x > 5 and x < 20]
#for fac in factors:
#    #print ' '.join(spaceless_ps3[i:i+fac] for i in xrange(0,len(spaceless_ps3),fac))
#    print collections.Counter(spaceless_ps3[::fac])

s.close()
