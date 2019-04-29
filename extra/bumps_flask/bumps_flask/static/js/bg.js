/* Bumps GUI middleware */
//-----------------------------------------------------------------------------
var g_socket = null;
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
function getGeoData() {
	$.getJSON('http://gd.geobytes.com/GetCityDetails?callback=?', function(data) {
      console.log(JSON.stringify(data, null, 2));
      $('#ipAddress').val(data['geobytesremoteip']);
	});
}
//-----------------------------------------------------------------------------
function clear_file() {
    document.getElementById("problemFile").value = null;
    display_prolem(null);
//    getGeoData();
	//$.getJSON('http://gd.geobytes.com/GetCityDetails?callback=?', function(data) {
	  //console.log(JSON.stringify(data, null, 2));
	//});
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
function insertSelectCell (table, row, idx) {
    var cell = row.insertCell(idx);
	var cbox_id = 'cbox' + table.rows.length.toString(10);
	cell.innerHTML = '<input type="checkbox" id="' + cbox_id + '">';//cbox4">';
}
//-----------------------------------------------------------------------------
function insertTimeCell (table, row, idx) {
    var cell = row.insertCell(idx);
    var dt = new Date();
	var month = dt.toLocaleDateString('en-us',{month:'short'});
    cell.innerText = dt.getFullYear() + '-' + month + '-'+ dt.getDate() + ', ' + 
        dt.getHours() + ':' + dt.getMinutes() + ':' + dt.getSeconds();
}
//-----------------------------------------------------------------------------
function insertTagCell (row, tag, idx) {
    var cell = row.insertCell(idx);
    cell.innerText = tag;
}
//-----------------------------------------------------------------------------
function insertStatusCell (row, idx) {
    var cell = row.insertCell(idx);
    cell.innerText = 'sent';
}
//-----------------------------------------------------------------------------
function insertResultsCell (row, idx) {
    var cell = row.insertCell(idx);
    cell.innerText = '---';
}
//-----------------------------------------------------------------------------
function addResultRow (tag)
{
    var table = document.getElementById('results_table');
    var row = table.insertRow(table.rows.length);
    insertSelectCell (table, row, 0);
    insertTimeCell (table, row, 1);
    insertTagCell (row, tag, 2)
    insertStatusCell (row, 3);
    insertResultsCell (row, 4);
}
//-----------------------------------------------------------------------------
function getTag() {
    var tag = document.getElementById('remote_tag').value;
    if (tag == '')
        tag = generateTag();
    return (tag);
}
//-----------------------------------------------------------------------------
function uploadFitParams() {
    var fitParams = new Object;

    fitParams['algorithm'] = 'rpg';
    fitParams['steps'] = $('#fitting_steps').val();
    fitParams['burns'] = $('#fitting_burn').val();
    return (fitParams);
}
//-----------------------------------------------------------------------------
function upload_problem_file() {
    var fname = null;

    try {
        fname = $('#problemFile').val();
    }
    catch {
        fname = 'problem.py';
    }
    return (fname);
}
//-----------------------------------------------------------------------------
function composeJobSendMessage(txtProblem) {
    var message = new Object;

    var tag = getTag();
    message['header'] = 'bumps client';
    message['tag']    = tag;
    message['command'] = 'StartFit';
    message['fit_problem'] = txtProblem;
    message['problem_file'] = upload_problem_file();
    message['params'] = uploadFitParams();
    message['multi_processing'] = 'none'
    return (message);
}
//-----------------------------------------------------------------------------
function onSendJobClick() {
    var txtProblem = $('#problem_text').val().trim();

    if (txtProblem.length > 0) {
        var message = composeJobSendMessage(txtProblem);
        var tag = message['tag'];
        addResultRow (tag);
        g_socket.send (JSON.stringify(message));
    }
    else
        alert ('Missing problem definition');
}
//-----------------------------------------------------------------------------
function ip_local() {
/*
Source: https://stackoverflow.com/questions/20194722/can-you-get-a-users-local-lan-ip-address-via-javascript
*/
    var ip = false;
    window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection || false;

    if (window.RTCPeerConnection) {
        ip = [];
        var pc = new RTCPeerConnection({iceServers:[]}), noop = function(){};
        pc.createDataChannel('');
        pc.createOffer(pc.setLocalDescription.bind(pc), noop);

        pc.onicecandidate = function(event) {
            if (event && event.candidate && event.candidate.candidate) {
                var s = event.candidate.candidate.split('\n');
                ip.push(s[0].split(' ')[4]);
            }
        }
    }

    return ip;
}
//-----------------------------------------------------------------------------
function connectServer() {
    var remoteServer = $('#remote_server').val();
    var remotePort   = $('#remote_port').val();
    g_socket = openWSConnection("ws", remoteServer, remotePort, "");
//    g_socket = openWSConnection("ws", "NCNR-R9nano.campus.nist.gov", 8765, "");
}
//-----------------------------------------------------------------------------
function disconnectServer() {
    g_socket.close();
}
//-----------------------------------------------------------------------------
function socketErrorHandler (socket, eventError) {
    if (webSocket.readyState == 3) {
        alert('Communication faule:\nDestination not ready');
    }
}
//-----------------------------------------------------------------------------
function openWSConnection(protocol, hostname, port, endpoint) {
    var webSocketURL = null;
    webSocketURL = protocol + "://" + hostname + ":" + port + endpoint;
    console.log("openWSConnection::Connecting to: " + webSocketURL);
    try {
        webSocket = new WebSocket(webSocketURL);
        webSocket.addEventListener('error', (event) => {
            console.log('in addEventListener');
            console.log(event);
        });
        webSocket.onopen = function(openEvent) {
            console.log("WebSocket OPEN: " + JSON.stringify(openEvent, null, 4));
            document.getElementById("btnSendJob").disabled       = false;
            document.getElementById("btnConnect").disabled    = true;
            document.getElementById("btnDisconnect").disabled = false;
        };
        webSocket.onclose = function (closeEvent) {
            console.log("WebSocket CLOSE: " + JSON.stringify(closeEvent, null, 4));
            document.getElementById("btnSendJob").disabled       = true;
            document.getElementById("btnConnect").disabled    = false;
            document.getElementById("btnDisconnect").disabled = true;
        };
        webSocket.onerror = function (errorEvent) {
            var msg = "WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4);
            console.log("WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4));
            console.log(msg);
            socketErrorHandler (webSocket, errorEvent);
            //document.getElementById("job_results").value += "message: " + msg + "\n";
        };
        webSocket.onmessage = function (messageEvent) {
            var wsMsg = messageEvent.data;
            console.log("WebSocket MESSAGE: " + wsMsg);
            if (wsMsg.indexOf("error") > 0) {
                document.getElementById("job_results").value += "error: " + wsMsg.error + "\r\n";
            } else {
				console.log(wsMsg);
				$('#status_line').append(wsMsg);
                //document.getElementById("job_results").value += "message: " + wsMsg + "\r\n";
            }
        };
    } catch (exception) {
        console.error(exception);
    }
	return (webSocket);
}
//-----------------------------------------------------------------------------
function generateTag() {
    var rw = random_words()
    document.getElementById('remote_tag').value = rw;
    return (rw)
}
//-----------------------------------------------------------------------------
