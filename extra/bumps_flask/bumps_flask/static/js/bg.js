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
function getNextCBoxID () {
    var n, id, idMax, tbl = document.getElementById('tblResults');

    try {
        idMax = 1;
        for (n=1 ; n < tbl.rows.length ; n++) {
            var txtID=tbl.rows[n].cells[0].innerHTML;
            if (txtID.length > 0) {
                txtID = $(txtID).attr('id');
                id = parseInt (txtID.substring(4,txtID.length));
            }
            else
                id = 0;
            idMax = Math.max (idMax, id);
        }
    }
    catch (err) {
        console.log(err.message);
        idMax = 1;
    }
    idMax = Math.max (idMax, 1);
    return (idMax);
}
//-----------------------------------------------------------------------------
function insertSelectCell (row, idx) {
    var cell = row.insertCell(idx);
	var cbox_id = 'cbox' + (getNextCBoxID () + 1);//table.rows.length.toString(10);
    cell.innerHTML = '<input type="checkbox" id="' + cbox_id + '">';//cbox4">';
    return (cbox_id);
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
    var table = document.getElementById('tblResults');
    var row = table.insertRow(table.rows.length);
    var cell_id = insertSelectCell (row, 0);
    insertTimeCell (table, row, 1);
    insertTagCell (row, tag, 2)
    insertStatusCell (row, 3);
    insertResultsCell (row, 4);
    return (cell_id);
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
function getMessageTime() {
    var d = new Date;
    var date_json = {};
    date_json['year'] = d.getFullYear();
    date_json['month'] = (d.getMonth() + 1);
    date_json['date'] = d.getDate();
    date_json['hour'] = d.getHours();
    date_json['minutes'] = d.getMinutes();
    date_json['seconds'] = d.getSeconds();
    date_json['milliseconds'] = d.getMilliseconds();
    return (date_json);
    //return (JSON.stringify(date_json));
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
function enableResultsButtons(op) {
    var fSend, fConnect, fDisconnect, fDel;

    fSend = fConnect = fDisconnect = fDel = false;
    if (op == 'open') {
        fDisconnect = fSend = fDel = true;
    }
    else if (op == 'close') {
        fConnect = true;
    }
    else
        return;
    //document.getElementById("btnSendJob").disabled      = !fSend;//false;
    document.getElementById("btnConnect").disabled      = !fConnect;//true;
    document.getElementById("btnDisconnect").disabled   = !fDisconnect;//false;
    //document.getElementById("btnResultDelete").disabled = !fDel;//false;
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
            enableResultsButtons('open');
        };
        webSocket.onclose = function (closeEvent) {
            console.log("WebSocket CLOSE: " + JSON.stringify(closeEvent, null, 4));
            enableResultsButtons('close');
        };
        webSocket.onerror = function (errorEvent) {
            var msg = "WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4);
            console.log("WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4));
            console.log(msg);
            socketErrorHandler (webSocket, errorEvent);
        };
        webSocket.onmessage = function (messageEvent) {
            var wsMsg = messageEvent.data;
            console.log("WebSocket MESSAGE: " + wsMsg);
            if (wsMsg.indexOf("error") > 0) {
                document.getElementById("job_results").value += "error: " + wsMsg.error + "\r\n";
            } else {
                console.log(wsMsg);
                handle_reply(wsMsg);
				$('#status_line').append(wsMsg + '<br>');
            }
        };
    } catch (exception) {
        console.error(exception);
    }
	return (webSocket);
}
//-----------------------------------------------------------------------------
function webSocketSendMessage(protocol, hostname, port, endpoint, message) {
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
            webSocket.send(message);
            enableResultsButtons('open');
        };
        webSocket.onclose = function (closeEvent) {
            console.log("WebSocket CLOSE: " + JSON.stringify(closeEvent, null, 4));
            enableResultsButtons('close');
        };
        webSocket.onerror = function (errorEvent) {
            var msg = "WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4);
            console.log("WebSocket ERROR: " + JSON.stringify(errorEvent, null, 4));
            console.log(msg);
            socketErrorHandler (webSocket, errorEvent);
        };
        webSocket.onmessage = function (messageEvent) {
            var wsMsg = messageEvent.data;
            console.log("WebSocket MESSAGE: " + wsMsg);
            if (wsMsg.indexOf("error") > 0) {
                document.getElementById("job_results").value += "error: " + wsMsg.error + "\r\n";
            } else {
                console.log(wsMsg);
                handle_reply(wsMsg);
				$('#status_line').append(wsMsg + '<br>');
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
function handle_reply(wsMsg) {
    var msg = wsMsg.split("'").join("\"");
    var jmsg = JSON.parse(msg);
    var command = jmsg['command'];
    if (command == ServerCommands.START_FIT) {
        var params = jmsg['params'];
        var row_id = Object.keys(params).toString();
        var db_id = params[row_id];
        var cbox = document.getElementById(row_id);
        cbox.setAttribute('db_id', db_id);
    }
    else if (command == ServerCommands.DELETE) {
        var params = jmsg['params'];
        console.log('length(params): ' + params.length);
        for (var n=0 ; n < params.length ; n++) {
            var id = params[n];
            deleteRowByDBID (id);
        }
    }
}
//-----------------------------------------------------------------------------
function deleteRowByDBID (db_id) {
    var id, row, tbl = document.getElementById('tblResults'), rowToDel;

    for (row=1, rowToDel=-1 ; (row < tbl.rows.length) && (rowToDel < 0) ; row++) {
        try {
            id = $(tbl.rows[row].cells[0].innerHTML).attr('db_id');
        }
        catch (err) {
            id = null
        }
        if (id == db_id) {
            rowToDel = row;
        }
    }
    if (rowToDel >= 0) {
        tbl.deleteRow (rowToDel);
    }
        
}
//-----------------------------------------------------------------------------
