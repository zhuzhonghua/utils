# coding:utf-8
# style:
# class name: StreamStr, SWF
# variable name: stream, abc, file_pos
# method name: readTag, usage
# SB[1] readBitFlag
# UB[1] readBitFlag

import sys, os
import struct
import zlib
import ctypes

def usage():
    print "usage: python ", sys.argv[0], " filename.swf"
    sys.exit(1)

def DEBUG(arg):
    print arg

D=DEBUG

class StreamFile:
    def __init__(self, filename):
        self.filename = filename
        self.stream = file(filename, "rb")
        self.stream.seek(0, os.SEEK_END)
        self.file_size = self.stream.tell()
        self.stream.seek(0, os.SEEK_SET)
        self.pos = self.stream.tell()

    def readBytes(self, n):
        self.pos += n
        res = self.stream.read(n)
        #DEBUG("streamfile readbytes["+res+"]")
        return res

    def setPos(self, pos):
        self.stream.seek(pos, os.SEEK_SET)
        
class StreamStr:
    def __init__(self, str):
        self.stream = str
        self.pos = 0

    def readBytes(self, n=-1):
        if n != -1:
            res = self.stream[self.pos:self.pos+n]
            self.pos += n
            #DEBUG("streamstr readbytes["+res+"]")
        else:
            res = self.stream[self.pos:]
            self.pos = len(self.stream)
        return res
    
    def setPos(self, pos):
        self.pos = pos
        
class Stream:
    def __init__(self, filename=None, string=None):
        if filename:
            streamFile = StreamFile(filename)
            content = streamFile.readBytes(streamFile.file_size)
            self.stream = StreamStr(content)
        else:
            self.stream = StreamStr(string)
        self.unused_bits = 0
        self.current_byte = 0
        self.m_tag_stack = []

    def getPos(self):
        return self.stream.pos
    
    def setPos(self, pos):
        self.stream.pos = pos
        
    def align(self):
        self.unused_bits = 0
        self.current_byte = 0

    def openTag(self):
        self.align()
        tag_header = self.readUI16()
        tag_type = tag_header>>6
        tag_len = tag_header&0x3F
        if tag_len == 0x3F:
            tag_len = self.readSI32()
            
        DEBUG("tag_type="+str(tag_type)+", tag_len="+str(tag_len))
        self.m_tag_stack.append((tag_type, self.stream.pos+tag_len))
        return tag_type

    def closeTag(self):
        (tag_type, end_pos) = self.m_tag_stack.pop()
        if end_pos != self.stream.pos:
            DEBUG("!!!!!!!!!!!tag "+str(tag_type)+" is not correctly read,end_pos="+str(end_pos)+",streampos="+str(self.stream.pos))
            self.stream.setPos(end_pos)
        
        self.align()

    def ensureBytes(self, n):
        if len(self.m_tag_stack) <= 0:
            return
        elif n > self.getTagEndPos()-self.getPos():
            raise Exception("need bytes="+str(n)+", left "+str(self.getTagEndPos()-self.getPos()))
    
    def getTagEndPos(self):
        (tag_type, end_pos) = self.m_tag_stack[-1]
        return end_pos
    
    def decompress(self):
        res = zlib.decompress(self.stream.readBytes())
        self.stream = StreamStr(res)

    def getTagLeftLen(self):
        return self.getTagEndPos() - self.getPos()
    
    def getLeftTagBytes(self):
        return self.readBytes(self.getTagLeftLen())
    
    def decompressBytes(self):
        zip = zlib.decompressobj()
        data = zip.decompress(self.stream.stream[self.getPos():])
        self.readBytes(len(zlib.compress(data, 9)))
        
        return data
            
    def readChar(self):
        self.align()
        res = self.stream.readBytes(1)
        return res
    
    def readString(self):
        self.align()
        value = ""
        c = self.readChar()
        while c != "\0":
            value += c
            c = self.readChar()
        return value

    def readBytes(self, num):
        self.align()
        self.ensureBytes(num)
        return self.stream.readBytes(num)
    
    def readUI8(self):
        self.align()
        res = self.readBytes(1)
        return struct.unpack("B", res)[0]

    def toUI8(self, byte):
        return struct.unpack("B", byte)[0]

    def readSI8(self):
        self.align()
        res = self.readBytes(1)
        return struct.unpack("b", res)[0]

    def readUI16(self):
        self.align()
        res = self.readBytes(2)
        return struct.unpack("H", res)[0]
    
    def readSI16(self):
        self.align()
        res = self.readBytes(2)
        return struct.unpack("h", res)[0]
    
    def readUI32(self):
        self.align()
        res = self.readBytes(4)
        return struct.unpack("I", res)[0]
    
    def readSI32(self):
        self.align()
        res = self.readBytes(4)
        return struct.unpack("i", res)[0]

    def readFloat(self):
        self.align()
        res = self.readBytes(4)
        return struct.unpack("f", res)[0]

    def readFloat16(self):
        self.align()
        res = self.readBytes(2)
        value = (res & 0x8000) << 16
        value |= ((((res >> 10) & 0x1F)+0x70) << 23)
        value |= ((res & 0x3FF) << 13)
        res = struct.pack("I", value)
        return struct.unpack("f", res)
        
    def readDouble(self):
        self.align()
        res = self.readBytes(8)
        return struct.unpack("d", res)[0]
    
    def readUIntBit(self, bitcount):
        if bitcount > self.unused_bits:
            value = 0
            if self.unused_bits > 0:
                unused_mask = (1<<self.unused_bits)-1
                bitcount -= self.unused_bits
                value |= ((self.current_byte&unused_mask)<<bitcount)

            bytes_to_read = bitcount/8
            spare_bits = bitcount%8

            if spare_bits != 0:
                cache = self.readBytes(bytes_to_read+1)
            else:
                cache = self.readBytes(bytes_to_read)

            for i in xrange(bytes_to_read):
                bitcount -= 8
                value |= self.toUI8(cache[i])<<bitcount

            if bitcount > 0:
                self.current_byte = self.toUI8(cache[bytes_to_read])
                self.unused_bits = 8-bitcount
                value |= self.current_byte>>self.unused_bits
            else:
                self.unused_bits = 0
                
            return value

        if self.unused_bits == 0:
            self.current_byte = self.readUI8()
            self.unused_bits = 8

        unused_mask = (1<<self.unused_bits)-1
        if bitcount == self.unused_bits:
            self.unused_bits = 0
            return self.current_byte&unused_mask
        else:
            self.unused_bits -= bitcount
            return (self.current_byte&unused_mask)>>self.unused_bits
        
    def readUIntBit_bak(self, bits):
        value = 0
        while bits > 0:
            if self.unused_bits > 0:
                if bits >= self.unused_bits:
                    value |= (self.current_byte<<(bits-self.unused_bits))
                    bits -= self.unused_bits
                    self.unused_bits = 0
                    self.current_byte = 0
                else:
                    value |= (self.current_byte>>(self.unused_bits-bits))
                    self.current_byte &= ((1 << (self.unused_bits - bits)) - 1)
                    self.unused_bits -= bits
                    bits = 0
            else:
                self.current_byte = self.readUI8()
                self.unused_bits = 8
                
        return ctypes.c_uint(value).value

    def readBitFlag(self):
        value = self.readUIntBit(1)
        value = ctypes.c_int(value).value
        return value == 1
    
    def readSIntBit(self, bits):
        value = self.readUIntBit(bits)
        value = ctypes.c_int(value).value

        if bits > 0:
	    if (value & (1 << (bits - 1))) != 0:
                value |= (-1 << bits)
            
        return value

    def readFixedD8(self):
        value = self.readSI16()
        return value/256
    
    def readFixed(self):
        value = self.readSI32()
        return value/65536

    def readEncodedU32(self):
        value = self.readUI8()
        if value & 0x00000080 == 0:
            return value
        value = (value & 0x0000007F) | (self.readUI8() << 7)
        if value & 0x00004000 == 0:
            return value
        value = (value & 0x00003FFF) | (self.readUI8() << 14)
        if value & 0x00200000 == 0:
            return value
        value = (value & 0x001FFFFF) | (self.readUI8() << 21)
        if value & 0x10000000 == 0:
            return value
        value = (value & 0x0FFFFFFF) | (self.readUI8() << 28)
        return value
    
class RECT:
    def __init__(self):
        self.x_min = 0
        self.y_min = 0
        self.x_max = 0
        self.y_max = 0
        
    def read(self, stream):
        nbits = stream.readUIntBit(5)
        self.x_min = stream.readSIntBit(nbits)
        self.x_max = stream.readSIntBit(nbits)
        self.y_min = stream.readSIntBit(nbits)
        self.y_max = stream.readSIntBit(nbits)

class GradRecord:
    def __init__(self):
        pass
    def read(self, stream, tag_type):
        self.ratio = stream.readUI8()
        self.color = RGBA()
        if tag_type == DefineShapeLoader.tag_type or \
                tag_type == DefineShapeLoader.tag_type2:
            self.color.readRGB(stream)
        else:
            self.color.readRGBA(stream)
            
class Gradient:
    def __init__(self):
        pass
    def readGradient(self, stream, tag_type):
        flag = stream.readUI8()
        self.spread_mode = (((flag & 0xF0) >> 4) & 0xC)>>2
        self.interpolation_mode = ((flag & 0xF0)>>4) & 0x3
        self.num_gradient = flag & 0x0F

        self.gradient_records = []
        for i in xrange(self.num_gradient):
            gr = GradRecord()
            gr.read(stream, tag_type)
            self.gradient_records.append(gr)
            
    def readFocalGradient(self, stream, tag_type):
        flag = stream.readUI8()
        self.spread_mode = (((flag & 0xF0) >> 4) & 0xC)>>2
        self.interpolation_mode = ((flag & 0xF0)>>4) & 0x3
        self.num_gradient = flag & 0x0F

        self.gradient_records = []
        for i in xrange(self.num_gradient):
            gr = GradRecord()
            gr.read(stream, tag_type)
            self.gradient_records.append(gr)
        self.focal_point = stream.readFixedD8()
        
class FillStyle:
    def __init__(self):
        self.fill_style_type = 0
    def read(self, stream, tag_type):
        self.fill_style_type = stream.readUI8()
        if self.fill_style_type == 0x00:
            if tag_type == tag_type == DefineShapeLoader.tag_type3:
                self.color = RGBA()
                self.color.readRGBA(stream)
            elif tag_type in [DefineShapeLoader.tag_type, DefineShapeLoader.tag_type2]:
                self.color = RGBA()
                self.color.readRGB(stream)
            
        if self.fill_style_type in [0x10, 0x12]:
            self.gradient_matrix = Matrix()
            self.gradient_matrix.read(stream)
            self.gradient = Gradient()
            self.gradient.readGradient(stream, tag_type)
            
        if self.fill_style_type == 0x13:
            self.gradient = Gradient()
            self.gradient.readFocalGradient(stream, tag_type)

        if self.fill_style_type in [0x40, 0x41, 0x42, 0x43]:
            self.bitmap_id = stream.readUI16()
            self.bitmap_matrix = Matrix()
            self.bitmap_matrix.read(stream)
            
class FillStyleArray:
    def __init__(self):
        self.fill_style_count = 0
        self.fill_styles = []
    def read(self, stream, tag_type):
        self.fill_style_count = stream.readUI8()
        if self.fill_style_count == 0xFF:
            self.fill_style_count = stream.readUI16()
        for i in xrange(self.fill_style_count):
            fs = FillStyle()
            fs.read(stream, tag_type)
            self.fill_styles.append(fs)
            
class LineStyle:
    def __init__(self):
        pass
    def read(self, stream, tag_type):
        self.width = stream.readUI16()
        
        if tag_type in [DefineShapeLoader.tag_type,DefineShapeLoader.tag_type2]:
            self.color = RGBA()
            self.color.readRGB(stream)
            
        elif tag_type == DefineShapeLoader.tag_type3:
            self.color = RGBA()
            self.color.readRGBA(stream)

class LineStyle2:
    def __init__(self):
        pass
    def read(self, stream, tag_type):
        self.width = stream.readUI16()
        flag = stream.readUI8()
        self.start_cap_style = (flag >> 4) >> 2
        self.join_style = (flag >> 4) & 0x03
        
        self.has_fill_flag = (flag & 0x0F) & ( 1 << 3) >> 3
        self.no_h_scale_flag = (flag & 0x0F) & ( 1 << 2) >> 2
        self.no_v_scale_flag = (flag & 0x0F) & ( 1 << 1) >> 1
        self.pixel_hinting_flag = (flag & 0x0F) & 0x01

        flag = stream.readUI8()
        self.no_close = flag & (1 << 2) >> 2
        self.end_cap_style = flag & 0x03

        if self.join_style == 2:
            self.miter_limit_factor = stream.readUI16()
        if self.has_fill_flag == 1:
            self.color = RGBA()
            self.color.readRGBA()
        if self.has_fill_flag == 1:
            self.fill_type = FillStyle()
            self.fill_type.read(stream, tag_type)
            
class LineStyleArray:
    def __init__(self):
        pass
    def read(self, stream, tag_type):
        self.line_style_count = stream.readUI8()
        if self.line_style_count == 0xFF:
            self.line_style_count = stream.readUI16()
        
        if tag_type in [DefineShapeLoader.tag_type, DefineShapeLoader.tag_type2, DefineShapeLoader.tag_type3]:
            self.line_styles = []
            for i in xrange(self.line_style_count):
                ls = LineStyle()
                ls.read(stream, tag_type)
                self.line_styles.append(ls)
                
        elif tag_type == DefineShapeLoader.tag_type4:
            self.line_styles = []
            for i in xrange(self.line_style_count):
                ls = LineStyle2()
                ls.read(stream, tag_type)
                self.line_styles.append(ls)


class Shape:
    def __init__(self):
        pass
    def read(self, stream):
        flag = stream.readUI8()
        num_fill_bits = (flag & 0xF0) >> 4
        num_line_bits = (flag & 0x0F)

        #self.shape_records = []
        while True:
            is_edge = stream.readUIntBit(1)
            if is_edge == 0:
                flag = stream.readUIntBit(5)
                if flag == 0:
                    break
                # state move to
                if (flag & 0x01) == 0x01:
                    self.move_bits = stream.readUIntBit(5)
                    self.move_delta_x = stream.readSIntBit(self.move_bits)
                    self.move_delta_y = stream.readSIntBit(self.move_bits)
                # state fillstyle0
                if (flag & 0x02) == 0x02:
                    self.fill_style0 = stream.readUIntBit(num_fill_bits)
                # state fillstyle1
                if (flag & 0x04) == 0x04:
                    self.fill_style1 = stream.readUIntBit(num_fill_bits)
                # state line style
                if (flag & 0x08) == 0x08:
                    self.line_style = stream.readUIntBit(num_line_bits)
                # state new styles
                if (flag & 0x10) == 0x10:
                    self.fill_styles = FillStyleArray()
                    self.fill_styles.read(stream, tag_type)
                    self.line_styles = LineStyleArray()
                    self.line_styles.read(stream, tag_type)
                    num_fill_bits = stream.readUIntBit(4)
                    num_line_bits = stream.readUIntBit(4)
            else:
                straight_flag = stream.readUIntBit(1)
                num_bits = stream.readUIntBit(4)
                if straight_flag == 1:
                    general_line_flag = stream.readUIntBit(1)
                    if general_line_flag == 0:
                        vert_flag = stream.readBitFlag()
                    if general_line_flag == 1 or vert_flag == 0:
                        delta_x = stream.readSIntBit(num_bits+2)
                    if general_line_flag == 1 or vert_flag == 1:
                        delta_y = stream.readSIntBit(num_bits+2)
                else:
                    control_delta_x = stream.readSIntBit(num_bits+2)
                    control_delta_y = stream.readSIntBit(num_bits+2)
                    anchor_delta_x = stream.readSIntBit(num_bits+2)
                    anchor_delta_y = stream.readSIntBit(num_bits+2)
                    
class ShapeWithStyle(Shape):
    def __init__(self):
        Shape.__init__(self)
        
        self.fillStyles = None
        self.lineStyles = None
        self.numFillBits = 0
        self.numLineBits = 0
        self.shape_records = None
        
    def read(self, stream, tag_type):
        self.fill_styles = FillStyleArray()
        self.fill_styles.read(stream, tag_type)
        self.line_styles = LineStyleArray()
        self.line_styles.read(stream, tag_type)

        Shape.read(self, stream)
                    
class ShapeCharacterDef:
    def __init__(self):
        self.shape_bounds = None
    def read(self, stream, tag_type, flag, swf):
        self.shape_bounds = RECT()
        self.shape_bounds.read(stream)
        self.shapes = ShapeWithStyle()
        self.shapes.read(stream, tag_type)

class RGBA:
    def __init__(self):
        pass
    def readRGB(self, stream):
        self.r = stream.readUI8()
        self.g = stream.readUI8()
        self.b = stream.readUI8()
        self.a = 0xFF;

    def readRGBA(self, stream):
        self.readRGB(stream)
        self.a = stream.readUI8()

class AlphaColorMapData:
    def __init__(self):
        self.colorTableRGB = []
        self.colorMapPixelData = []
        
    def read(self, stream, color_table_size, bm_width, bm_height, tag_type):
        stream = Stream(string=stream)
        i = 0
        while i < color_table_size+1:
            i += 1
            rgba = RGBA()
            if tag_type == 36:
                rgba.readRGBA(stream)
            elif tag_type == 20:
                rgba.readRGB(stream)
            else:
                raise Exception("alpha color map , "+str(tag_type))
            self.colorTableRGB.append(rgba)
            
        self.colorMapPixelData = stream.readBytes(bm_width*bm_height)

class AlphaBitmapData:
    def __init__(self):
        self.bitmap_pixel_data = []
        
    def read(self, stream, bm_width, bm_height, tag_type, bitmap_format):
        streamInst = Stream(string=stream)
        i = 0
        while i < bm_width*bm_height:
            i += 1
            if tag_type == 36:
            	rgba = RGBA()
            	rgba.readRGBA(streamInst)
            	self.bitmap_pixel_data.append(rgba)
            elif tag_type == 20:
                pass
            else:
                raise Exception("alpha bitmap data, "+str(tag_type))
            
class SetBackgroundColor:
    def __init__(self):
        self.color = RGBA()
        
    def read(self, stream):
        self.color.readRGB(stream)
        DEBUG("set backgroundcolor "+str(self.color.r)+", "+str(self.color.g)+", "+str(self.color.b))

class BitmapInfo:
    def __init__(self):
        pass

class BitmapCharacter:
    def __init__(self, swf, bitmap_info):
        self.swf = swf
        self.bitmap_info = bitmap_info

class Matrix:
    def __init__(self):
        #self.m = [[0 for i in xrange(3)] for j in xrange(2)]
        self.a = 65536
        self.b = 0
        self.c = 0
        self.d = 65536
        self.tx = 0
        self.ty = 0
        
    def read(self, stream):
        stream.align()
        sx = 65536
        sy = 65536
        
        has_scale = stream.readUIntBit(1) == 1
        if has_scale:
            scale_bits = stream.readUIntBit(5)
            sx = stream.readUIntBit(scale_bits)
            sy = stream.readUIntBit(scale_bits)
        has_rotate = stream.readUIntBit(1) == 1
        shx = 0
        shy = 0
        if has_rotate:
            rotate_bits = stream.readUIntBit(5)
            shx = stream.readUIntBit(rotate_bits)
            shy = stream.readUIntBit(rotate_bits)
        tx = 0
        ty = 0
        translate_bits = stream.readUIntBit(5)
        if translate_bits > 0:
            tx = stream.readSIntBit(translate_bits)
            ty = stream.readSIntBit(translate_bits)
        self.a = sx
        self.b = shx
        self.c = shy
        self.d = sy
        self.tx = tx
        self.ty = ty
        
class CXForm:
    def __init__(self):
        self.m = [[0 for i in xrange(2)] for j in xrange(4)]
        
    def readRGBA(self, stream):
        stream.align()
        has_add = stream.readBitFlag()
        has_mult = stream.readBitFlag()
        bits = stream.readUIntBit(4)

        if has_mult:
            self.m[0][0] = stream.readSIntBit(bits)/256.0
            self.m[1][0] = stream.readSIntBit(bits)/256.0
            self.m[2][0] = stream.readSIntBit(bits)/256.0
            self.m[3][0] = stream.readSIntBit(bits)/256.0
        else:
            for i in range(4):
                self.m[i][0] = 1

        if has_add:
            self.m[0][1] = stream.readSIntBit(bits)/256.0
            self.m[1][1] = stream.readSIntBit(bits)/256.0
            self.m[2][1] = stream.readSIntBit(bits)/256.0
            self.m[3][1] = stream.readSIntBit(bits)/256.0
        else:
            for i in range(4):
                self.m[i][1] = 0

class ActionRecord:
    def __init__(self):
        self.action_code = 0
        self.length = 0
        self.action = None
        
    def read(self, stream, swf):
        self.action_code = stream.readUI8()
        if self.action_code == 0:
            return False
        
        if self.action_code >= 0x80:
            self.length = stream.readUI16()
            self.action = stream.readBytes(self.length)
            
class ClipActionRecord:
    def __init__(self):
        self.event_flags = None
        self.action_record_size = 0
        self.keycode = 0
        self.actions = None
        
    def read(self, stream, swf):
        self.event_flags = ClipEventFlags()
        self.event_flags.read(stream, swf)
        if self.event_flags.flags != 0:
            self.action_record_size = stream.readUI32()
            
            if self.event_flags.key_press:
                self.keycode = stream.readUI8()
                
            self.actions = ActionRecord()
            self.actions.read(stream, swf)
        
class ClipActions:
    def __init__(self):
        self.all_event_flags = None
        
    def read(self, stream, swf):
        stream.readUI16()
        self.all_event_flags = ClipEventFlags()
        self.all_event_flags.read(stream, swf)
        self.clip_action_records = []
        #ClipActionRecord
        while True:
            clip_action_record = ClipActionRecord()
            clip_action_record.read(stream, swf)
            if clip_action_record.event_flags.getFlag() == 0:
                break
            self.clip_action_records.append(clip_action_record)
                
class ClipEventFlags:
    def __init__(self):
        #self.key_up = False
        #self.key_down = False
        #self.mouse_up = False
        #self.mouse_down = False
        #self.mouse_move = False
        #self.unload = False
        #self.enter_frame = False
        #self.drag_over = False
        #self.roll_out = False
        #self.roll_over = False
        #self.release_outsize = False
        #self.release = False
        #self.press = False
        #self.initialize = False
        #self.data = False
        #self.construct = False
        #self.key_press = False
        #self.drag_out = False
        self.flags = 0

    def getFlag(self):
        return self.flags
    
    def read(self, stream, swf):
        if swf.version < 6:
            self.flags = stream.readUI16()
        else:
            self.flags = stream.readUI32()
            
        return self.flags
    
        #self.key_up = stream.readBitFlag()
        #self.key_down = stream.readBitFlag()
        #self.mouse_up = stream.readBitFlag()
        #self.mouse_down = stream.readBitFlag()
        #self.mouse_move = stream.readBitFlag()
        #self.unload = stream.readBitFlag()
        #self.enter_frame = stream.readBitFlag()
        #self.load = stream.readBitFlag()
        #self.drag_over = stream.readBitFlag()
        #self.roll_out = stream.readBitFlag()
        #self.roll_over = stream.readBitFlag()
        #self.release_outsize = stream.readBitFlag()
        #self.release = stream.readBitFlag()
        #self.press = stream.readBitFlag()
        #self.initialize = stream.readBitFlag()
        #self.data = stream.readBitFlag()
        #
        #if swf.version >= 6:
        #    stream.readUIntBit(5)
        #    self.construct = stream.readBitFlag()
        #    self.key_press = stream.readBitFlag()
        #    self.drag_out = stream.readBitFlag()
        #    stream.readUIntBit(8)

class PlaceObject:
    def __init__(self):
        self.tag_type = 0
        self.has_clip_actions = False
        self.has_clip_depth = False
        self.has_name = False
        self.has_ratio = False
        self.has_color_transform = False
        self.has_matrix = False
        self.has_character = False
        self.flag_move = False
        self.depth = 0

        self.character_id = 0
        self.matrix = None
        self.color_transform = None
        self.ration = 0
        self.name = ""
        self.clip_depth = 0
        self.clip_actions = None
        
    def read(self, stream, tag_type, swf):
        self.tag_type = tag_type
        if tag_type == 26:
            self.flags = stream.readUI8()
            
            self.has_clip_actions = self.flags & (1 << 7)
            self.has_clip_depth = self.flags & (1 << 6)
            self.has_name = self.flags & (1 << 5)
            self.has_ratio = self.flags & (1 << 4)
            self.has_color_transform = self.flags & (1 << 3)
            self.has_matrix = self.flags & (1 << 2)
            self.has_character = self.flags & (1 << 1)
            self.flag_move = self.flags & (1 << 0)
            
            self.depth = stream.readUI16()

            if self.has_character:
                self.character_id = stream.readUI16()
            if self.has_matrix:
                self.matrix = Matrix()
                self.matrix.read(stream)
            if self.has_color_transform:
                self.color_transform = CXForm()
                self.color_transform.readRGBA(stream)
            if self.has_ratio:
                self.ratio = stream.readUI16()
            if self.has_name:
                self.name = stream.readString()
            if self.has_clip_depth:
                self.clip_depth = stream.readUI16()
            if self.has_clip_actions:
                self.clip_actions = ClipActions()
                self.clip_actions.read(stream, swf)

class KerningRecord:
    def __init__(self):
        pass
    def read(self, stream, wide):
        if wide:
            self.kerning_code1 = stream.readUI16()
            self.kerning_code2 = stream.readUI16()
        else:
            self.kerning_code1 = stream.readUI8()
            self.kerning_code2 = stream.readUI8()
            
        self.kerning_adjust = stream.readSI16()

class ZoneData:
    def __init__(self):
        pass
    def read(self, stream, swf):
        self.align_coord = stream.readFixedD8()
        self.range = stream.readFixedD8()
        
class ZoneRecord:
    def __init__(self):
        pass
    def read(self, stream, swf):
        self.num_zone_data = stream.readUI8()
        self.zone_datas = []
        for i in xrange(self.num_zone_data):
            zd = ZoneData()
            zd.read(stream, swf)
            self.zone_datas.append(zd)
        flag = stream.readUI8()
        self.zone_mask_y = (flag & 0x2) >> 1
        self.zone_mask_x = flag & 0x1

class PIX15:
    def read(self, stream, swf):
        stream.readBitFlag()
        red = stream.readUIntBit(5)
        green = stream.readUIntBit(5)
        blue = stream.readUIntBit(5)
        
class PIX24:
    def read(self, stream, swf):
        stream.readUI8()
        red = stream.readUI8()
        green = stream.readUI8()
        blue = stream.readUI8()

class DropShadowFilter:
    def read(self, stream):
        color = RGBA()
        color.read(stream)
        blurx = stream.readFixed()
        blury = stream.readFixed()
        angle = stream.readFixed()
        distance = stream.readFixed()
        strength = stream.readFixedD8()
        flag = stream.readUI8()
        inner_shadow = (flag >> 7) & 0x1 == 0x1
        knock_out = (flag >> 6) & 0x1 == 0x1
        compositeSrc = (flag >> 5) & 0x1 == 0x1
        passes = flag & 0x1F
        
class BlurFilter:
    def read(self, stream):
        blurx = stream.readFixed()
        blury = stream.readFixed()
        flag = stream.readUI8()
        passes = flag >> 3
        
class GlowFilter:
    def read(self, stream):
        color = RGBA()
        color.read(stream)
        blurx = stream.readFixed()
        blury = stream.readFixed()
        strength = stream.readFixedD8()
        flag = stream.readUI8()
        innter_glow = (flag >> 7) & 0x1 == 0x1
        knock_out = (flag >> 6) & 0x1 == 0x1
        compositeSrc = (flag >> 5) & 0x1 == 0x1
        passes = (flag & 0x1F)
        
class BevelFilter:
    def read(self, stream):
        shadow_color = RGBA()
        shadow_color.read(stream)
        high_color = RGBA()
        high_color.read(stream)
        blurx = stream.readFixed()
        blury = stream.readFixed()
        angle = stream.readFixed()
        dist = stream.readFixed()
        strength = stream.readFixedD8()
        flag = stream.readUI8()
        innter_shadow = (flag >> 7) & 0x1 == 0x1
        knock_out = (flag >> 6) & 0x1 == 0x1
        compositeSrc = (flag >> 5) & 0x1 == 0x1
        onTop = (flag >> 4) & 0x1 == 0x1
        passes = (flag & 0xF)

class GradientGlowFilter:
    def read(self, stream):
        num = stream.readUI8()
        for i in xrange(num):
            color = RGBA()
            color.read(stream)
        for i in xrange(num):
            stream.readUI8()
        blurx = stream.readFixed()
        blury = stream.readFixed()
        angle = stream.readFixed()
        dist = stream.readFixed()
        strength = stream.readFixedD8()
        flag = stream.readUI8()
        innter_shadow = (flag >> 7) & 0x1 == 0x1
        knock_out = (flag >> 6) & 0x1 == 0x1
        compositeSrc = (flag >> 5) & 0x1 == 0x1
        onTop = (flag >> 4) & 0x1 == 0x1
        passes = (flag & 0xF)

class ConvolutionFilter:
    def read(self, stream):
        matrixX = stream.readUI8()
        matrixY = stream.readUI8()
        divisor = stream.readFloat()
        bias = stream.readFloat()
        for i in xrange(matrixX * matrixY):
            stream.readFloat()
        color = RGBA()
        color.read(stream)
        stream.readUIntBit(6)
        clamp = stream.readBitFlag()
        preserveAlpha = stream.readBitFlag()

class ColorMatrixFilter:
    def read(self, stream):
        for i in xrange(20):
            stream.readFloat()
            
class GradientBevelFilter:
    def read(self, stream):
        num = stream.readUI8()
        for i in xrange(num):
            color = RGBA()
            color.read(stream)
        for i in xrange(num):
            stream.readUI8()
        blurx = stream.readFixed()
        blury = stream.readFixed()
        angle = stream.readFixed()
        dist = stream.readFixed()
        strength = stream.readFixedD8()
        flag = stream.readUI8()
        innter_shadow = (flag >> 7) & 0x1 == 0x1
        knock_out = (flag >> 6) & 0x1 == 0x1
        compositeSrc = (flag >> 5) & 0x1 == 0x1
        onTop = (flag >> 4) & 0x1 == 0x1
        passes = (flag & 0xF)

class Filter:
    def read(self, stream):
        filter_id = stream.readUI8()
        if filter_id == 0:
            drop_shadow_filter = DropShadowFilter()
            drop_shadow_filter.read(stream)
        elif filter_id == 1:
            blur_filter = BlurFilter()
            blur_filter.read(stream)
        elif filter_id == 2:
            glow_filter = GlowFilter()
            glow_filter.read(stream)
        elif filter_id == 3:
            bevel_filter = BevelFilter()
            bevel_filter.read(stream)
        elif filter_id == 4:
            filter = GradientGlowFilter()
            filter.read(stream)
        elif filter_id == 5:
            filter = ConvolutionFilter()
            filter.read(stream)
        elif filter_id == 6:
            filter = ColorMatrixFilter()
            filter.read(stream)
        elif filter_id == 7:
            filter = GradientBevelFilter()
            filter.read(stream)
            
class FilterList:
    def read(self, stream):
        num = stream.readUI8()
        for i in xrange(num):
            filter = Filter()
            filter.read(stream)
            
class ButtonRecord:
    def read(self, stream, tag_type, swf):
        flag = stream.readUI8()
        if flag == 0:
            return False
        has_blend_mode = flag & (1 << 5) == (1 << 5)
        has_filter_list = flag & (1 << 4) == (1 << 4)
        state_hit_test = flag & (1 << 3) == (1 << 3)
        state_down = flag & (1 << 2) == (1 << 2)
        state_over = flag & (1 << 1) == (1 << 1)
        state_up = flag & (1 << 0) == (1 << 0)
        ch_id = stream.readUI16()
        depth = stream.readUI16()
        place_matrix = Matrix()
        place_matrix.read(stream)
        if tag_type == 34:
            cxform = CXForm()
            cxform.readRGBA(stream)
        if tag_type == 34 and has_filter_list:
            filter = FilterList()
            filter.read(stream)
        if tag_type == 34 and has_blend_mode:
            blend_mode = stream.readUI8()

class ButtonCondAction:
    def read(self, stream, tag_type, swf):
        cond_action_size = stream.readUI16()
        flag = stream.readUI8()
        #cond 
        flag = stream.readUI8()
        #cond
        while True:
            act_record = ActionRecord()
            flag = act_record.read(stream, tag_type, swf)
            if flag == False:
                break
        return cond_action_size
    
#class PlaceObject2:
#    def __init__(self):
#        self.tag_type = -1
#        self.depth = -1
#        self.character_id = -1
#        self.character_name = ""
#        self.has_matrix = False
#        self.matrix = Matrix()
#        self.has_cxform = False
#        self.color_transform = CXForm()
#        self.ratio = 0
#        self.clip_depth = -1
#        
#    def read(self, stream, tag_type, swf):
#        self.tag_type = tag_type
#        if tag_type == 26 or tag_type == 70:
#            stream.align()
#            has_actions = stream.readBitFlag()
#            has_clip_bracket = stream.readBitFlag()
#            has_name = stream.readBitFlag()
#            has_ratio = stream.readBitFlag()
#            self.has_cxform = stream.readBitFlag()
#            self.has_matrix = stream.readBitFlag()
#            has_char = stream.readBitFlag()
#            flag_move = stream.readBitFlag()
#            
#            has_image = False
#            has_class_name = False
#            has_cache_asbitmap = False
#            has_blend_mode = False
#            has_filter_list = False
#
#            if tag_type == 70:
#                stream.readUIntBit(3) #unused
#                has_image = stream.readBitFlag()
#                has_class_name = stream.readBitFlag()
#                has_cache_asbitmap = stream.readBitFlag()
#                has_blend_mode = stream.readBitFlag()
#                has_filter_list = stream.readBitFlag()
#
#            self.depth = stream.readUI16()
#            if has_char:
#                self.character_id = stream.readUI16()
#
#            if self.has_matrix:
#                self.matrix.read(stream)
#                
#            if self.has_cxform:
#                self.color_transform.readRGBA(stream)
#
#            if has_ratio:
#                self.ratio = stream.readUI16()/65535
#                DEBUG("ratio "+str(self.ratio))
#
#            if has_name:
#                self.character_name = stream.readString()
#                DEBUG("char name "+self.character_name)
#                
#            if has_clip_bracket:
#                self.clip_depth = stream.readUI16()
#                DEBUG("clip depth "+str(self.clip_depth))
#
#            if has_filter_list:
#                readFilterList(stream)

class EndLoader:
    tag_type = 0
    def __init__(self):
        pass

    def load(self, stream, tag_type, swf):
        pass

class ShowFrameLoader:
    tag_type = 1
    def __init__(self):
        pass
    def load(self, stream, tag_type, swf):
        pass

class DefineShapeLoader:
    tag_type = 2
    tag_type2 = 22
    tag_type3 = 32
    tag_type4 = 83
    def __init__(self):
        pass
    def load(self, stream, tag_type, swf):
        character_id = stream.readUI16()
        DEBUG("define shape loader character_id="+str(character_id))
        ch = ShapeCharacterDef()
        ch.read(stream, tag_type, True, swf)
        swf.addCharacter(character_id, ch)

class DefineButton:
    tag_type = 34
    tag_type2 = 7
    def load(self, stream, tag_type, swf):
        button_id = stream.readUI16()
        if tag_type == 7:
            while True:
                btnRecord = ButtonRecord()
                flag = btnRecord.read(stream, tag_type, swf)
                if flag == False:
                    break
            while True:
                actRecord = ActionRecord()
                flag = actRecord.read(stream)
                if flag == False:
                    break
        elif tag_type == 34:
            flag = stream.readUI8()
            track_as_menu = flag & 0x1 == 0x1
            
            start_pos = stream.getPos()
            action_offset = stream.readUI16()

            while True:
                act_record = ButtonRecord()
                flag = act_record.read(stream, tag_type, swf)
                if flag == False:
                    break
            if action_offset != 0:
                end_pos = stream.getPos()
                assert action_offset == end_pos - start_pos
                while True:
                    start_pos = stream.getPos()
                    
                    btn_cond_action = ButtonCondAction()
                    offset = btn_cond_action.read(stream, tag_type, swf)
                    
                    end_pos = stream.getPos()
                    if offset == 0:
                        break
                    else:
                        assert end_pos - start_pos != offset
                        
class SetBackgroundColorLoader:
    tag_type = 9
    def __init__(self):
        pass
    
    def load(self, stream, tag_type, swf):
        sb = SetBackgroundColor()
        sb.read(stream)

        swf.addExecuteTag(sb)

class DefineText:
    tag_type = 11
    tag_type2 = 33
    
    def load(self, stream, tag_type, swf):
        ch_id = stream.readUI16()
        text_bounds = RECT()
        text_bounds.read(stream)
        
        text_matrix = Matrix()
        text_matrix.read(stream)
        
        glyph_bits = stream.readUI8()
        advance_bits = stream.readUI8()
        while True:
            flag = stream.readUI8()
            if flag == 0:
                break
            tr_type = (flag >> 7) & 1
            reserved = (flag >> 4) & 0x3
            has_font = (flag >> 3) & 0x1 == 0x1
            has_color = (flag >> 2) & 0x1 == 0x1
            has_y_offset = (flag >> 1) & 0x1 == 0x1
            has_x_offset = (flag >> 0) & 0x1 == 0x1

            if has_font:
                font_id = stream.readUI16()
            if has_color:
                color = RGBA()
                if tag_type == 11:
                    color.readRGB(stream)
                elif tag_type == 33:
                    color.readRGBA(stream)
                else:
                    raise Exception("define text type "+str(tag_type))
            if has_x_offset:
                xoffset = stream.readSI16()
            if has_y_offset:
                yoffset = stream.readSI16()
            
            if has_font:
                text_height = stream.readUI16()
            glyph_count = stream.readUI8()
            for i in xrange(glyph_count):
                glyph_index = stream.readUIntBit(glyph_bits)
                glyph_advance = stream.readSIntBit(advance_bits)
                
class PlaceObject2Loader:
    tag_type = 26
    def __init__(self):
        pass
    def load(self, stream, tag_type, swf):
        ch = PlaceObject()
        ch.read(stream, tag_type, swf)
        #swf.add_execute_tag(ch)

class DefineBitsLossLess2Loader:
    tag_type = 36
    tag_type2 = 20
    def __init__(self):
        pass
    def load(self, stream, tag_type, swf):
        character_id = stream.readUI16()
        bitmap_format = stream.readUI8() # 3=8bit 4=16bit 5=32bit
        width = stream.readUI16()
        height = stream.readUI16()
        DEBUG("definebitslossless2 tag_type="+str(tag_type)+",id="+str(character_id)+",bitmap_format="+str(bitmap_format)+",width="+str(width)+",height="+str(height))

        if bitmap_format == 3:
            bitmap_color_table_size = stream.readUI8()+1
            alpha_color_map_data = stream.decompressBytes()
            #alpha_color_map_data_inst = AlphaColorMapData()
            #if tag_type == 36:
            #    alpha_color_map_data_inst.read(alpha_bitmap_data, bitmap_color_table_size, width, height, alpha_flag=True)
            #elif tag_type == 20:
            #    alpha_color_map_data_inst.read(alpha_bitmap_data, bitmap_color_table_size, width, height, alpha_flag=False)

        if bitmap_format == 4 or bitmap_format == 5:
            alpha_bitmap_data = stream.decompressBytes()
            #alpha_bitmap_data_inst = AlphaBitmapData()
            #alpha_bitmap_data_inst.read(alpha_bitmap_data, width, height)

class DefineEditText:
    tag_type = 37
    def __init__(self):
        pass
    def load(self, stream, tag_type, swf):
        self.ch_id = stream.readUI16()
        self.bounds = RECT()
        self.bounds.read(stream)
        flag = stream.readUI8()
        
        self.has_text   = (flag & 0x80) == 0x80
        self.word_wrap  = (flag & 0x40) == 0x40
        self.multi_line = (flag & 0x20) == 0x20
        self.passwd     = (flag & 0x10) == 0x10

        
        self.read_only          = (flag & 0x8) == 0x8
        self.has_text_color     = (flag & 0x4) == 0x4
        self.has_max_len        = (flag & 0x2) == 0x2
        self.has_font           = (flag & 0x1) == 0x1

        flag = stream.readUI8()
        self.has_font_class     = (flag & 0x80) == 0x80
        self.auto_size          = (flag & 0x40) == 0x40
        self.has_layout         = (flag & 0x20) == 0x20
        self.no_select          = (flag & 0x10) == 0x10

        self.border             = (flag & 0x8)  == 0x8
        self.static             = (flag & 0x4)  == 0x4
        self.html               = (flag & 0x2)  == 0x2
        self.outlines           = (flag & 0x1)  == 0x1

        if self.has_font:
            self.font_id = stream.readUI16()
        if self.has_font_class:
            self.font_name = stream.readString()
        if self.has_font:
            self.font_height = stream.readUI16()
        if self.has_text_color:
            self.text_color = RGBA()
            self.text_color.readRGBA(stream)
        if self.has_max_len:
            self.max_len = stream.readUI16()
        if self.has_layout:
            self.align_type = stream.readUI8()
            self.left_margin = stream.readUI16()
            self.right_margin = stream.readUI16()
            self.indent = stream.readUI16()
            self.leading = stream.readSI16()
            
        self.var_name = stream.readString()
        if self.has_text:
            self.init_text = stream.readString()
        
class FileAttributeLoader:
    tag_type = 69
    def __init__(self):
        pass
    
    def load(self, stream, tag_type, swf):
        attr = stream.readUI8()
        stream.readUIntBit(24)
        swf.has_metadata = attr & 0x10 != 0
        swf.is_avm2 = attr & 0x08 != 0
        swf.use_network = attr & 0x01 != 0
        DEBUG("load fileattribute meta="+str(swf.has_metadata)+",avm2="+str(swf.is_avm2)+",network="+str(swf.use_network));

class DefineFontAlignZones:
    tag_type = 73
    def __init__(self):
        pass
    
    def load(self, stream, tag_type, swf):
        self.font_id = stream.readUI16()
        flag = stream.readUI8()
        self.csm_table_hint = flag >> 6
        
        glyph_count = swf.getCharacter(self.font_id).num_glyphs

        self.zone_records = []
        for i in xrange(glyph_count):
            zr = ZoneRecord()
            zr.read(stream, swf)
            self.zone_records.append(zr)

class DefineFont3:
    tag_type = 75
    def __init__(self):
        self.font_id = 0
        self.has_layout = False
        self.shift_jis = False
        self.small_text = False
        self.ansi = False
        self.wide_offset = False
        self.wide_code = False
        self.italic = False
        self.bold = False
        self.lang_code = 0
        self.name = ""
        self.offset_table = []
        self.code_table_offset = 0
        self.glyph_table = []
        self.code_table = []
        
    def load(self, stream, tag_type, swf):
        self.font_id = stream.readUI16()

        swf.addCharacter(self.font_id, self)
        
        flag = stream.readUI8()
        self.has_layout = flag & (1 << 7) == (1 << 7)
        self.shift_jis = flag & (1 << 6) == (1 << 6)
        self.small_text = flag & (1 << 5) == (1 << 5)
        self.ansi = flag & (1 << 4) == (1 << 4)
        self.wide_offset = flag & (1 << 3) == (1 << 3)
        self.wide_code = flag & (1 << 2) == (1 << 2)
        self.italic = flag & (1 << 1) == (1 << 1)
        self.bold = flag & (1 << 0) == (1 << 0)

        self.lang_code = stream.readUI8()
        name_len = stream.readUI8()
        self.name = []
        for i in xrange(name_len):
            self.name.append(stream.readUI8())

        num_glyphs = self.num_glyphs = stream.readUI16()
        if self.wide_offset:
            for i in xrange(num_glyphs):
                self.offset_table.append(stream.readUI32())
            self.code_table_offset = stream.readUI32()
        else:
            for i in xrange(num_glyphs):
                self.offset_table.append(stream.readUI16())
            self.code_table_offset = stream.readUI16()
            
        for i in xrange(num_glyphs):
            shape = Shape()
            shape.read(stream)
            self.glyph_table.append(shape)
            
        for i in xrange(num_glyphs):
            self.code_table.append(stream.readUI16())
            
        if self.has_layout:
            self.ascent = stream.readSI16()
            self.descent = stream.readSI16()
            self.leading = stream.readSI16()

            self.advance_table = []
            for i in xrange(num_glyphs):
                self.advance_table.append(stream.readSI16())
                
            self.bounds_table = []
            for i in xrange(num_glyphs):
                bound = RECT()
                bound.read(stream)
                self.bounds_table.append(bound)

            kerning_count = stream.readUI16()
            self.kerning_table = []
            for i in xrange(kerning_count):
                kern = KerningRecord()
                kern.read(stream, self.wide_code)
                self.kerning_table.append(kern)
                
class SymbolClass:
    tag_type = 76
    def load(self, stream, tag_type, swf):
        num_symbols = stream.readUI16()
        for i in xrange(num_symbols):
            tag = stream.readUI16()
            name = stream.readString()
            
class DefineMetaDataLoader:
    tag_type = 77
    def __init__(self):
        pass
    def load(self, stream, tag_type, swf):
        value = stream.readString()
        D("load definemetadata value="+value)

class DoABC:
    tag_type = 82
    def load(self, stream, tag_type, swf):
        flag = stream.readUI32()
        name = stream.readString()
        abcData = stream.getLeftTagBytes()
        
class DefineSceneAndFrameLabelData:
    tag_type = 86
    def load(self, stream, tag_type, swf):
        self.scene_count = scene_count = stream.readEncodedU32()
        self.scenes = []
        for i in xrange(scene_count):
            offset = stream.readEncodedU32()
            name = stream.readString()
            self.scenes.append((offset, name))
            
        self.frame_label_count = frame_label_count = stream.readEncodedU32()
        self.frame_labels = []
        for i in xrange(frame_label_count):
            frame_num = stream.readEncodedU32()
            frame_label = stream.readString()
            self.frame_labels.append((frame_num, frame_label))

class DefineFontName:
    tag_type = 88
    def load(self, stream, tag_type, swf):
        font_id = stream.readUI16()
        font_name = stream.readString()
        font_copy_right = stream.readString()
        
class SWF:
    def __init__(self):
        self.characters = {}
        self.play_list = {}
        self.loading_frame = 0
        self.play_list[self.loading_frame] = []
        self.bitmap_characters = {}
        self.tag_loader = {}
        self.regTagLoader()
        
    def regTagLoader(self):
        self.tag_loader[FileAttributeLoader.tag_type] = FileAttributeLoader()
        self.tag_loader[EndLoader.tag_type] = EndLoader()
        self.tag_loader[ShowFrameLoader.tag_type] = ShowFrameLoader()
        self.tag_loader[DefineShapeLoader.tag_type] = DefineShapeLoader()
        self.tag_loader[DefineMetaDataLoader.tag_type] = DefineMetaDataLoader()
        self.tag_loader[SetBackgroundColorLoader.tag_type] = SetBackgroundColorLoader()
        self.tag_loader[PlaceObject2Loader.tag_type] = PlaceObject2Loader()
        self.tag_loader[DefineBitsLossLess2Loader.tag_type] = DefineBitsLossLess2Loader()
        self.tag_loader[DefineBitsLossLess2Loader.tag_type2] = DefineBitsLossLess2Loader()
        self.tag_loader[DefineFont3.tag_type] = DefineFont3()
        self.tag_loader[DefineFontAlignZones.tag_type] = DefineFontAlignZones()
        self.tag_loader[DefineEditText.tag_type] = DefineEditText()
        self.tag_loader[DefineSceneAndFrameLabelData.tag_type] = DefineSceneAndFrameLabelData()
        self.tag_loader[DefineFontName.tag_type] = DefineFontName()
        self.tag_loader[DefineText.tag_type] = DefineText()
        self.tag_loader[DefineText.tag_type2] = DefineText()
        self.tag_loader[DoABC.tag_type] = DoABC()
        self.tag_loader[SymbolClass.tag_type] = SymbolClass()
        self.tag_loader[DefineButton.tag_type] = DefineButton()
        self.tag_loader[DefineButton.tag_type2] = DefineButton()
        
    def read(self, stream):
        self.compress = compress = stream.readChar()
        DEBUG("compress "+swf.compress)
        
        w = stream.readChar()
        if 'W' != w:
            DEBUG("signature not W")
            sys.exit(1)
        else:
            DEBUG("W")
            
        s = stream.readChar()
        if 'S' != s:
            DEBUG("signature not S")
            sys.exit(1)
        else:
            DEBUG("S")

        self.version = version = stream.readUI8()
        DEBUG("version "+str(self.version))
        self.fileLen = fileLen = stream.readUI32()
        DEBUG("fileLen "+str(self.fileLen))

        self.file_end_pos = self.fileLen
        if 'C' == compress:
            stream.decompress()
            DEBUG("stream decompress")
            self.file_end_pos = self.fileLen - 8
        else:
            DEBUG("stream not decompress")
        
        self.frame_size = RECT()
        self.frame_size.read(stream)
        self.frame_rate = stream.readUI16()/256
        self.frame_count = stream.readUI16()
        if self.frame_count < 1:
            self.frame_count = 1
        DEBUG("framerate="+str(self.frame_rate)+",framecount="+str(self.frame_count))
        self.readTags(stream)

    def readTags(self, stream):
        while stream.getPos() < self.file_end_pos:
            tag_type = stream.openTag()
            if tag_type == 1:
                self.incLoadingFrame()
                DEBUG("show_frame")
            
            if self.tag_loader.has_key(tag_type):
                try:
                    self.tag_loader[tag_type].load(stream, tag_type, self)
                except Exception, e:
                    D("<!!!!!!!!>"+str(e)+"<!>")
            else:
                DEBUG("<!!!!!!!!>no loader for tag="+str(tag_type)+"<!>")
                break
            stream.closeTag()
            
            if tag_type == 0:
                if stream.getPos() != self.file_end_pos:
                    DEBUG("tag_type=0, pos!=end pos")
    
    def addBitmapCharacter(self, ch_id, character):
        self.bitmap_characters[ch_id] = character
        # add bitmap info list
        # self.bitmap_list.push(character)
        
    def addCharacter(self, ch_id, character):
        self.characters[ch_id] = character

    def getCharacter(self, ch_id):
        return self.characters[ch_id]
    
    def addExecuteTag(self, tag):
        self.play_list[self.loading_frame].append(tag)

    def incLoadingFrame(self):
        self.loading_frame += 1
        self.play_list[self.loading_frame] = []
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    else:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            DEBUG(filename+" does not exist")
            sys.exit(1)

        swf = SWF()
        stream = Stream(filename)
        swf.read(stream)
