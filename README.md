# test_ECG-Signal-Viewer
Development repository. 

Experiment language, libraries; development & test on new features.

See [Ecg-Signal-Viewer](https://github.com/StefanHeng/Ecg-Signal-Viewer) for release. Release repo [contact](https://stefanheng.github.io). 


## Repository structure 
Files at root prefixed with `ecg_` are for package release. 

Files of the form `ecg_dev_run-(.*).py` are time sensitive, iterative scripts for Dash web app integration. 
Only the most recent versions are meaningful and relevant.
See [Google Drive](https://drive.google.com/drive/u/0/folders/1LoDe0fVXWghLS3dO6EcsUCoV639Plo7I) `~/Dev Progress` folder 
for a more detailed development record and demo. 
 
`dev` folder contains unit tests at various scale on language and python package functionality. 
 
`assets` folder contains `CSS` and `JS` files per [Dash](https://dash.plotly.com). 
 
`Design` folder contains design decisions, e.g. color choices. 



## On Code organization 
Here explains the relations between `ecg_(.*).py` release files. 

- `data_link.py`: specifies the local directory for `.h5` record files  
	- So long as files are processed locally
- `dev_helper.py`: contains development-only links
- `ecg_app.py`: encapsulates a `Dash` web app with all the interactions  
	- The highest level of abstraction
- `ecg_defns_n_util`: associated with `ecg_app`, stores the static declarations 
- `ecg_record.py`: interfaces with local `.h5` binary file on ECG recordings, e.g. fetching sampled data   
- `ecg_ui`: deals at low-level with `plotly` figures Dash web app specifications; Internal storage of caliper measurements
- `ecg_comment`: handles internal comment storage as lists 
- `ecg_export`: handles exporting lead channels on display to CSV 
- `ecg_marker`: contains intelligent analytic tools including filtering, R peak & QRS detection 
- `ecg_plot`: handles specifically each lead channel layout and the thumbnail layout



## Development resources
- [Dash core components](https://dash.plotly.com/dash-core-components), 
  [Dash bootstrap components](https://dash-bootstrap-components.opensource.faculty.ai).
- [FontAwesome icons](https://fontawesome.com/icons?d=gallery&p=2). 
- Bootswatch theme [LUX](https://bootswatch.com/lux/). 



## A note for next steps 
See [On next steps](https://github.com/StefanHeng/test_Ecg-Signal-Viewer/blob/main/On-next-steps.md) 
for some guidance on features to include and development advices. 
