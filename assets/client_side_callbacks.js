let ID_GRP_ANTN = 'list-group_annotations';
let ID_ITM_ANTN = 'item_annotation';
let ID_STOR_ANTN_IDX = 'store_clicked-annotation-index';

function get_match_id(str_id, idx) {
  return `${str_id}, ${idx}`;
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
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
