def load(self, context, filepath, gameVersion, linkFormat):
    pathOne = filepath
    if(gameVersion == 'WALL-E'):
        from . import mesh_z_wall_e as mesh_z
    else:
        from . import mesh_z_rat as mesh_z
    mesh_z.loadOne(pathOne, linkFormat)
    return True