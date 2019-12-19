from math       import radians
from random     import random, seed
from mathutils  import Vector,Matrix

import bpy


from bpy.props import   FloatProperty,              \
                        FloatVectorProperty,        \
                        IntProperty,                \
                        StringProperty,             \
                        BoolProperty,               \
                        EnumProperty

from .lsystem import Turtle, Edge, Quad, BObject, Meta

def nupdate(self, context):

    for n in range(self.nproductions):
        namep = 'prod' + str(n+1)
        namem = 'mod' + str(n+1)
        nameq = 'prob' + str(n+1)

        try:
            s = getattr(self, namep)
        except AttributeError:
            setattr(self.__class__, namep,
                            StringProperty(
                                name=namep,
                                description="replacement string")
            )
        try:
            s = getattr(self, namem)
        except AttributeError:
            setattr(self.__class__, namem,
                            StringProperty(
                                name=str(n+1),
                                description="a single character module, but mighty fine",
                                maxlen=1)
            )
        try:
            s = getattr(self, nameq)
        except AttributeError:
            setattr(self.__class__, nameq, 
                            FloatProperty(name='prob' + str(n+1), 
                            min=0.0, 
                            max=1.0, 
                            default=1.0)
            )

class meahcci_OT_add_meahcci(bpy.types.Operator):
    bl_idname = "mesh.add_meahcci"
    bl_label = "Meahcci"
    bl_description = "Grow me a forest"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    nproductions: IntProperty(
        name="productions",
        min=0,
        max=50,
        update=nupdate)

    niterations: IntProperty(
        name="iterations",
        min=0,
        max=15)

    seed: IntProperty(name="seed")

    start: StringProperty(
            name='start',
            default="F"
        )

    angle: FloatProperty(
        name='angle',
        default=radians(30),
        subtype='ANGLE',
        description="size in degrees of angle operators")

    tropism: FloatVectorProperty(
        name='tropism',
        subtype='DIRECTION',
        default=(0.0, 0.0, -1.0),
        description="direction of tropism")

    tropismsize: FloatProperty(
        name='tropism size',
        description="size of tropism")

    smooth_operator: BoolProperty(
            name='smooth_operator',
            default=False
        )

    meta_type: EnumProperty(
        name="meta_type",
        description="Metaball canopy rendering",
        items=[
            ('CUBE', 'Cube', '', 'META_CUBE', 1),
            ('BALL', 'Ball', '', 'META_BALL', 2)
        ],
        default='BALL'
    )

    meta_resolution: FloatProperty(
        name='meta_resolution',
        default=0.2,
        description="Resolution of metaballs")
    
    meta_radius: FloatProperty(
        name='meta_radius',
        default=10.0,
        description="relative radius of metaballs")
    
    # Forestry properties
    ngenerations: IntProperty(
            name='ngenerations',
            description="number of generations",
            min=1,
            max=10,
            default=1
        )

    nspecimen: IntProperty(
            name='nspecimen',
            description="number of specimen",
            min=1,
            max=10,
            default=1
        )

    gridstep: FloatProperty(
            name='gridstep',
            description="distance between trees",
            min=0.0,
            default=1.0,
            subtype='DISTANCE'
        )

    # Mehods are really not supposed to be here.
   
    def iterate(self):
        class ldict(dict):
            def __missing__(self, key):
                return key, 2.0
        
        seed(self.seed)
        s = self.start

        prod = ldict()
        for i in range(self.nproductions):
            namep = 'prod' + str(i+1)
            namem = 'mod' + str(i+1)
            nameq = 'prob' + str(i+1)
            prod[getattr(self, namem)] = getattr(self, namep), getattr(self, nameq)
        for i in range(self.niterations):
            si = ""
            for c in s:
                if random() < prod[c][1]:
                    si += prod[c][0]
            s = si
        return s

    @staticmethod
    def add_obj(obdata, context):
        obj_new = bpy.data.objects.new(obdata.name, obdata)
        context.collection.objects.link(obj_new)
        return obj_new

    @staticmethod
    def add_obj_cpy(original, context):
        obj_new = original.copy()
        obj_new.data = original.data.copy()
        context.collection.objects.link(obj_new)
        return obj_new

    # interpretation:
    def interpret(self, s, context):
        q = None
        qv = ((0.5, 0, 0), (0.5, 1, 0), (-0.5, 1, 0), (-0.5, 0, 0))
        verts = []
        edges = []
        quads = []
        metas = []
        self.radii = []

        t = Turtle( self.tropism,
                    self.tropismsize,
                    self.angle,
                    self.seed)
        for e in t.interpret(s):
            if isinstance(e, Edge):
                si, ei = ( verts.index(v)
                            if v in verts
                            else (  len(verts),
                                    verts.append(v),
                                    self.radii.append(e.radius))[0]
                            for v in (e.start, e.end)
                        )
                edges.append((si, ei))
            elif isinstance(e, Quad):
                if q is None:
                    q = bpy.data.meshes.new('lsystem-leaf')
                    q.from_pydata(qv, [], [(0, 1, 2, 3)])
                    q.update()
                    q.uv_textures.new()
                obj = self.add_obj(q, context)
                
                r = Matrix()
                for i in (0, 1, 2):
                    r[i][0] = e.right[i]
                    r[i][1] = e.up[i]
                    r[i][2] = e.forward[i]
                obj.matrix_world = Matrix.Translation(e.pos)*r
                quads.append(obj)

            elif isinstance(e, BObject):
                if bpy.data.objects.get(e.name) is not None:
                    original = bpy.data.objects[e.name]
                elif bpy.data.objects.get('Cube') is not None:
                    original = bpy.data.objects['Cube']
                else:
                    bpy.ops.mesh.primitive_cube_add()
                    original = bpy.data.objects['Cube']

                obj = self.add_obj_cpy(original, context)
                
                r = Matrix()
                for i in (0, 1, 2):
                    r[i][0] = e.right[i]
                    r[i][1] = e.up[i]
                    r[i][2] = e.forward[i]
                obj.matrix_world = Matrix.Translation(e.pos)*r
                quads.append(obj)

            elif isinstance(e, Meta):
                metas.append(e)
            
        
            
        
        mesh = bpy.data.meshes.new('muorra')
        mesh.from_pydata(verts, edges, [])
        mesh.update()
        obj = self.add_obj(mesh, context)
        base = obj

        if len(metas) > 0:
            mball = bpy.data.metaballs.new('MetaBall')
            mball.resolution = self.meta_resolution
            o = bpy.data.objects.new('Meta_Obj', mball)
            context.collection.objects.link(o)

            for e in metas:
                this_ball = mball.elements.new()
                this_ball.type = self.meta_type
                this_ball.use_negative = False
                this_ball.radius = e.radius*self.meta_radius
                this_ball.co = e.pos + e.forward*this_ball.radius/2
            
            #bpy.context.scene.update()
            bpy.context.view_layer.update()
            m = o.to_mesh(preserve_all_data_layers=True)

            can_obj = bpy.data.objects.new('Canopy', m)
            for p in can_obj.data.polygons:
                p.use_smooth = False

            context.collection.objects.link(can_obj)
            context.collection.objects.unlinklink(o)
            #context.scene.objects.link(can_obj)
            #context.scene.objects.unlink(o)
            can_obj.parent = obj
            
            
            

#        for ob in context.scene.objects:
 #           ob.select_set(False)
  #      base.select_set(True)
   #     context.scene.objects.active = obj
        for q in quads:
            q.parent = base
        return base


    # Execution?
    def execute(self, context):

        start_gen = self.niterations
        start_seed = self.seed


        for m in range(0, self.nspecimen):
            self.seed = start_seed + m
            for n in range(0, self.ngenerations):
                self.niterations = start_gen + n
                s = self.iterate()
                obj = self.interpret(s, context)

                #bpy.context.active_object = obj
                context.view_layer.objects.active = obj
                bpy.ops.object.modifier_add(type='SKIN')
                obj.modifiers[0].use_smooth_shade = False
                obj.modifiers[0].use_x_symmetry = False
                #context.active_object.modifiers[0].use_smooth_shade = False
                #context.active_object.modifiers[0].use_x_symmetry = False

                skinverts = context.active_object.data.skin_vertices[0].data

                for i, v in enumerate(skinverts):
                    v.radius = [self.radii[i], self.radii[i]]

                if self.smooth_operator:
                    bpy.ops.object.modifier_add(type='SUBSURF')
                    context.active_object.modifiers[1].levels = 2

                context.active_object.location = (m*self.gridstep, n*self.gridstep, 0.0)

        self.niterations = start_gen
        self.seed = start_seed
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'nproductions')
        box = layout.box()
        if getattr(self, 'start') == '':
            box.alert = True
        box.prop(self, 'start')

        for i in range(self.nproductions):
            namep = 'prod' + str(i+1)
            namem = 'mod' + str(i+1)
            nameq = 'prob' + str(i+1)

            box = layout.box()
            row = box.row(align=True)
            if getattr(self, namem) == '' or \
                getattr(self, namep) == '':
                    row.alert = True
            row.prop(self, namem)
            row.prop(self, namep, text="")
            row.prop(self, nameq, text="frac")

        box = layout.box()
        box.label(text="Interpretation section")
        box.prop(self, 'niterations')
        box.prop(self, 'seed')
        box.prop(self, 'angle')
        box.prop(self, 'tropism')
        box.prop(self, 'tropismsize')
        
        box = layout.box()
        box.label(text="Fun with geometry")
        box.prop(self, 'meta_type')
        box.prop(self, 'meta_radius')
        box.prop(self, 'meta_resolution')
        box.prop(self, 'smooth_operator')
        #box.prop(self,'canopy_gravity')
        #box.prop(self,'canopy_scale')
        #box.prop(self,'canopy_height')

        box = layout.box()
        box.label(text="Family tree")
        box.prop(self, 'ngenerations')
        box.prop(self, 'nspecimen')
        box.prop(self, 'gridstep')