def load(self, context, filepath, gameVersion):
    pathOne = filepath
    if(gameVersion == 'Wall-E'):
        from . import mesh_z_wall_e as mesh_z
    else:
        from . import mesh_z_rat as mesh_z
    mesh_z.loadOne(pathOne)
    return True