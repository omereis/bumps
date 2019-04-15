/* Bumps GUI middleware */
//-----------------------------------------------------------------------------
function load_bumps_problem () {
    try {
        var in_name = document.getElementById('problemFile').files[0];
        var file_name=null;
        var reader = new FileReader();
        reader.onload = function(e) {
            display_prolem(this.result);
            fileData = this.result;
        }
        file_name = in_name.name;
        reader.readAsText(in_name);
    }
    catch (err) {
        alert (err.message);
        document.getElementById("problemFile").value = null;
    }
}
//-----------------------------------------------------------------------------
function display_prolem(file_data) {
    var text_area = document.getElementById('problem_text');
    if (text_area) {
        text_area.value = file_data;
    }

}
//-----------------------------------------------------------------------------
function clear_file() {
    document.getElementById("problemFile").value = null;
    display_prolem(null);
}
//-----------------------------------------------------------------------------
function init_app () {
    change_multi_processing ("none");
}
//-----------------------------------------------------------------------------
function change_multi_processing (value) {
    if (value == "slurm") {
        document.getElementById ("mp_slurm").checked    = true;
        document.getElementById ("mp_celery").checked = false;
        document.getElementById ("mp_none").checked   = false;
        document.getElementById ("slurm_params").style.visibility    = 'visible';
        document.getElementById ("celery_params").style.visibility = 'hidden';
        document.getElementById ("no_mp_params").style.visibility  = 'hidden';
}
    else if (value == "none") {
        document.getElementById ("mp_slurm").checked  = false;
        document.getElementById ("mp_celery").checked = false;
        document.getElementById ("mp_none").checked     = true;
        document.getElementById ("slurm_params").style.visibility  = 'hidden';
        document.getElementById ("celery_params").style.visibility = 'hidden';
        document.getElementById ("no_mp_params").style.visibility    = 'visible';
    }
    else if (value == "celery") {
        document.getElementById ("mp_slurm").checked  = false;
        document.getElementById ("mp_celery").checked   = true;
        document.getElementById ("mp_none").checked   = false;
        document.getElementById ("slurm_params").style.visibility  = 'hidden';
        document.getElementById ("celery_params").style.visibility   = 'visible';
        document.getElementById ("no_mp_params").style.visibility  = 'hidden';
    }
}
//-----------------------------------------------------------------------------
function save_model () {
    var model_text = "model text";
    var file_name = "model.py"
    //saveData(model_text, file_name);
    download(model_text, file_name, 'text/plain');
}
//-----------------------------------------------------------------------------
function download(text, name, type) {
    var a = document.getElementById("a");
    var file = new Blob([text], {type: type});
    a.href = URL.createObjectURL(file);
    a.download = name;
  }
/*
function download(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}
*/
//-----------------------------------------------------------------------------
function download(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}
//-----------------------------------------------------------------------------
function onSendJobClick() {
    alert ("Job Sent");
}
//-----------------------------------------------------------------------------
