import os

from chimerax.core.toolshed import ProviderManager


class ClusterSchedulingSoftwareManager(ProviderManager):
    def __init__(self, session, *args, **kwargs):
        self.session = session
        self.queues = dict()
        
        super().__init__(*args, **kwargs)

    def add_provider(self, bundle_info, name):
        self.queues[name] = bundle_info
    
    def get_queue_manager(self, name):
        return self.queues[name].run_provider(
            self.session,
            name,
            self,
        )


class DefaultTemplateManager(ProviderManager):
    def __init__(self, session, *args, **kwargs):
        self.session = session
        self.templates = dict()
        
        super().__init__(*args, **kwargs)

    def add_provider(self, bundle_info, name):
        self.templates[name] = bundle_info
    
    def get_template(self, name):
        return self.templates[name].run_provider(
            self.session,
            name,
            self,
        )


class SlurmDefault(DefaultTemplateManager):
    pass


class SGEDefault(DefaultTemplateManager):
    pass


class PBSDefault(DefaultTemplateManager):
    pass


class LSFDefault(DefaultTemplateManager):
    pass


class ClusterSubmitTemplate:
    template = None
    
    def submit_job(
        self,
        input_path,
        walltime,
        processors,
        memory,
        template=None,
        template_kwargs=None,
    ):
        """
        submit the job in input_path to the cluster
        input_path - path to input file for a software package
        walltime, processors, memory, and kwargs are
        used to construct the execution instructions using
        the template
        do not return until the submission is complete
        """
        from AaronTools.job_control import SubmitProcess

        if template_kwargs is None:
            template_kwargs = dict()
        proc = SubmitProcess(
            input_path,
            walltime,
            processors,
            memory,
            template=template,
        )
        proc.submit(**template_kwargs, wait=False)


class ProgramSubmitTemplate:
    expected_input_ext = None
    expected_output_ext = None


class GaussianSubmit(ProgramSubmitTemplate):
    expected_input_ext = "com"
    expected_output_ext = "log"
    

class ORCASubmit(ProgramSubmitTemplate):
    expected_input_ext = "inp"
    expected_output_ext = "out"

class Psi4Submit(ProgramSubmitTemplate):
    expected_input_ext = "in"
    expected_output_ext = "out"


class QChemSubmit(ProgramSubmitTemplate):
    expected_input_ext = "in"
    expected_output_ext = "out"


class SQMSubmit(ProgramSubmitTemplate):
    expected_input_ext = "mdin"
    expected_output_ext = "sqmout"
    

class GaussianSlurmTemplate(ClusterSubmitTemplate, GaussianSubmit):
    template = """#!/bin/bash
#SBATCH --job-name={{ name }}
#SBATCH --partition {{ queue }}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={{ processors }}
#SBATCH --time={{ walltime }}:00
#SBATCH --mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the gaussian input file should have a .com extension
# the gaussian output file should have a .log extension

module purge

module load gaussian
export GAUSS_SCRDIR=/scratch/$USER/$PBS_JOBID
SCRATCH=$GAUSS_SCRDIR
mkdir -p $SCRATCH
cd $SCRATCH
cp $SLURM_SUBMIT_DIR/{{ name }}.com .
g16 {{ name }}.com $SLURM_SUBMIT_DIR/{{ name }}.log
if [ -e {{ name }}.chk ]; then
    formchk {{ name }}.chk {{ name }}.fchk
    cp {{ name }}.fchk $SLURM_SUBMIT_DIR
fi
cd $SLURM_SUBMIT_DIR
rm -rf $SCRATCH
exit"""


class ORCASlurmTemplate(ClusterSubmitTemplate, ORCASubmit):
    template = """#!/bin/bash
#SBATCH --job-name={{ name }}
#SBATCH --partition {{ queue }}
#SBATCH --ntasks={{ processors }}
#SBATCH --cpus-per-task=1
#SBATCH --time={{ walltime }}:00
#SBATCH --mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the orca input file should have a .inp extension
# the orca output file should have a .out extension

module purge

module load ORCA
export orcapath=`which orca`
SCRATCH=/scratch/$USER/$SLURM_JOB_ID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SLURM_SUBMIT_DIR/{{ name }}.inp .
$orcapath {{ name }}.inp > $SLURM_SUBMIT_DIR/{{ name }}.out
cd $SLURM_SUBMIT_DIR
rm -rf $SCRATCH
exit"""


class Psi4SlurmTemplate(ClusterSubmitTemplate, Psi4Submit):
    template = """#!/bin/bash
#SBATCH --job-name={{ name }}
#SBATCH --partition {{ queue }}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={{ processors }}
#SBATCH --time={{ walltime }}:00
#SBATCH --mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the psi4 input file should have a .in extension
# the psi4 output file should have a .out extension

module purge

module load psi4
SCRATCH=/scratch/$USER/$SLURM_JOB_ID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SLURM_SUBMIT_DIR/{{ name }}.in .
psi4 {{ name }}.in $SLURM_SUBMIT_DIR/{{ name }}.out
if [ -e {{ name }}.fchk ]; then
    cp {{ name }}.fchk $SLURM_SUBMIT_DIR
fi
cd $SLURM_SUBMIT_DIR
rm -rf $SCRATCH
exit"""


class QChemSlurmTemplate(ClusterSubmitTemplate, QChemSubmit):
    template = """#!/bin/bash
#SBATCH --job-name={{ name }}
#SBATCH --partition {{ queue }}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={{ processors }}
#SBATCH --time={{ walltime }}:00
#SBATCH --mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the q-chem input file should have a .in extension
# the q-chem output files should have a .out extension

module purge

module load qchem
SCRATCH=/scratch/$USER/$SLURM_JOB_ID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SLURM_SUBMIT_DIR/{{ name }}.inp .
qchem -np {{ processors }} {{ name }}.in $SLURM_SUBMIT_DIR/{{ name }}.out
cd $SLURM_SUBMIT_DIR
rm -rf $SCRATCH
exit"""


class SQMSlurmTemplate(ClusterSubmitTemplate, SQMSubmit):
    template = """#!/bin/bash
#SBATCH --job-name={{ name }}
#SBATCH --partition {{ queue }}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time={{ walltime }}:00
#SBATCH --mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads (sqm will not use more than 1 core)
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the sqm input file should have a .mdin extension
# the sqm output file should have a .sqmout extension

module purge

module load AmberTools
SCRATCH=/scratch/$USER/$SLURM_JOB_ID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SLURM_SUBMIT_DIR/{{ name }}.inp .
sqm -i {{ name }}.mdin -o $SLURM_SUBMIT_DIR/{{ name }}.sqmout
cd $SLURM_SUBMIT_DIR
rm -rf $SCRATCH
exit"""


class GaussianPBSTemplate(ClusterSubmitTemplate, GaussianSubmit):
    template = """#PBS -S /bin/bash
#PBS -N {{ name }}
#PBS -q {{ queue }}
#PBS -l nodes=1:ppn={{ processors }}
#PBS -l walltime={{ walltime }}:00
#PBS -l mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the gaussian input file should have a .com extension
# the gaussian output file should have a .log extension

module purge

module load gaussian
export GAUSS_SCRDIR=/scratch/$USER/$PBS_JOBID
SCRATCH=$GAUSS_SCRDIR
mkdir -p $SCRATCH
cd $SCRATCH
cp $PBS_O_WORKDIR/{{ name }}.com .
g16 {{ name }}.com $PBS_O_WORKDIR/{{ name }}.log
if [ -e {{ name }}.chk ]; then
    formchk {{ name }}.chk {{ name }}.fchk
    cp {{ name }}.fchk $PBS_O_WORKDIR
fi
cd $PBS_O_WORKDIR
rm -rf $SCRATCH
exit"""


class ORCAPBSTemplate(ClusterSubmitTemplate, ORCASubmit):
    template = """#PBS -S /bin/bash
#PBS -N {{ name }}
#PBS -q {{ queue }}
#PBS -l nodes=1:ppn={{ processors }}
#PBS -l walltime={{ walltime }}:00
#PBS -l mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the orca input file should have a .inp extension
# the orca output file should have a .out extension

module purge

module load ORCA
export orcapath=`which orca`
SCRATCH=/scratch/$USER/$PBS_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $PBS_O_WORKDIR/{{ name }}.inp .
$orcapath {{ name }}.inp > $PBS_O_WORKDIR/{{ name }}.out

cd $PBS_O_WORKDIR
rm -rf $SCRATCH
exit"""


class Psi4PBSTemplate(ClusterSubmitTemplate, Psi4Submit):
    template = """#PBS -S /bin/bash
#PBS -N {{ name }}
#PBS -q {{ queue }}
#PBS -l nodes=1:ppn={{ processors }}
#PBS -l walltime={{ walltime }}:00
#PBS -l mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the psi4 input file should have a .in extension
# the psi4 output file should have a .out extension

module purge

module load psi4
SCRATCH=/scratch/$USER/$PBS_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $PBS_O_WORKDIR/{{ name }}.in .
psi4 {{ name }}.in $PBS_O_WORKDIR/{{ name }}.out
if [ -e {{ name }}.fchk ]; then
    cp {{ name }}.fchk $PBS_O_WORKDIR
fi
cd $PBS_O_WORKDIR
rm -rf $SCRATCH
exit"""


class QChemPBSTemplate(ClusterSubmitTemplate, QChemSubmit):
    template = """#PBS -S /bin/bash
#PBS -N {{ name }}
#PBS -q {{ queue }}
#PBS -l nodes=1:ppn={{ processors }}
#PBS -l walltime={{ walltime }}:00
#PBS -l mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the q-chem input file should have a .in extension
# the q-chem output files should have a .out extension

module purge

module load qchem
SCRATCH=/scratch/$USER/$PBS_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $PBS_O_WORKDIR/{{ name }}.in .
qchem -np {{ processors }} {{ name }}.in $PBS_O_WORKDIR/{{ name }}.out
cd $PBS_O_WORKDIR
rm -rf $SCRATCH
exit"""


class SQMPBSTemplate(ClusterSubmitTemplate, SQMSubmit):
    template = """#PBS -S /bin/bash
#PBS -N {{ name }}
#PBS -q {{ queue }}
#PBS -l nodes=1:ppn=1
#PBS -l walltime={{ walltime }}:00
#PBS -l mem={{ memory }}gb

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads (sqm will not use more than 1 core)
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the sqm input file should have a .mdin extension
# the sqm output file should have a .sqmout extension

module purge

module load AmberTools
SCRATCH=/scratch/$USER/$PBS_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $PBS_O_WORKDIR/{{ name }}.in .
sqm -i {{ name }}.mdin -o $PBS_O_WORKDIR/{{ name }}.sqmout
cd $PBS_O_WORKDIR
rm -rf $SCRATCH
exit"""


class GaussianSGETemplate(ClusterSubmitTemplate, GaussianSubmit):
    template = """#!/bin/bash
#$ -N {{ name }}
#$ -q {{ queue }}
#$ -pe smp {{ processors }}
#$ -l s_rt={{ walltime }}:00:00
#$ -l s_vmem={{ memory }}G

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the gaussian input file should have a .com extension
# the gaussian output file should have a .log extension

module purge

module load gaussian
export GAUSS_SCRDIR=/scratch/$USER/$JOB_ID
SCRATCH=$GAUSS_SCRDIR
mkdir -p $SCRATCH
cd $SCRATCH
cp $SGE_O_WORKDIR/{{ name }}.com .
g16 {{ name }}.com $SGE_O_WORKDIR/{{ name }}.log
if [ -e {{ name }}.chk ]; then
    formchk {{ name }}.chk {{ name }}.fchk
    cp {{ name }}.fchk $SGE_O_WORKDIR
fi
cd $SGE_O_WORKDIR
rm -rf $SCRATCH
exit"""


class ORCASGETemplate(ClusterSubmitTemplate, ORCASubmit):
    template = """#!/bin/bash
#$ -N {{ name }}
#$ -q {{ queue }}
#$ -pe smp {{ processors }}
#$ -l s_rt={{ walltime }}:00:00
#$ -l s_vmem={{ memory }}G

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the ORCA input file should have a .inp extension
# the ORCA output file should have a .out extension

module purge

module load orca
SCRATCH=/scratch/$USER/$JOB_ID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SGE_O_WORKDIR/{{ name }}.inp .
orca {{ name }}.inp > $SGE_O_WORKDIR/{{ name }}.out

cd $SGE_O_WORKDIR
rm -rf $SCRATCH
exit"""


class Psi4SGETemplate(ClusterSubmitTemplate, Psi4Submit):
    template = """#!/bin/bash
#$ -N {{ name }}
#$ -q {{ queue }}
#$ -pe smp {{ processors }}
#$ -l s_rt={{ walltime }}:00:00
#$ -l s_vmem={{ memory }}G

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the Psi4 input file should have a .in extension
# the Psi4 output file should have a .out extension

module purge

module load psi4
SCRATCH=/scratch/$USER/$PBS_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SGE_O_WORKDIR/{{ name }}.in .
psi4 {{ name }}.in $SGE_O_WORKDIR/{{ name }}.out
if [ -e {{ name }}.fchk ]; then
    cp {{ name }}.fchk $SGE_O_WORKDIR
fi
cd $SGE_O_WORKDIR
rm -rf $SCRATCH
exit"""


class QChemSGETemplate(ClusterSubmitTemplate, QChemSubmit):
    template = """#!/bin/bash
#$ -N {{ name }}
#$ -q {{ queue }}
#$ -pe smp {{ processors }}
#$ -l s_rt={{ walltime }}:00:00
#$ -l s_vmem={{ memory }}G

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the q-chem input file should have a .in extension
# the q-chem output files should have a .out extension

module purge

module load qchem
SCRATCH=/scratch/$USER/$JOB_ID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SGE_O_WORKDIR/{{ name }}.in .
qchem -np {{ processors }} {{ name }}.in $SGE_O_WORKDIR/{{ name }}.out
cd $SGE_O_WORKDIR
rm -rf $SCRATCH
exit"""


class SQMSGETemplate(ClusterSubmitTemplate, SQMSubmit):
    template = """#!/bin/bash
#$ -N {{ name }}
#$ -q {{ queue }}
#$ -pe smp {{ processors }}
#$ -l s_rt={{ walltime }}:00:00
#$ -l s_vmem={{ memory }}G

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads (sqm will not use more than 1 core)
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the sqm input file should have a .mdin extension
# the sqm output file should have a .sqmout extension

module purge

module load AmberTools
SCRATCH=/scratch/$USER/$JOB_ID
mkdir -p $SCRATCH
cd $SCRATCH
cp $SGE_O_WORKDIR/{{ name }}.in .
sqm -i {{ name }}.mdin -o $SGE_O_WORKDIR/{{ name }}.sqmout
cd $SGE_O_WORKDIR
rm -rf $SCRATCH
exit"""


class GaussianLSFTemplate(ClusterSubmitTemplate, GaussianSubmit):
    template = """#BSUB -L /bin/bash
#BSUB -N {{ name }}
#BSUB -q {{ queue }}
#BSUB -n {{ processors }}
#BSUB -W {{ walltime }}:00
#BSUB -M {{ 1000000 * memory }}

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the gaussian input file should have a .com extension
# the gaussian output file should have a .log extension

module purge

module load gaussian
export GAUSS_SCRDIR=/scratch/$USER/$LSB_JOBID
SCRATCH=$GAUSS_SCRDIR
mkdir -p $SCRATCH
cd $SCRATCH
cp $LS_SUBCWD/{{ name }}.com .
g16 {{ name }}.com $LS_SUBCWD/{{ name }}.log
if [ -e {{ name }}.chk ]; then
    formchk {{ name }}.chk {{ name }}.fchk
    cp {{ name }}.fchk $LS_SUBCWD
fi
cd $LS_SUBCWD
rm -rf $SCRATCH
exit"""


class ORCALSFTemplate(ClusterSubmitTemplate, ORCASubmit):
    template = """#BSUB -L /bin/bash
#BSUB -N {{ name }}
#BSUB -q {{ queue }}
#BSUB -n {{ processors }}
#BSUB -W {{ walltime }}:00
#BSUB -M {{ 1000000 * memory }}

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the ORCA input file should have a .inp extension
# the ORCA output file should have a .out extension

module purge

module load orca
SCRATCH=/scratch/$USER/$LSB_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $LS_SUBCWD/{{ name }}.inp .
orca {{ name }}.inp > $LS_SUBCWD/{{ name }}.out

cd $LS_SUBCWD
rm -rf $SCRATCH
exit"""


class Psi4LSFTemplate(ClusterSubmitTemplate, Psi4Submit):
    template = """#BSUB -L /bin/bash
#BSUB -N {{ name }}
#BSUB -q {{ queue }}
#BSUB -n {{ processors }}
#BSUB -W {{ walltime }}:00
#BSUB -M {{ 1000000 * memory }}

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the Psi4 input file should have a .in extension
# the Psi4 output file should have a .out extension

module purge

module load psi4
SCRATCH=/scratch/$USER/$LSB_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $LS_SUBCWD/{{ name }}.in .
psi4 {{ name }}.in $LS_SUBCWD/{{ name }}.out
if [ -e {{ name }}.fchk ]; then
    cp {{ name }}.fchk $LS_SUBCWD
fi
cd $LS_SUBCWD
rm -rf $SCRATCH
exit"""


class QChemLSFTemplate(ClusterSubmitTemplate, QChemSubmit):
    template = """#BSUB -L /bin/bash
#BSUB -N {{ name }}
#BSUB -q {{ queue }}
#BSUB -n {{ processors }}
#BSUB -W {{ walltime }}:00
#BSUB -M {{ 1000000 * memory }}

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the q-chem input file should have a .in extension
# the q-chem output files should have a .out extension

module purge

module load qchem
SCRATCH=/scratch/$USER/$LSB_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $LS_SUBCWD/{{ name }}.in .
qchem -np {{ processors }} {{ name }}.in $LS_SUBCWD/{{ name }}.out
cd $LS_SUBCWD
rm -rf $SCRATCH
exit"""


class SQMLSFTemplate(ClusterSubmitTemplate, SQMSubmit):
    template = """#BSUB -L /bin/bash
#BSUB -N {{ name }}
#BSUB -q {{ queue }}
#BSUB -n {{ processors }}
#BSUB -W {{ walltime }}:00
#BSUB -M {{ 1000000 * memory }}

# a variable in double curly brackets will be replaced with
# the appropriate value
# the following variables are required/strongly recommended:
# * name - name of the job and associated input/output files
# * processors - number of cpu cores/threads (sqm will not use more than 1 core)
# * memory - amount of memory requested from the cluster in GB
# * walltime - time limit for the job
#
# the sqm input file should have a .mdin extension
# the sqm output file should have a .sqmout extension

module purge

module load AmberTools
SCRATCH=/scratch/$USER/$LSB_JOBID
mkdir -p $SCRATCH
cd $SCRATCH
cp $LS_SUBCWD/{{ name }}.in .
sqm -i {{ name }}.mdin -o $LS_SUBCWD/{{ name }}.sqmout
cd $LS_SUBCWD
rm -rf $SCRATCH
exit"""
