ECHO OFF

:: Define the CLI version
SET mainCLI=main_CLI_v3.py

:: Define the Path Variables
SET pathIn=Ref_2100_39765_SPIM_MuVi_15x_Line_AJO_TS_M_Test\2022-01-28_152503\raw\stack_1-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5
SET pathConf=C:\Users\aarias\MySpyderProjects\p1_15_DataStructureConverter\example\config.json
SET pathOut=C:\Users\aarias\MySpyderProjects\p1_15_DataStructureConverter\example\results

:: Define the Computing Settings
SET nCPU=4

ECHO nCPU=%nCPU%
python %mainCLI% -dx=2 -dy=2 -dz=1 --nCPU=%nCPU%

::python %mainCLI% --pathFileIn=%pathIn% --pathFileConf=%pathConf% --pathFolderOut=%pathOut% --nCPU=%nCPU%

PAUSE