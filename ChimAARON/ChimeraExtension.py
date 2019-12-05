import chimera
import ChimAARON
import os

from chimera.extension import EMO, manager
from Midas.midas_text import addCommand
from ChimAARON.prefs import ENVIRONMENT

envPrefs = chimera.preferences.preferences.get('ChimAARON', ENVIRONMENT)
if 'AARONLIB' in envPrefs:
    os.environ['AARONLIB'] = envPrefs['AARONLIB']

try:
    from AaronTools.fileIO import read_types
    
    # -------------
    # Nice-to-haves
    # -------------
    
    # open AaronTools-readable files
    def openAaronTools(filename):
        """open a file format that is supported by AaronTools"""
        from ChimAARON import AaronGeometry2ChimeraMolecule
        from AaronTools.geometry import Geometry
        from AaronTools.fileIO import FileReader
        
        #this doesn't work unless we go through a FileReader first - why?
        geom = Geometry(FileReader(filename))
        m = AaronGeometry2ChimeraMolecule(geom)
        return [m]
            
    chimera.fileInfo.register("AaronTools coordinate", openAaronTools, ['.'+filetype for filetype in read_types], ['AaronTools' for filetype in read_types], category=chimera.FileInfo.STRUCTURE)

except:
    pass


# ----------
# Menu Stuff
# ----------

class Frequency_Dialog_EMO(EMO):
    def name(self):
        return 'Visualize Normal Mode...'
    
    def description(self):
        return self.categoryDescriptions()['ChimAARON']
    
    def categories(self):
        return self.categoryDescriptions().keys()
        
    def categoryDescriptions(self):
        return {'ChimAARON':'Visualize Normal Mode...'}
        
    def icon(self):
        return self.path('Icons/normalModes.png')
        
    def activate(self):
        from ChimAARON.NormalModeDialog import FreqFileLoader
        
        dialog = FreqFileLoader()
        
class Library_Dialog_EMO(EMO):

    def name(self):
        return 'AaronTools Libraries'
        
    def description(self):
        return self.categoryDescriptions()['ChimAARON']
        
    def categories(self):
        return self.categoryDescriptions().keys()
        
    def categoryDescriptions(self):
        return {'ChimAARON':'Libraries'}
        
    def icon(self):
        return self.path('Icons/AaronTools_Libraries.png')
        
    def activate(self):
        from ChimAARON.LibraryDialog import LibraryDialogMenu
        dialog = LibraryDialogMenu()

class AARON_Input_Dialog_EMO(EMO):
    def name(self):
        return "Set up AARON Input..."
        
    def description(self):
        return self.categoryDescriptions()['ChimAARON']
        
    def categories(self):
        return self.categoryDescriptions().keys
        
    def categoryDescriptions(self):
        return {'ChimAARON':self.name()}
    
    def icon(self):
        return self.path('Icons/AARON_Input.png')
        
    def activate(self):
        from ChimAARON.AARONInputDialog import InputGenerator_templateSelector
        dialog = InputGenerator_templateSelector()

class GetAaronTools_EMO(EMO):
    def name(self):
        return "Set up AaronTools"
    
    def description(self):
        return self.categoryDescriptions()['ChimAARON']
    
    def categories(self):
        return self.categoryDescriptions.keys()
    
    def categoryDescriptions(self):
        return {'ChimAARON':self.name()}
        
    def icon(self):
        return None
        
    def activate(self):
        from ChimAARON.GetAaronTools import GetAaronToolsDialog
        dialog = GetAaronToolsDialog()

class StructureModification_EMO(EMO):
    def name(self):
        return "Modify structure"
        
    def description(self):
        return self.categoryDescriptions()['ChimAARON']
        
    def categories(self):
        return self.categoryDescriptions().keys
        
    def categoryDescriptions(self):
        return {'ChimAARON':self.name()}
    
    def icon(self):
        return self.path('Icons/mapLigand.png')
        
    def activate(self):
        from ChimAARON.StructureModification import StructureModificationDialog
        dialog = StructureModificationDialog()

class LibAdd_EMO(EMO):
    def name(self):
        return "Add to AaronTools Library"
        
    def description(self):
        return self.categoryDescriptions()['ChimAARON']
        
    def categories(self):
        return self.categoryDescriptions().keys
        
    def categoryDescriptions(self):
        return {'ChimAARON':self.name()}
    
    def icon(self):
        return self.path('Icons/addToLib.png')
        
    def activate(self):
        from ChimAARON.LibraryDialog import LibAddDialog
        dialog = LibAddDialog()

manager.registerExtension(Frequency_Dialog_EMO(__file__))
manager.registerExtension(Library_Dialog_EMO(__file__))
manager.registerExtension(AARON_Input_Dialog_EMO(__file__))
manager.registerExtension(StructureModification_EMO(__file__))
manager.registerExtension(LibAdd_EMO(__file__))

manager.registerExtension(GetAaronTools_EMO(__file__))

# --------
# Commands
# --------

# print coordinates in XYZ format to reply log
def cmd_printXYZ(cmdName, sel):
    """print XYZ file to reply log"""
    from ChimAARON import doPrintXYZ
    
    doPrintXYZ(cmdName, sel)

# label atoms according to AARON relative numbering
def cmd_AARON_SCL(cmdName, args):
    from ChimAARON import doAARON_SCL
    
    doAARON_SCL(cmdName, args)
    
# substitute equivalent
def cmd_Substitute(cmdName, args):
    """make substitution and open a new model"""
    from ChimAARON import doSubstitute
    from chimera import openModels
    
    new_mols, close_mols = doSubstitute(cmdName, args)

    openModels.close(close_mols)

    for mol in new_mols:
        openModels.add([mol])

# closering equivalent
def cmd_CloseRing(cmdName, args):
    """close the selected ring"""
    from ChimAARON import doCloseRing
    from chimera import openModels

    new_mols, close_mols = doCloseRing(cmdName, args)

    openModels.close(close_mols)
    
    for mol in new_mols:
        openModels.add([mol])

# follow equivalent
def cmd_Follow(cmdName, args):
    """load frequency job as an animation"""
    from ChimAARON import doFollow
    
    doFollow(cmdName, args)

# printFreqBild equivalent
def cmd_FreqBild(cmdName, args):
    """grab a normal mode from the file and open displacement vectors"""
    from ChimAARON import doFreqBild
    
    doFreqBild(cmdName, args)

# mapLigand equivalent
def cmd_MapLigand(cmdName, args):
    """change one ligand for another"""
    from ChimAARON import doMapLigand
    from chimera import openModels
    
    new_mols, close_mols = doMapLigand(cmdName, args)
    
    openModels.close(close_mols)
    
    for mol in new_mols:
        openModels.add([mol])

# rmsd_align equivalent
def cmd_RmsdAlign(cmdName, args):
    """rmsd aligns things to other things"""
    from ChimAARON import doRmsdAlign
    
    doRmsdAlign(cmdName, args)

# draw a bond for a TSS
def cmd_TSBond(cmdName, arg_str):
    from ChimAARON import doTSBond
    
    doTSBond(cmdName, arg_str)

# load all structures in a file as a movie
def cmd_AllGeom(cmdName, arg_str):
    from ChimAARON import doAllGeom
    
    doAllGeom(cmdName, arg_str)

#AARON Input file record manager
def cmd_ArnRecord(cmdName, arg_str):
    from ChimAARON import doArnRecord
    
    doArnRecord(cmdName, arg_str)

addCommand("allgeom", cmd_AllGeom, help=("commands/allgeom.html", ChimAARON))
addCommand("arninp", cmd_ArnRecord, help=("commands/arninp.html", ChimAARON))
addCommand("arnscl", cmd_AARON_SCL, help=("commands/arnscl.html", ChimAARON))
addCommand("closering", cmd_CloseRing, help=("commands/closering.html", ChimAARON))
addCommand("follow", cmd_Follow, help=("commands/follow.html", ChimAARON))
addCommand("freqvec", cmd_FreqBild, help=("commands/freqvec.html", ChimAARON))
addCommand("mapligand", cmd_MapLigand, help=("commands/mapligand.html", ChimAARON))
addCommand("printxyz", cmd_printXYZ, help=("commands/printXYZ.html", ChimAARON))
addCommand("rmsdalign", cmd_RmsdAlign, help=("commands/rmsdalign.html", ChimAARON))
addCommand("substitute", cmd_Substitute, help=("commands/substitute.html", ChimAARON))
addCommand("tsbond", cmd_TSBond, help=("commands/tsbond.html", ChimAARON))

