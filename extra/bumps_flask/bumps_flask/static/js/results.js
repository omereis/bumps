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
    sendMessage (JSON.stringify(message));
//    g_socket.send (JSON.stringify(message));
}
//-----------------------------------------------------------------------------
function onResultsDisplayClick() {
}
//-----------------------------------------------------------------------------
function onResultsLoadClick() {
}
//-----------------------------------------------------------------------------
function onResultsStatusClick () {
    var message = getMessageStart();

    message['command'] = ServerCommands.GET_STATUS;
    sendMessage (JSON.stringify(message));
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
//-----------------------------------------------------------------------------
function onSendJobClick() {
    var txtProblem = $('#problem_text').val().trim();

    if (txtProblem.length > 0) {
        var message = composeJobSendMessage(txtProblem);
        var tag = message['tag'];
        var row_id = addResultRow (tag);
        message['row_id'] = row_id;
        //g_socket = openWSConnection("ws", remoteServer, remotePort, "");
        sendMessage (JSON.stringify(message));
        //webSocketSendMessage ("ws", remoteServer, remotePort, "", JSON.stringify(message));
//        g_socket.send (JSON.stringify(message));
    }
    else
        alert ('Missing problem definition');
}
//-----------------------------------------------------------------------------
function sendMessage (message) {
    var remoteServer = $('#remote_server').val();
    var remotePort   = $('#remote_port').val();

    webSocketSendMessage ("ws", remoteServer, remotePort, "", message);
}
//-----------------------------------------------------------------------------
