from . import binary_reader

def read_link(self, link_format="DPC", count=None):
    if link_format == "DPC":
        return self.read_uint32(count)
    elif link_format == "BFF":
        return self.read_int32(count)

binary_reader.BinaryReader.read_link = read_link