import json
import struct
import sys

class LyricLine(object):
    def __init__(self, line):
        self.words = []
        self.line = line

    @property
    def start(self):
        """ return start time of this line. We dynamically calculate the value
        """
        return sorted(self.words, key=lambda word : word.start)[0].start

    @property
    def end(self):
        """ return end time of this line. We dynamically calculate the value
        """
        return sorted(self.words, key=lambda word : word.end)[-1].end

    def __dict__(self):
        return {
                'start' : self.start,
                'end'   : self.end,
                'line'  : self.line
            }

class LyricWord(object):
    def __init__(self, **kwargs):
        self.start = kwargs['start'] 
        self.end = kwargs['end']
        self.index = kwargs['index']
        self.length = kwargs['length']
        self.rel_line = kwargs['rel_line']
        self.abs_line = kwargs['abs_line']
        self.newline = True if kwargs['newline'] else False
        self.word = kwargs['word']

class Skym(object):
    @classmethod
    def open(cls, fn):
        return Skym(fn)
         
    def __init__(self, filename):
        self.filename = filename

        f = open(filename, "rb")
            
        # section 1: header
        # content: ???
        # length: 128 bytes
        self.header = f.read(128)

        # section 2: song info
        # content: contains metadata about the song
        # length: 256 bytes
        b_info = f.read(256)

        ## info bytes are layout as follows
        ## 04 bytes = 'LTAG' (garbage)
        ## 05 bytes = song id
        ## 01 byte  = padding
        ## 80 bytes = song title
        ## 20 bytes = lyricists
        ## 20 bytes = composer
        ## 20 bytes = singer
        ## 13 bytes = UNKNOWN
        ## 01 byte  = F or M (female or male)
        ## 48 bytes = melody keys
        ## 43 bytes = garabae (20s)
        INFO_FMT = "4x5s1x80s20s20s20s13x1s1x48s43x"
        i_fields = ('id', 
                    'title', 
                    'lyricist', 
                    'composer',
                    'singer', 
                    'sex', 
                    'keys')
        i_vals = struct.unpack(INFO_FMT, b_info)
        self.info = {k : v.decode('cp949') for 
                        k,v in zip(i_fields, i_vals)}


        # section 3: song lyric
        # content: contains song lyrics
        # length: variable
        #
        ## lyrics laid out as "page by page"
        ## Each 'page' can have any number of bytes
        ## Each 'page' is separated with X 00 bytes
        ## where the number of 00 bytes is not really knwon
        ## When 'STAG' x(53 54 41 47) is read, we know we have 
        ## reached the end of lyric section

        LYRIC_EOS = [b'\x53', b'\x54', b'\x41', b'\x47']
        word = ['']*4       # holds currently read word (4 bytes)
        bytes_read = 0      # holds number of bytes read
        cur_page = []       # holds bytes of the current "page"
        in_padding = False  # tells wheter we are reading padded values

        self.b_lyric = []   # hold pages of lyric as binary
        self.lyric = []     # holds pages of lyrics decoded to cp949

        ## we skip the first 4 byte (ltag garbage)
        f.read(4)

        ## we read until we read STAG
        while word != LYRIC_EOS:
            byte = f.read(1)
            word[bytes_read % 4] = byte
            bytes_read += 1

            ## if the byte read is 00, 
            ## we have reached the end of current page
            if byte == b'\x00':
                if not in_padding:
                    in_padding = True
                    ## append decoded lyric to the lyric
                    lyric = b''.join(cur_page)
                    self.b_lyric.append(lyric)
                    self.lyric.append(lyric.decode('cp949'))
                    cur_page = []
            else:
                in_padding = False
                cur_page.append(byte)
            

        # section 4: song lyric info
        # content: maps lyric to song (length of each word)
        # length: variable
        #
        ## lyric info is laid out in units of 23 bytes 
        ## per "word" in the song's lyric
        ##
        ## format:
        ## AA AA AA AA BB BB BB BB CC DD EE 00 00 00 FF 00 00 00 0G 0F 00 00 00
        ## AA = word starttime in milisec
        ## BB = word endtime in milisec
        ## CC = byte _index_ of the current lyric page
        ## DD = number of bytes (from CC) to be highlighted
        ## EE = relative line number (current verse)
        ## FF = absolute line number (entire song)
        ## G = end of section
        ## F = newline?

        ## for simplicity, we will only parse out 
        ## the length of each "page"
        LYRIC_FMT = "IIBBB3xB3xBB3x" 
        i_fields = ('start',
                    'end',
                    'index',
                    'length',
                    'rel_line',
                    'abs_line',
                    'EOF',
                    'newline')
        EOF_BYTE = 7

        import codecs
        self.lyric_info = [None] * len(self.lyric)

        while True:
            b_info = f.read(23)
            i_vals = struct.unpack(LYRIC_FMT, b_info)
            info = {k : v for 
                        k,v in zip(i_fields, i_vals)}

            ## extract "word" associated with this set
            index = info['index']
            length = info['length']
            word_str = self.b_lyric[info['abs_line']][index:index+length].decode('cp949')
            word = LyricWord(word=word_str, **info)
            line = self.lyric_info[info['abs_line']]  

            if not line:
                line = LyricLine(self.lyric[info['abs_line']])

            line.words.append(word) 
            self.lyric_info[info['abs_line']] = line

            ## EOF Byte is seen AND all lyric has been filled
            if (info['EOF'] == EOF_BYTE) and not (None in self.lyric_info):
                break

    def toJson(self):
        return json.dumps(list(map(lambda x : x.__dict__(),self.lyric_info)))

def _print_sec4():
        import codecs
        for i in range(1000):
            bs = f.read(23)
            to_print = []
            for i in range(len(bs)):
                byte = bs[i:i+1]
                encoded_b = codecs.encode(byte, 'hex')
                if byte != b'\x00':
                    to_print.append(encoded_b)
            if len(to_print) == 7:
                to_print.insert(4, b'00')
            if len(to_print) < 7:
                to_print.append(b'00')

            sec = (int(to_print[3],16) - int(to_print[1],16))
            if sec < 0:
                sec = 256 - (int(to_print[1],16) - int(to_print[3],16)) 
            print("{1}\t:{0}".format(str(to_print), sec))
                
def _print_lyric(lyric):
    lyric = ["{}\t{}".format(y,x) for x, y in zip(lyric, range(1,len(lyric)+1))]
    print("\n".join(lyric))

if __name__ == "__main__":
    import json
    song = "./sample/{}.skym".format(sys.argv[1])
    sk = Skym.open(song)
    print(sk.toJson())
    #print(sk.info)

    #_print_lyric(sk.lyric)
    #print("\n".join(lyric))
