/*
 * Local Tags
 */
 
//-----------------------------------------------------------------------------
function generateTag() {
    var latest_tag = get_latest_tag();
    if (latest_tag == null)
        latest_tag = random_words();
    return (latest_tag);
}
//-----------------------------------------------------------------------------
function get_latest_tag() {
    current_tags = localStorage.getItem('bumps_tags');
    if (current_tags != null) {
        all_tags = current_tags.split(';');
        latest_tag = all_tags[0];
    }
    else {
        latest_tag = null;
    }
    return (latest_tag);
}
//-----------------------------------------------------------------------------
function save_tag_to_local(tag) {
    current_tags = localStorage.getItem('bumps_tags');
    if (current_tags == null)
        current_tags = tag;
    else {
        all_tags = current_tags.split(';');
        iTag = all_tags.indexOf(tag);
        if (iTag >= 0) {
            if (iTag > 0) {
                all_tags.splice(iTag,1);
            }
        }
        all_tags.splice(0,1,tag);
        current_tags = all_tags.join(';');
    }
    localStorage.setItem('bumps_tags',current_tags);
    return (tag);
}
//-----------------------------------------------------------------------------
function save_tag_to_local(tag) {
    current_tags = localStorage.getItem('bumps_tags');
    if (current_tags == null)
        current_tags = tag;
    else {
        all_tags = current_tags.split(';');
        iTag = all_tags.indexOf(tag);
        if (iTag >= 0) {
            if (iTag > 0) {
                all_tags.splice(iTag,1);
            }
        }
        all_tags.splice(0,1,tag);
        current_tags = all_tags.join(';');
    }
    localStorage.setItem('bumps_tags',current_tags);
    return (tag);
}
