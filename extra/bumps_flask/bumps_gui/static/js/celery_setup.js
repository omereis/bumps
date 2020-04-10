//-----------------------------------------------------------------------------
function getServersParams() {
    var jsnBroker = getBrokerParams();
    var jsnBackend = getBackendParams();
    var jsonServers = {'broker': jsnBroker, 'backend' : jsnBackend};
    return (jsonServers);
    //return ('servers params')
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
        if (jsonResponse.result) {
            res.innerText = 'OK';
            res.style.color = 'green';
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
function init_celery_setup(jsonServers) {
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
    displayBrokerSetup(jsnBroker);
    displayBackendSetup(jsnBackend);
}
//-----------------------------------------------------------------------------
function displayBrokerSetup(jsnBroker) {
    document.getElementById('txtBroker').value   = jsnBroker.address;
    document.getElementById('broker_type').value = jsnBroker.type;
}
//-----------------------------------------------------------------------------
function displayBackendSetup(jsnBackend) {
    document.getElementById('txtBackend').value   = jsnBackend.address;
    document.getElementById('backend_type').value = jsnBackend.type;
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
        url: "/save_server_setup",
        type: "get",
        data: {jsdata: text},
        success: function(response) {
            try {
                if (response.toLowerCase().indexOf('error') >= 0) {
                    alert(response);
                }
                else {
                    jsonResponse = JSON.parse(response.replace(/\'/g,'"'));
                    init_celery_setup (jsonResponse);
                    //displayBrokerResults(jsonResponse.broker);
                    //displayBackendResults(jsonResponse.backend);
                }
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
