# LuxendoToTeraStitcherConverter
## Description
LuxendoToTeraStitcherConverter (LTC) is a tool that converts the Luxendo microscope format into the TeraStitcher format.

The LTC changes both the folder structure of scanned tiles (from Luxendo to TeraStitcher) and the image format of tiles (from hdf5 to tif) making it possible to stitch the images acquired with Luxendo LSFM models (MuVi-SPIM and LCS-SPIM) with the TeraStitcher software. There is also the possibility of applying image processing operations over the scanned tiles to improve the signal to noise ratio of the acquisition through several contrast stretching strategies (intensity mapping, histogram equalization, CLAHE, etc). Moreover, the tool enables to generate pseudo-stitched whole brain images on-the-fly during the scanning day to check whether the quality of the labeling and several settings are the righ ones (the overlap between tiles and the spatial boundaries of the scan that keeps the whole brain on frame). This is essencial at the time of exploring a fast test-scan that can take 1 hour before performing the full-scan that takes around 2 days.

## Image Gallery
### Luxendo to TeraStitcher Convertion Diagram
The diagram shows the workflow for converting a whole brain scanned with a Luxendo microscope to the TeraStitcher format. 
![Convertion Diagram](https://github.com/MorphoNeuralNetworks/LuxendoToTeraStitcherConverter/blob/main/readme_images/Luxendo_Workflow.png)
### On-the-Fly Visualization with Pseudo-Stitched Whole Brain Images
The computation and visualization of pseudotitching whole brain images enables the inspection of the quality of the images and the suitability of the scanning settings of the Luxendo microscope.
![Luxendo Inspection](https://github.com/MorphoNeuralNetworks/LuxendoToTeraStitcherConverter/blob/main/readme_images/Luxendo_Inspection.png)
### Grafical User Interface (GUI)
The GUI makes the tool more user-friendly. Moreover, users can also use a CLI to launch the tool on a high computing cluster. 
![GUI Demo](https://github.com/MorphoNeuralNetworks/LuxendoToTeraStitcherConverter/blob/main/readme_images/Luxendo_GUI.png)

## AUTHORS
Adrian Arias Abreu

## LICENCE
[LICENCE](https://github.com/MorphoNeuralNetworks/LuxendoToTeraStitcherConverter/blob/main/LICENCE)
