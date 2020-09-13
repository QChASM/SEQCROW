import numpy as np

from chimerax.atomic import selected_atoms, selected_residues
from chimerax.core.commands import run
from chimerax.core.tools import ToolInstance
from chimerax.ui.gui import MainToolWindow
from chimerax.core.models import MODEL_ID_CHANGED, MODEL_NAME_CHANGED, ADD_MODELS
from chimerax.std_commands.coordset_gui import CoordinateSetSlider

from io import BytesIO

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QGridLayout, QPushButton, QTreeWidget, QWidget, QVBoxLayout, QTreeWidgetItem, QCheckBox

from SEQCROW.residue_collection import ResidueCollection
from SEQCROW.managers.filereader_manager import FILEREADER_CHANGE 
from SEQCROW.tools import EnergyPlot


class FileReaderPanel(ToolInstance):
    SESSION_ENDURING = False
    SESSION_SAVE = False         
    help = "https://github.com/QChASM/SEQCROW/wiki/Model-Manager-Tool"
    
    NAME_COL = 0
    ID_COL = 1
    COORDSETS_COL = 2
    NRG_COL = 3
    FREQ_COL = 4
    
    def __init__(self, session, name):       
        super().__init__(session, name)
        
        self.display_name = "SEQCROW Models"
        
        self.tool_window = MainToolWindow(self)        
        
        self._build_ui()
        self.fill_tree()
        
        self._fr_change = self.session.filereader_manager.triggers.add_handler(FILEREADER_CHANGE,
            lambda *args: self.fill_tree(*args))        
        self._add_models = self.session.triggers.add_handler(ADD_MODELS,
            lambda *args: self.fill_tree(*args))
        self._molid_change = self.session.triggers.add_handler(MODEL_ID_CHANGED,
            lambda *args: self.fill_tree(*args))
        self._molname_change = self.session.triggers.add_handler(MODEL_NAME_CHANGED,
            lambda *args: self.fill_tree(*args))
        
    def _build_ui(self):
        layout = QGridLayout()

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        #TODO: make buttons disabled/enabled if items are selected that don't have the info
        self.tree = QTreeWidget()
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree.setHeaderLabels(["Name", "ID", "movie", "energy", "frequencies"])
        self.tree.setUniformRowHeights(True)
        
        self.tree.setColumnWidth(self.NAME_COL, 200)
        layout.addWidget(self.tree, 0, 0, 3, 1)

        restore_button = QPushButton("restore")
        restore_button.clicked.connect(self.restore_selected)
        layout.addWidget(restore_button, 0, 1)
        
        nrg_plot_button = QPushButton("energy plot")
        nrg_plot_button.clicked.connect(self.open_nrg_plot)
        layout.addWidget(nrg_plot_button, 1, 1)
        
        coordset_slider_button = QPushButton("movie slider")
        coordset_slider_button.clicked.connect(self.open_movie_slider)
        layout.addWidget(coordset_slider_button, 2, 1)

        self.tool_window.ui_area.setLayout(layout)

        self.tool_window.manage(placement="side")
        
    def fill_tree(self, *args):        
        item_stack = [self.tree.invisibleRootItem()]
        
        self.tree.clear()
        self._items = []

        fr_dict = self.session.filereader_manager.filereader_dict

        for model in fr_dict.keys():
            id = model.id
            if id is None:
                continue
            
            name = model.name
            parent = item_stack[0]
            item = QTreeWidgetItem(parent)
            item._model = model
            item_stack.append(item)
            self._items.append(item)
            
            item.setData(self.NAME_COL, Qt.DisplayRole, model)
            item.setText(self.NAME_COL, name)
            item.setText(self.ID_COL, ".".join([str(x) for x in id]))
            
            if any(x.all_geom is not None and len(x.all_geom) > 1 for x in fr_dict[model]):
                item.setText(self.COORDSETS_COL, "yes")
            else:
                item.setText(self.COORDSETS_COL, "no")
                
            if any("energy" in x.other for x in fr_dict[model]):
                item.setText(self.NRG_COL, "yes")
            else:
                item.setText(self.NRG_COL, "no")
                
            if any("frequency" in x.other for x in fr_dict[model]):
                item.setText(self.FREQ_COL, "yes")
            else:
                item.setText(self.FREQ_COL, "no")
        
            for fr in fr_dict[model]:
                child = QTreeWidgetItem(item)
                child.setData(self.NAME_COL, Qt.DisplayRole, fr)
                child.setText(self.NAME_COL, fr.name)
                if fr.all_geom is not None and len(fr.all_geom) > 1:
                    child.setText(self.COORDSETS_COL, "yes")
                else:
                    child.setText(self.COORDSETS_COL, "no")
                    
                if "energy" in fr.other:
                    child.setText(self.NRG_COL, "%.6f" % fr.other["energy"])
                else:
                    child.setText(self.NRG_COL, "")
                    
                if "frequency" in fr.other:
                    child.setText(self.FREQ_COL, "yes")
                else:
                    child.setText(self.FREQ_COL, "no")    
            
            #self.tree.expandItem(item)
    
        for i in [self.ID_COL, self.COORDSETS_COL, self.NRG_COL, self.FREQ_COL]:
            self.tree.resizeColumnToContents(i)
   
    def restore_selected(self):
        items = [item for item in self.tree.selectedItems()]
        model_dict = self.session.filereader_manager.filereader_dict
        models = list(model_dict.keys())
        for item in items:
            parent = item.parent()
            mdl = models[self.tree.indexOfTopLevelItem(parent)]
            if parent is None:
                fr = model_dict[mdl][-1]
            else:
                fr = model_dict[mdl][parent.indexOfChild(item)]

            fr_rescol = ResidueCollection(fr)
            fr_rescol.update_chix(mdl)
            if fr.all_geom is not None and len(fr.all_geom) > 1:
                coordsets = fr_rescol.all_geom_coordsets(fr)

                mdl.remove_coordsets()
                mdl.add_coordsets(coordsets)

                for i, coordset in enumerate(coordsets):
                    mdl.active_coordset_id = i + 1
                    
                    for atom, coord in zip(mdl.atoms, coordset):
                        atom.coord = coord
                
                mdl.active_coordset_id = 1

    def open_nrg_plot(self):
        items = [item for item in self.tree.selectedItems()]
        model_dict = self.session.filereader_manager.filereader_dict
        models = list(model_dict.keys())
        for item in items:
            parent = item.parent()
            mdl = models[self.tree.indexOfTopLevelItem(parent)]
            if parent is None:
                fr = model_dict[mdl][-1]
            else:
                fr = model_dict[mdl][parent.indexOfChild(item)]

            EnergyPlot(self.session, mdl, fr)
    
    def open_movie_slider(self):
        items = [item for item in self.tree.selectedItems()]
        model_dict = self.session.filereader_manager.filereader_dict
        models = list(model_dict.keys())
        for item in items:
            parent = item.parent()
            mdl = models[self.tree.indexOfTopLevelItem(parent)]
            #coordset doesn't start out with the current coordset id
            #it looks like it should, but it doesn't
            #it starts at 1 instead
            slider = CoordinateSetSlider(self.session, mdl)
            slider.set_slider(mdl.active_coordset_id)
            #run(self.session, "coordset slider %s" % mdl.atomspec)
    
    def display_help(self):
        """Show the help for this tool in the help viewer."""
        from chimerax.core.commands import run
        run(self.session,
            'open %s' % self.help if self.help is not None else "")
    
    def delete(self):
        """overload delete"""
        self.session.filereader_manager.triggers.remove_handler(self._fr_change)
        self.session.triggers.remove_handler(self._add_models)
        self.session.triggers.remove_handler(self._molid_change)
        self.session.triggers.remove_handler(self._molname_change)
        super().delete()
