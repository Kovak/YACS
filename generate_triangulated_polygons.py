import triangle
from numpy import array
from math import pi, cos, sin
from random import randint

def triangulate_regular_polygon(sides, radius, pos, size):
        x, y = pos
        angle = 2 * pi / sides
        all_verts = []
        all_verts_a = all_verts.append
        r = radius
        for s in range(sides):
            new_pos = x + r * sin(s * angle), y + r * cos(s * angle)
            all_verts_a(new_pos)
        A = {'vertices':array(all_verts)}
        command = 'cqa' + size + 'YY'
        B = triangle.triangulate(A, command)
        tri_indices = B['triangles']
        new_indices = []
        new_vertices = {}
        tri_verts = B['vertices']
        new_ex = new_indices.extend
        ind_count = 0
        for tri in tri_indices:
            new_ex((tri[0], tri[1], tri[2]))
            ind_count += 3
        vert_count = 0
        for i, tvert in enumerate(tri_verts):
            new_vertices[i] = {
                'pos': [tvert[0], tvert[1]], 
                'v_color': [255, 255, 255, 255]
                }
            vert_count += 1
        return {'indices': new_indices, 'vertices': new_vertices, 
            'vert_count': vert_count, 'ind_count': ind_count}


def create_triangulated_polygon_model(
    model_manager, sides, radius, area, name
    ):
    t = triangulate_regular_polygon(sides,radius, (0., 0.), area)
    model_name = model_manager.load_model('vertex_format_2f4ub', 
        t['vert_count'], t['ind_count'], name, 
        indices=t['indices'], vertices=t['vertices'])
    return model_name

def generate_and_save_various_models(
    model_manager, radii=[], areas=[], sides=40
    ):
for radius in radii:
    for area in areas:
        name = 'circle_' + str(int(radius)) + '_' + area
        model_name = create_triangulated_polygon_model(
            model_manager, sides, radius, area, name
            )
        model_manager.pickle_model(model_name, 'triangulated_models')

def pregenerate_models(model_manager):
    generate_and_save_various_models(
        model_manager, radii=[100., 200.,], areas=['5', '10', '20']
        )
    generate_and_save_various_models(
        model_manager, radii=[400.], areas=['10', '20', '30'], sides=60
        )
    generate_and_save_various_models(
        model_manager, radii=[800.], areas=['25', '35', '50'], sides=100
        )