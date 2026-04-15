# Informações obrigatórias para o Blender 4.0 reconhecer o Add-on
bl_info = {
    "name": "Silence Remover for VSE",
    "author": "Sub",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "Video Sequencer > Sidebar",
    "description": "Remove silences from selected audio strips in the Video Sequencer",
    "category": "Sequencer",
}

import bpy
from . import ui, logic  # Importa seus outros arquivos da mesma pasta

def register():
    # Aqui chamaremos as funções de registro que criaremos nos outros arquivos
    ui.register()
    logic.register()

def unregister():
    ui.unregister()
    logic.unregister()

if __name__ == "__main__":
    register()