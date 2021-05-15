# On next steps 

Stefan, Yuzhao Heng 

Since Thur. Apr. 22nd. 2021 





​		This document is written for someone to pick up my work on developing the web app for supporting the visualization and annotation of ECG signals. 



​		Feel free to read through my weekly reports, progress media files & design wireframes on the Google Drive or contact me. 





The following are features I have discussed with Dr. Saeed but weren’t able to finish implementing. 

## On features should have

### Comment edit and removal

The design is thought through and its bare-bone implemented only. 

- Edit: click on a timestamp for an item in the comment list which loads up the corresponding caliper measurement 
- Removal: Click on a remove button for each item in the comment list 



This is important for retrospective study, in particular for annotating on regions of interest. 



The logic for loading a caliper corresponding to a comment <u>only when</u> the caliper is not already present is not implemented 





## On features nice to have

### ECG Signal filtering

Would be a good ideal in terms of runtime efficiency to store a filtered version of the ECG signals using notch filter & bandpass filter 





### ECG QRS complex detection

In particular, detects the QRS onset and offset and show those on the lead channels on display. 



QRS detection is implemented, see `ecg_marker`. Also for runtime efficiency, it’s a good idea to preprocess them into a local file. 



The design is thought through but the UI interactions is not implemented. 





### Caliper measurement mode switch

Caliper measurement is supported for both 

1. Synchronized: caliper measurement on 1 channel is broadcast to all channels on display 

For now for simplicity, when users switch mode, all existing caliper measurements are removed 

A more convenient solution would be 

- Keep track of most recent edited lead index for each caliper measurement 
- For transferring from synchronized to independent which is the less intuitive part, take advantage of the above 





### Log in & preferences 

Several static declarations can be subject to user preference: e.g. 

- Maximal lead on display 
- Discrete jump size 
- Lead templates 
- Maximal number of points on display for each channel 







## Some advice

Dash has a big overhead in terms of updating interactive elements compared to e.g. JavaScript. There would be multiple communication between the server. 

Note that we have 300 static tags that supports interaction, i.e. navigation by clicking on the timestamp. Listening to such a magnitude of components makes the library update time really slow. 

My 2 solutions in mind are either 1) switch to another language for development or 2) dynamically and load less number of components.  





## On understanding the implementation 

1> I found modifications to the plotly figures’ internal dictionary more convenient as I know exactly what happened. This is requires a bit experimenting at first. 

I choose to do so this way because the plotly supported functions are in some sense a black box and they don’t tend to work as I intend. 





2> The global thumbnail preview is a hack. I took advantage of `RangeSlider` for a plotly figure and hid the actual figure. 





