
import sys



class ACFormatError(Exception): pass

class ACLoader:
  def __init__(self, name):
    self.materials = []
    self.objects = []
    self.file = file(name)

    if not self.file.readline().strip() == "AC3Db":
      raise ACFormatError("File is not an AC3D file")

    for line in self.file:
      line = line.strip()
      if not self.__parseMaterial(line):
        obj = self.__parseObject(line)
        if obj:
          self.objects.append(obj)
        else:
          raise ACFormatError("Error: Expecting material or object")

  def __parseMaterial(self, line):
    """Parse MATERIAL data from a given line, if it is there"""
    if line.startswith('MATERIAL'):
      parts = line.split()

      if not (parts[2] == 'rgb' and parts[6] == 'amb' and parts[10] == 'emis' and 
              parts[14] == 'spec' and parts[18] == 'shi' and parts[20] == 'trans'):
        raise ACFormatError("Material missing lighting components")

      self.materials.append({
        'name' : parts[1].strip('"'),
        'rgb'  : tuple([float(x) for x in parts[3:6]]),
        'amb'  : tuple([float(x) for x in parts[7:10]]),
        'emis' : tuple([float(x) for x in parts[11:14]]),
        'spec' : tuple([float(x) for x in parts[15:18]]),
        'shi'  : int(parts[19]),
        'trans': float(parts[21]),
      });
      return True

  def __parseObject(self, line):
    """Parse an AC3D object from the line and following lines in the file"""
    if line.startswith('OBJECT'):
      obj = { 'type': line.split()[1], 'loc': (0.0, 0.0, 0.0) , 'verts': [], 'surfaces': [] }
      for line in self.file:
        line = line.strip()
        if line.startswith('name'):
          obj['name'] = line.split(' ', 1)[1].strip('"')
        elif line.startswith('data'):
          num = int(line.split(' ', 1)[1])
          obj['data'] = self.file.read(num)
        elif line.startswith('texture'):
          obj['texture'] = line.split(' ', 1)[1].strip('"')
        elif line.startswith('texrep'):
          obj['texrep'] = tuple([float(x) for x in line.split()[1:3]])
        elif line.startswith('rot'):
          nums = [float(x) for x in line.split()[1:]]
          obj['rot'] = (tuple(nums[0:3]), tuple(nums[3:6]), tuple(nums[6:9]))
        elif line.startswith('loc'):
          obj['loc'] = tuple([float(x) for x in line.split()[1:4]])
        elif line.startswith('url'):
          obj['url'] = line.split(' ', 1)[1]
        elif line.startswith('numvert'):
          obj['verts'] = self.__parseVerts(int(line.split(' ', 1)[1]))
        elif line.startswith('numsurf'):
          obj['surfaces'] = self.__parseSurfaces(int(line.split()[1]))
        elif line.startswith('kids'):
          obj['kids'] = self.__parseObjects(int(line.split(' ', 1)[1]))
          break

      return obj

  def __parseSurface(self):
    """Read surface data from the current line"""
    header = self.file.next()
    if not header.startswith('SURF'):
      raise ACFormatError("Missing surface header")

    surf = { 'type': int(header.split()[1], 16) }

    line = self.file.next()
    if line.startswith('mat'):
      surf['mat'] = int(line.split()[1])
      surf['material'] = self.materials[surf['mat']]
      line = self.file.next()
    if line.startswith('refs'):
      refs = []
      for i in range(int(line.split()[1])):
        nums = self.file.next().split()
        refs.append((int(nums[0]), float(nums[1]), float(nums[2])))
      surf['refs'] = refs
    else:
      raise ACFormatError('Missing surface refs')

    return surf

  def __parseVerts(self, num):
    """Parse vertices"""
    verts = []
    for i in range(num):
      verts.append(tuple([float(x) for x in self.file.next().strip().split()]))

    return verts

  def __parseSurfaces(self, num):
    """Parse surfaces"""
    surfs = []
    for line in range(num):
      surfs.append(self.__parseSurface())

    return surfs

  def __parseObjects(self, num):
    """Parse all objects"""
    objs = []
    for i in range(num):
      objs.append(self.__parseObject(self.file.next()))
    return objs

if __name__ == "__main__":
  if (len(sys.argv) != 2):
    print "Usage: acloader.py <filename>"
    sys.exit(0)

  print "Loading %s" % sys.argv[1]
  tmp = ACLoader(sys.argv[1])
  print "Loaded properly"

  import pprint
  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(tmp.objects)
