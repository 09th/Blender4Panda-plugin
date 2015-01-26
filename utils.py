import bpy

def pnt2line(pnt, start, end):
    line_vec = end - start
    pnt_vec =  pnt - start
    #line_len = length(line_vec)
    line_unitvec = line_vec.normalized()
    pnt_vec_scaled = pnt_vec * 1.0/line_vec.length
    t = line_unitvec.dot(pnt_vec_scaled)
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    nearest = line_vec * t
    dist = (pnt_vec-nearest).length
    nearest = nearest + start
    #return (dist, nearest)
    return dist

def delete_recursive(ob,t=0):
    if t == 0:
        for object in bpy.context.selected_objects:
            object.select = False
        bpy.context.scene.objects.active = ob    
    ob.select = True
    for child in ob.children:
        delete_recursive(child,1)    
    bpy.ops.object.delete(use_global=False)
