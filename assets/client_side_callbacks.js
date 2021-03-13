let ID_GRP_ANTN = 'list-group_annotations';
let ID_ITM_ANTN = 'item_annotation';
let ID_STOR_ANTN_IDX = 'store_clicked-annotation-index';

function get_match_id(str_id, idx) {
  return `${str_id}, ${idx}`;
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // load_annotations: function(record_nm, annotations) {
        //     if (record_nm != null) {
        //         let div = document.getElementById(ID_GRP_ANTN);
        //         for (let i = 0; i < annotations.length; ++i) {
        //             let type = annotations[i][0];
        //             let time = annotations[i][1];
        //             let text = annotations[i][2];
        //
        //             let li = document.createElement('li');
        //             let span_time = document.createElement('span');
        //             span_time.id = get_match_id(ID_ITM_ANTN, i);
        //             span_time.innerHTML = time;
        //             span_time.addEventListener('click', function() {
        //                 document.getElementById(ID_STOR_ANTN_IDX).innerHTML = i.toString();
        //             });
        //
        //             let para = document.createElement('P');
        //             para.innerHTML = 'This is a paragraph.' + type;
        //             div.appendChild(span_time);
        //         }
        //     } else {
        //         document.getElementById(ID_GRP_ANTN).innerHTML = '';  // Clear the layout
        //     }
        //     return 'dummy';
        // },

        update_tag_clicked: function(ns_clicks, ns_clicks_prev) {
            for (let i = 0; i < ns_clicks.length; ++i) {
                if (ns_clicks[i] !== ns_clicks_prev[i]) {  // Must've been greater than 1 by construction
                    return i;
                }
            }
            return -1;
        }
    }
});
