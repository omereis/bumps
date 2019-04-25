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
    var txtProblem = $('#problem_text').val().trim();
    g_socket.send('if (txtProblem.length == 0) {');
        //alert ('Missing problem definition');
        //$('#problem_text').focus();
    //}
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
    g_socket = openWSConnection("ws", "NCNR-R9nano.campus.nist.gov", 8765, "");
    // openWSConnection(protocol, hostname, port, endpoint)

}
//-----------------------------------------------------------------------------
function disconnectServer() {
    g_socket.close();
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
            document.getElementById("job_results").value += "message: " + msg + "\n";
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
