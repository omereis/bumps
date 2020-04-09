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
    document.getElementById('txtBroker').innerText = jsnBroker.address;
    document.getElementById('broker_type').value   = jsnBroker.type;
}
//-----------------------------------------------------------------------------
function displayBackendSetup(jsnBackend) {
    document.getElementById('txtBackend').innerText = jsnBackend.address;
    document.getElementById('backend_type').value   = jsnBackend.type;
}
//-----------------------------------------------------------------------------
