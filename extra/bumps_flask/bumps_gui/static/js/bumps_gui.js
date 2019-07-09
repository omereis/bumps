/* Bumps GUI middleware */
//-----------------------------------------------------------------------------
var g_socket = null;
var g_flagNetBusy = false;
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
	var cbox_id = 'cbox' + (getNextCBoxID () + 1);
    cell.innerHTML = '<input type="checkbox" id="' + cbox_id + '">';
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
function addServerCells(row)
{
    var cell = row.insertCell(5);
    cell.innerText = $('#remote_server').val();
    cell.style.display="none";
    cell = row.insertCell(6);
    cell.innerText = $('#remote_port').val();
    cell.style.display="none";
    cell = row.insertCell(7);
    cell.innerText = $('#remote_tag').val();
    cell.style.display="none";
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
    addServerCells(row);
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

    fitParams['algorithm'] = $('#algorithm').val();//'rpg';
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
        var cbox = document.getElementById('cboxStatusPoll');
        if (cbox.checked) 
            cbox.checked = false;
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
// source: http://jsfiddle.net/HrJku/1/
function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds){
            break;
        }
    }
}
//-----------------------------------------------------------------------------
function generateTag() {
    var rw = random_words()
    document.getElementById('remote_tag').value = rw;
    return (rw)
}
//-----------------------------------------------------------------------------
function handleDelete (jmsg) {
    var params = jmsg['params'];
    console.log('length(params): ' + params.length);
    for (var n=0 ; n < params.length ; n++) {
        var id = params[n];
        deleteRowByDBID (id);
        deleteResultsById (id);
    }
}
//-----------------------------------------------------------------------------
function handle_reply(wsMsg) {
    var msg = wsMsg.split("'").join("\"");
    var jmsg = JSON.parse(msg);
    var command = jmsg['command'];
    if (command == ServerCommands.START_FIT) {
        var params = jmsg['params'];
        var local_id = Object.keys(params).toString();
        var db_id = params[local_id];
        var cbox = document.getElementById(local_id);
        cbox.setAttribute('db_id', db_id);
        var cell = cbox.parentElement;
        cell.innerHTML += db_id.toString();
    }
    else if (command == ServerCommands.DELETE) {
        handleDelete (jmsg);
    }
    else if (command == ServerCommands.GET_STATUS) {
        var params = jmsg['params'];
        console.log('GetStatus reply' + wsMsg)
        updateJobsStatus (params);
    }
    else if (command == ServerCommands.GET_RESULTS) {
        showFitResults (jmsg);
    }
}
//-----------------------------------------------------------------------------
function getFileExtension (file_name) {
    return (file_name.split('.').pop());
}
//-----------------------------------------------------------------------------
function resFileLink (name) {
    html = '<a href="' + name + '" target="_blank">' + name.split('/').pop() + '</a>';
    return (html);
}
//-----------------------------------------------------------------------------
function resFileImageLink (name) {
    html = '<img src="' + name + '">';
    return (html);
}
//-----------------------------------------------------------------------------
function isPicture(ext) {
    var lstrPicExtension = ['jpg', 'jpeg','png', 'gif']
    var pos = lstrPicExtension.indexOf(ext.toLowerCase());
    return (pos >= 0);
}
//-----------------------------------------------------------------------------
function getDifference(a, b)
{
    var i = 0;
    var j = 0;
    var result = "";

    while (j < b.length)
    {
        if (a[i] != b[j] || i == a.length)
            result += b[j];
        else
            i++;
        j++;
    }
    return result;
}
//-----------------------------------------------------------------------------
function getResultsDivFromID (id) {
    var strFitResults = 'fit_results_' + id.toString();
    return (strFitResults);
}
//-----------------------------------------------------------------------------
function showFitResults (jmsg) {
    var divResults = document.getElementById('fit_results');
    var n, strHtml='', name, ext, id;

    if (divResults) {
        id = jmsg['params'].id;
        //var strFitResults = 'fit_results_' + id.toString();
        var strFitResults = getResultsDivFromID (jmsg['params'].id);
        var divJobRslt = document.getElementById(strFitResults);
        if (divJobRslt == null) {
            divJobRslt = document.createElement('div');
            divJobRslt.setAttribute('id',strFitResults);
            divResults.appendChild(divJobRslt);
        }
        divJobRslt.innerHTML = 'Results for job #' + id.toString() + '<br>';
        for (n=0 ; n < jmsg['params'].files.length ; n++) {
            name = jmsg['params'].files[n];
            ext = getFileExtension (name);
            if (isPicture(ext))
                strHtml += '<br>' + resFileImageLink (name) + '<br>';
            else
                strHtml += resFileLink (name) + ", ";
        }
        strHtml += '<hr>';
        divJobRslt.innerHTML = divJobRslt.innerHTML + strHtml;
    }
}
//-----------------------------------------------------------------------------
function get_db_id_from_row (row, tbl=null) {
    var id;
    
    if (tbl == null)
        tbl = document.getElementById('tblResults');
    try {
        id = $(tbl.rows[row].cells[0].innerHTML).attr('db_id');
    }
    catch {
        id = -1;
    }
    return (id);
}
//-----------------------------------------------------------------------------
function getRowByDBID (db_id) {
    var id, row, tbl = document.getElementById('tblResults'), rowSelected;

    for (row=1, rowSelected=-1 ; (row < tbl.rows.length) && (rowSelected < 0) ; row++) {
        try {
            //id = $(tbl.rows[row].cells[0].innerHTML).attr('db_id');
            id = get_db_id_from_row (row);
            }
        catch (err) {
            id = null
        }
        if (id == db_id) {
            rowSelected = row;
        }
    }
    return (rowSelected);
}
//-----------------------------------------------------------------------------
function getBtnIdFromHTML (btnID, lstrHTML) {
    var lstr, n, id=-1;

	lstr = lstrHTML.split(' ');
    for (n=0 ; (n < lstr.length) && (id < 0) ; n++) {
        var desc = lstr[n].split('=');
        if (desc[0] == "id")
            id = desc[1].toString().replace(/\"/g,'');
    }
    return (id);
}
//-----------------------------------------------------------------------------
function getRowByBtnShowID (db_id) {
    var id, row, tbl = document.getElementById('tblResults'), rowSelected;

    for (row=1, rowSelected=-1 ; (row < tbl.rows.length) && (rowSelected < 0) ; row++) {
        try {
            //id = $(tbl.rows[row].cells[0].innerHTML).attr('db_id');
            id = getBtnIdFromHTML (db_id, tbl.rows[row].cells[4].innerHTML);
        }
        catch (err) {
            id = null
        }
        if (id == db_id) {
            rowSelected = row;
        }
    }
    return (rowSelected);
}
//-----------------------------------------------------------------------------
function deleteRowByDBID (btn_id) {
    var id, row, tbl = document.getElementById('tblResults'), rowToDel;

    for (row=1, rowToDel=-1 ; (row < tbl.rows.length) && (rowToDel < 0) ; row++) {
        try {
            id = $(tbl.rows[row].cells[0].innerHTML).attr('db_id');
        }
        catch (err) {
            id = null
        }
        if (id == btn_id) {
            rowToDel = row;
        }
    }
    if (rowToDel >= 0) {
        tbl.deleteRow (rowToDel);
    }
}
//-----------------------------------------------------------------------------
function deleteResultsById (id) {
    var div = document.getElementById(getResultsDivFromID(id));
    if (div)
        div.parentNode.removeChild(div);
}
//-----------------------------------------------------------------------------
function sendForFitResults (job_id) {
    var res_div = document.getElementById('fit_results')
    var row = getRowByBtnShowID (job_id)
    if (row >= 0)
        id = get_db_id_from_row (row);
    else
        id = -1;
    var message = getMessageStart();
    message['command'] = ServerCommands.GET_RESULTS;
    message['params'] = id;
    sendMesssageThroughFlask(message);
    //sendMessage (JSON.stringify(message));

    res_div.innerHTML = res_div.innerHTML + '<br>' + s + '<hr>';
    //res_div.innerHTML = res_div.innerHTML + '<table><tr><td>' + job_id.toString() + '</td></tr></table><br><hr><img src="/static/ncnr01.jpg>';
    //</img>'<img src="http://urbanologia.tau.ac.il/wp-content/uploads/2015/06/20141212-RAHAT-ARAD-262.jpg" width="100" height="100">'
    $.post("dashboard");
}
//-----------------------------------------------------------------------------
function updateJobsStatus (params) {
    var n, tbl = document.getElementById('tblResults')

    try {
        for (n=0 ; n < params.length ; n++) {
            var job_id, row;
            job_id = params[n].job_id;
            row = getRowByDBID (job_id);
            if (row >= 0) {
                if (tbl.rows[row].cells[3].innerText != params[n].job_status) {
                    tbl.rows[row].cells[3].innerText = params[n].job_status;
                    if (params[n].job_status == 'Completed') {
                        var btnID = 'btnResultsBtn' + job_id.toString(10);
                        tbl.rows[row].cells[4].innerHTML = '<input type="button" id="' + btnID + '" value="Show" onclick="sendForFitResults(this.id)">';
                    }
                }
                
                
            }
        }
    }
    catch (err) {
        console.log ('Error in updateJobsStatus: ' + err.message);
    }
}
//-----------------------------------------------------------------------------
function onResultsDeleteClick() {
    var n, tbl = document.getElementById('tblResults'), aLinesToDel = [], idx = 0;

    for (n=1 ; n < tbl.rows.length ; n++) {
        var id=$(tbl.rows[n].cells[0].innerHTML).attr('id');
        var chk=document.getElementById(id).checked;
        if (chk)
            //tbl.deleteRow(n);
            aLinesToDel[idx++] = $(tbl.rows[n].cells[0].innerHTML).attr('db_id');
    }
    composeSendDeleteMessage (aLinesToDel);
}
//-----------------------------------------------------------------------------
function composeSendDeleteMessage (aLinesToDel) {
    var message = getMessageStart();
    message['command'] = ServerCommands.DELETE;
    message['params'] = aLinesToDel;
    sendMesssageThroughFlask(message);
}
//-----------------------------------------------------------------------------
function onResultsDisplayClick() {
}
//-----------------------------------------------------------------------------
function onResultsLoadClick() {
}
//-----------------------------------------------------------------------------
function getStatusCommandMessage() {
    var message = getMessageStart();

    message['command'] = ServerCommands.GET_STATUS;
    return (message);
}
//-----------------------------------------------------------------------------
function sendStatusMessage() {
    sendMesssageThroughFlask(getStatusCommandMessage());
}
//-----------------------------------------------------------------------------
function sendPrintStatus() {
    var message = getMessageStart();

    message['command'] = ServerCommands.PRINT_STATUS;
    sendMessage (JSON.stringify(message));
}
//-----------------------------------------------------------------------------
function onResultsStatusClick () {
    sendStatusMessage();
}
//-----------------------------------------------------------------------------
function onStatusTimerTick () {
    var cbox = document.getElementById('cboxStatusPoll');
    if (cbox.checked)
        sendStatusMessage();
}
//-----------------------------------------------------------------------------
function getMessageStart() {
    var message = new Object;

    message['header'] = 'bumps client';
    message['tag']    = getTag();
    message['message_time'] = getMessageTime();
    return (message);
}
//-----------------------------------------------------------------------------
function upload_multiprocessing() {
    var mp = '';
    if (document.getElementById('mp_none').checked)
        mp = 'none';
    else if (document.getElementById('mp_celery').checked)
        mp = 'celery';
    else if (document.getElementById('mp_slurm').checked)
        mp = 'slurm';
    else
        mp = 'error';
    return (mp);
}
//-----------------------------------------------------------------------------
function composeJobSendMessage(txtProblem) {
    var message = getMessageStart();

    message['command'] = ServerCommands.START_FIT;
    message['fit_problem'] = txtProblem;
    message['problem_file'] = upload_problem_file();
    message['params'] = uploadFitParams();
    message['multi_processing'] = upload_multiprocessing();
    return (message);
}
/*
//-----------------------------------------------------------------------------
function onSendJobClick() {
    var txtProblem = $('#problem_text').val().trim();

    if (txtProblem.length > 0) {
        var message = composeJobSendMessage(txtProblem);
        var tag = message['tag'];
        var row_id = addResultRow (tag);
        message['local_id'] = row_id;
        sendMessage (JSON.stringify(message));
    }
    else
        alert ('Missing problem definition');
}
*/
//-----------------------------------------------------------------------------
function sendMesssageThroughFlask(message) {
    $.ajax({
        url: "/onsendfitjob",
        type: "get",
        data: {message: JSON.stringify(message)},
        success: function(response) {
            try {
                var reply;
                if (typeof(response) != 'string')
                    reply = JSON.parse(response);
                else
                    reply = response;
                console.log(JSON.stringify(reply));
                handle_reply(reply);
            }
            catch (err) {
                console.log(err);
            }
        },
        error: function(xhr) {
            alert('error');
            console.log(xhr.toString());
        }
    });
}
//-----------------------------------------------------------------------------
function onSendFitJobClick() {
    var txtProblem = $('#problem_text').val().trim();

    if (txtProblem.length > 0) {
        var message = composeJobSendMessage(txtProblem);
        var tag = message['tag'];
        var row_id = addResultRow (tag);
        message['local_id'] = row_id;
        //message['row_id'] = row_id;
        sendMesssageThroughFlask(message);
    }
    else
        alert ('Missing problem definition');
}
//-----------------------------------------------------------------------------
