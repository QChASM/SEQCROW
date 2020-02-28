# ChimAARON
AaronTools plug-in for Chimera

Almost all of the functionality added by ChimAARON is based on our AaronTools package for Python 3. 
The AaronTools installation that comes with ChimAARON is compatible with Python 2, which is what Chimera uses. 

# Tools and Features
## Browse AaronTools Libraries <img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/Icons/AaronTools_Libraries.png">

This tool allows you to browse the <a href="https://github.com/QChASM/AaronTools/wiki#libraries">AaronTools Libraries</a>. You can easily load in any ligands, substituents, and ring fragments. Ligands can be sorted by name, denticity, and coordinating elements. Substituents can be sorted by name and conformer information. 

<img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/helpdir/images/ligandLibrary.png">

## AARON Input <img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/Icons/AARON_Input.png">

Create an <a href="https://github.com/QChASM/Aaron/wiki/More-on-AARON-Input-Files">AARON input file</a> using loaded models. 

<img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/helpdir/images/aaronInputDialog%20filled%20in.png">

## Visualize Normal Modes <img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/Icons/normalModes.png">

Load in a Gaussian output file for a frequency job and display the normal modes as vectors or as an animation.

<img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/helpdir/images/normalModes.png">

## Structure Modification <img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/Icons/mapLigand.png">

Swap a ligand, add or change a functional group, and close a ring.

# Installation  
## Adding the ChimAARON Plugin

<b>NOTE</b> - you may experience some issues using ChimAARON if AaronTools is installed in a cloud-synced directory, like a Dropbox folder.


1. To add ChimAARON as a Chimera plugin, go to Tools &rarr; Additional Tools</span> &rarr; Add third-party plugin location...
    * This will open a dialog menu, in the bottom half of which you can specify the location of plugin folder
2. Press Add... and navigate your way to the directory containing your ChimAARON and AaronTools directories (<i>e.g.</i> 'plugins' for /home/CoolUser/plugins/AaronTools and /home/CoolUser/plugins/ChimAARON)
    * Pressing Open will add that location to the "Third-party plugin locations" box
    * Check to make sure the location is set correctly (for our CoolUser example, you'd see "&bull; plugins - /home/CoolUser" or "&bull; /home/CoolUser/plugins" depending on a setting in your <span class="menulike">General Preferences</span>)
    * Make sure to press Save

Chimera is now able to discover AaronTools and ChimAARON. 
Now, we just need some AaronTools dependencies.

### Installing Dependencies

<b>
If you installed Chimera in a directory that requires administrator/root privileges to modify, you'll need to run Chimera as an administrator/super user for this.
</b>


We use `future` to make AaronTools compatible with Chimera's Python 2. 
If you're comfortable installing this manually, feel free to do so. 
A simpler option is to go through ChimAARON. 
Go to Tools &rarr; ChimAARON &rarr; Set up AaronTools.

You will see a dialog menu with buttons that simplify the setup process.


<img src="https://github.com/QChASM/ChimAARON/blob/Chimera/ChimAARON/helpdir/images/setupHelper.png">

ChimAARON utilizes pip to install any AaronTools dependencies, so first you'll want to press "<span class="buttonlike">install pip with ensurepip and update pip</span>". 
Check Chimera's reply log to make sure pip was installed and/or updated to the newest version. 

Once you've got pip, press "<span class="buttonlike">install dependencies</span>" to install and `future`.

## Setup
### Personal Library 

To specify the location of your personal AaronTools library, press set AARONLIB location. This will open a directory explorer. Navigate to your personal library directory and select it. You will have to restart Chimera before using your personal library. 

## Back Porting AaronTools

<b>
If you are using the AaronTools installation that comes with ChimAARON, you should not need to do this
</b>

We use the pasteurize script that comes with `future` to fix most of AaronTools' compatibility issues between Python 2 and 3. 
To run this script on AaronTools, press pasteurize AaronTools. 
Monitor Chimera's reply log to make sure this finishes without issue. 

Once pasteurize finishes, we still need to fix a couple of things that pasteurize doesn't catch. 
Simply press "fix misc. backporting".

Now you should just have to restart Chimera for all of the ChimAARON tools to start functioning!

## Other Versions
### ChimeraX
#### Stable
The ChimeraX version of ChimAARON can be found on the [master branch](https://github.com/QChASM/ChimAARON/tree/master).

#### Daily
For the latest features and bugs, go to the [development branch](https://github.com/QChASM/ChimAARON/tree/dev)
