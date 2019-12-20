# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "meahcci",
    "author" : "jomik",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Add Mesh"
}

import bpy

from . meahcci_op    import meahcci_OT_add_meahcci

def add_object_button(self, context):
    self.layout.operator(
        meahcci_OT_add_meahcci.bl_idname,
        text="MEAHCCI!",
        icon='PLUGIN')

def register():
    bpy.utils.register_class(meahcci_OT_add_meahcci)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(meahcci_OT_add_meahcci)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)
