//-----------------------------------------------------------------------------
function onResultsDeleteClick() {
    var n, tbl = document.getElementById('tblResults');

    for (n=1 ; n < tbl.rows.length ; ) {
        var id=$(tbl.rows[n].cells[0].innerHTML).attr('id');
        var chk=document.getElementById(id).checked;
        if (chk)
            tbl.deleteRow(n);
        else
            n++;
    }
}
//-----------------------------------------------------------------------------
function onResultsDisplayClick() {
}
//-----------------------------------------------------------------------------
function onResultsLoadClick() {
}
//-----------------------------------------------------------------------------
function enableResultsButtons() {
    
}
//-----------------------------------------------------------------------------
