# test_ECG-Signal-Viewer
Development repository. 

Experiment language, libraries; development & test on new features for release on [Ecg-Signal-Viewer](https://github.com/StefanHeng/Ecg-Signal-Viewer). 



## Guideline
Files at root prefixed with `ecg_` are for release. 

Files of the form `ecg_dev_run-(.*).py` are time sensitive, iterative scripts for Dash web app integration. 
Only the most recent versions are meaningful and relevant.
See [Google Drive](https://drive.google.com/drive/u/0/folders/1LoDe0fVXWghLS3dO6EcsUCoV639Plo7I) `~/Dev Progress` folder 
for a more detailed development record and demo. 
 
`dev` folder contains unit tests at various scale on language and python package functionality. 
 
`assets` folder contains `CSS` files per [Dash](https://dash.plotly.com). 
 
`Design` folder contains design, in particular color choices. 



## On Code organization 
Here explains the relations between `ecg_(.*).py` release files. 

- `data_link.py`, specify the local directory for `.h5` record files 
	- So long as files are processed locally 
- `ecg_app.py`, encapsulates a Dash app 
	- Highest level of abstraction 
- `ecg_record.py`, interface with local `.h5` file 
- `ecg_ui`, deals with conversion between `plotly` graph object and web app variables format 


