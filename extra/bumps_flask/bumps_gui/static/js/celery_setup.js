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
    var type = document.getElementById('broker_type');
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
/*
    try {
        var res = document.getElementById('broker_test_result');
        var msg = document.getElementById('broker_test_message');
        if (broker_response.result) {
            res.innerText = 'OK';
            res.style.color = 'green';
        }
        else {
            res.innerText = 'Fail';
            res.style.color = 'red';
        }
        msg.innerText = broker_response.message;
    }
    catch (e) {
        console.log(e);
    }
*/
}
//-----------------------------------------------------------------------------
function displayBackendResults(backend_response) {
    displayServerResults(backend_response, 'backend_test_result', 'backend_test_message');
/*
    try{
        var res = document.getElementById('backend_test_result');
        var msg = document.getElementById('backend_test_message');
        if (backend_response.result) {
            res.innerText = 'OK';
        }
        else {
            res.innerText = 'Fail';
        }
        msg.innerText = backend_response.message;
    }
    catch (e) {
        console.log(e);
    }
*/
}
//-----------------------------------------------------------------------------
