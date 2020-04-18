//-----------------------------------------------------------------------------
function getServersParams() {
    var jsnBroker = getBrokerParams();
    var jsnBackend = getBackendParams();
    var jsonServers = setServersJSON(jsnBroker, jsnBackend);
    //var jsonServers = {'broker': jsnBroker, 'backend' : jsnBackend};
    return (jsonServers);
    //return ('servers params')
}
//-----------------------------------------------------------------------------
function setServersJSON(jsnBroker, jsnBackend){
    // the idea for this function is to construct the JSON in one place only, for easier future changes
    var jsonServers = {'broker': jsnBroker, 'backend' : jsnBackend};
    return (jsonServers);
}
//-----------------------------------------------------------------------------
function getBrokerParams() {
    return (getServerGuiParams('broker_type', 'txtBroker'));
}
//-----------------------------------------------------------------------------
function getBackendParams() {
    return (getServerGuiParams('backend_type', 'txtBackend'));
}
//-----------------------------------------------------------------------------
function getServerGuiParams(idType, idAddress) {
    var type = document.getElementById(idType);
    var typeName = 'unknown';
    var address = '';
    var jsnParam;
    try {
        typeName = type.options[type.selectedIndex].value;
        address = document.getElementById(idAddress).value;
        jsnParam = {'type':typeName, 'address':address};
    }
    catch (e) {
        console.log(e.message);
        jsnBroker = {};
    }
    return (jsnParam);
}
//-----------------------------------------------------------------------------
function displayServerResults(jsonResponse, txtResult, txtMessage) {
    try {
        var res = document.getElementById(txtResult);
        var msg = document.getElementById(txtMessage);
        if (jsonResponse.result == '1') {
            res.innerText = 'OK';
            res.style.color = 'green';
        }
        else if (jsonResponse.result == 'none') {
            res.innerText = '';
        }
        else {
            res.innerText = 'Fail';
            res.style.color = 'red';
        }
        msg.innerText = jsonResponse.message;
    }
    catch (e) {
        console.log(e);
    }
}
//-----------------------------------------------------------------------------
function displayBrokerResults(broker_response) {
    displayServerResults(broker_response, 'broker_test_result', 'broker_test_message');
}
//-----------------------------------------------------------------------------
function displayBackendResults(backend_response) {
    displayServerResults(backend_response, 'backend_test_result', 'backend_test_message');
}
//-----------------------------------------------------------------------------
function display_celery_setup(jsonServers) {
    var jsnBroker, jsnBackend;
    try {
        jsnBroker = jsonServers.broker;
    }
    catch (e) {
        jsnBroker = {'type': 'rabbit', 'address': 'bumps:bumps@ncnr-r9nano.campus.nist.gov'};
    }
    try {
        jsnBackend = jsonServers.backend;
    }
    catch (e) {
        jsnBackend = {'type': 'redis', 'address': 'ncnr-r9nano.campus.nist.gov'};
    }
    displayServerSetup(jsnBroker, 'txtBroker', 'broker_type', 'divBrokerConnection');
    displayServerSetup(jsnBackend, 'txtBackend', 'backend_type', 'divBackendConnection');
}
//-----------------------------------------------------------------------------
function displayServerSetup(jsnServer, txtServer, txtType, txtString) {
    var s;

    document.getElementById(txtServer).value   = jsnServer.address;
    document.getElementById(txtType).value = jsnServer.type;
    try {
        s = jsnServer.string;
    }
    catch {
        s = '';
    }
    document.getElementById(txtString).innerText = s;
}
//-----------------------------------------------------------------------------
function getParamsAsText () {
    var jsnParams = getServersParams();
    return (JSON.stringify(jsnParams));
}
//-----------------------------------------------------------------------------
function onServersSaveClick() {
    var text = getParamsAsText ();
    $.ajax({
        url: "/save_server_setup", type: "get", data: {jsdata: text},
        success: function(response) {
            try {
                if (response.toLowerCase().indexOf('error') >= 0) {
                    alert(response);
                }
                else {
                    jsonResponse = JSON.parse(response.replace(/\'/g,'"'));
                    display_celery_setup (jsonResponse);
                    document.getElementById('divMsg').innerText="Setup Saved";
                }
            }
            catch (e) {
                var err_msg = 'response ' + response + 'can not be handled' + '\n' + e.message;
                alert (err_msg);
            }
        },
        error: function(xhr) {
            console.log('runtime error: ' + xhr);
        }
    });
}
//-----------------------------------------------------------------------------
function onServersReloadClick() {
    $.ajax({
        url: "/read_celery_params", type: "get",
        success: function(response) {
            try {
                display_celery_setup(JSON.parse(response.replace(/\'/g,'"')));
                document.getElementById('divMsg').innerText="Reloaded";
            }
            catch (e) {
                var err_msg = 'response ' + response + 'can not be handled' + '\n' + e.message;
                alert (err_msg);
            }
        },
        error: function(xhr) {
            console.log('runtime error: ' + xhr);
        }
    });
}
//-----------------------------------------------------------------------------
function onServersDefaultClick() {
    var txtParams = getParamsAsText ();
    $.ajax({
        url: "/get_servers_default", type: "get", data: {jsdata: txtParams},
        success: function(response) {
            console.log(response);
            try {
                //jsonResponse = JSON.parse(response.replace(/\'/g,'"'));
                //display_celery_setup (jsonResponse);
                display_celery_setup (response);
                document.getElementById('divMsg').innerHTML="Default Loaded<br><b>Note:</b><u>Default setup is only displayed, not loaded</u>";
            }
            catch (e) {
                var err_msg = 'response ' + response + 'can not be handled' + '\n' + e.message;
                alert (err_msg);
            }
        },
        error: function(xhr) {
            console.log('runtime error: ' + xhr);
        }
    });
}
//-----------------------------------------------------------------------------
function onServersTestClick() {
    displayIntermediateTestingMsg();
    var text = getParamsAsText ();
    $.ajax({
        url: "/test_server",
        type: "get",
        data: {jsdata: text},
        success: function(response) {
            console.log(response);
            try {
                jsonResponse = JSON.parse(response.replace(/\'/g,'"'));
                displayBrokerResults(jsonResponse.broker);
                displayBackendResults(jsonResponse.backend);
            }
            catch (e) {
                var err_msg = 'response ' + response + 'can not be handled' + '\n' + e.message;
                alert (err_msg);
            }
        },
        error: function(xhr) {
            //str = f'runtimer error: {xhr}'
            console.log('runtime error: ' + xhr);
        }
    });
}
//-----------------------------------------------------------------------------
function onServersExportClick() {
    var txtParams = JSON.stringify(getServersParams());
    var a = document.body.appendChild(
        document.createElement("a")
    );
    a.download = "celery_servers.json";
    a.href = "data:text/json," + txtParams;
    a.click();
}
//-----------------------------------------------------------------------------
function displayIntermediateTestingMsg() {
    var jsnTesting={'result':'none','message':'testing'};
    var jsonServers = setServersJSON(jsnTesting, jsnTesting);
    displayBrokerResults(jsonServers.broker);
    displayBackendResults(jsonServers.backend);
}
//-----------------------------------------------------------------------------
