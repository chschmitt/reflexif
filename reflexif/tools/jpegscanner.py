'''
Created on 26.06.2017

@author: gongy
'''
import io
from reflexif.parsers.parser_jpeg import JPEGStreamParser
import traceback

MARKER = b'\xff\xd8'

class FileScanner(object):
    def __init__(self, data, source=None):
        self.data = data
        self.source = None
        self.children = []
        self.error = False
        self.payload = None
    
    def scan(self):
        try:
            self._scan()
        except Exception:
            traceback.print_exc()
            self.error = True
    
    def _scan(self):
        marker_index = self.data.find(MARKER)
        if marker_index < 0:
            self.error = True
            return
        
        with io.BytesIO(self.data) as fd:
            fd.seek(marker_index)
            p = JPEGStreamParser(fd)
            for seg in p.parse_segments():
                if seg.segment.is_app:
                    child = FileScanner(seg.payload, source=seg)
                    self.children.append(child)
                    child.scan()
            
            self.payload = self.data[marker_index:fd.tell()]
            
            p.parse_trailer()
            if not p.trailer:
                return
            
            print('trailer!')
            child = FileScanner(p.trailer.data, source=p.trailer)
            self.children.append(child)
            child.scan()
            
    def traverse(self):
        stack = [self]
        while stack:
            current = stack.pop()
            if not current.error and current.payload:
                yield current.payload
            stack.extend(current.children)
                
if __name__ == '__main__':
    from tests import testfiles
    import itertools
    seq = itertools.count(start=1)
    for path in testfiles.FILES:
        print(path)
        with open(path, 'rb') as fd:
            data = fd.read()
        s = FileScanner(data)
        s.scan()
        for blob in s.traverse():
            print(path, blob[:10])
            fname = '/dev/shm/%04d.jpg' % next(seq)
            with open(fname, 'wb') as fd:
                fd.write(blob)
            