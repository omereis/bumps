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
/*    var type = document.getElementById('broker_type');
    var typeName = 'unknown';
    var address = '';
    var jsnBroker;
    try {
        typeName = type.options[type.selectedIndex].value;
        address = document.getElementById('txtBroker').value;
        jsnBroker = {'type':typeName, 'address':address;}
    }
    catch (e) {
        console.log(e.message);
        jsnBroker = {}
    }
    return (jsnBroker);
*/
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
