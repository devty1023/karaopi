import struct

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

        ## lyrics laid out as "page by page"
        ## Each 'page' can have any number of bytes
        ## Each 'page' is separated with X 00 bytes
        ## where the number of 00 bytes is not really knwon
        ## When 'STAG' x(53 54 41 47) is read, we know we have 
        ## reached the end of lyric section
        LYRIC_EOS = [b'\x53', b'\x54', b'\x41', b'\x47']
        word = ['']*4
        bytes_read = 0
        cur_page = []
        in_padding = False

        self.lyric = []

        ## we skip the first 4 byte (garbage)
        f.read(4)

        ## we read until we read a 32byte word 
        ## equivalent to LYRIC_EOS 
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
                    self.lyric.append(lyric.decode('cp949'))
                    cur_page = []
            else:
                in_padding = False
                cur_page.append(byte)
            

        import codecs
        for i in range(100):
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
            #print("{1}\t{2}\t:{0}".format(str(to_print), int(to_print[3],16) - int(to_print[1],16)))
                

if __name__ == "__main__":
    sk = Skym.open("./sample/76754.skym")
    #print(sk.info)
    print("\n".join(sk.lyric))
