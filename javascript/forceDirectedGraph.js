function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}


function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function nodeClick(d) {
    var attentioned_dialogs = "";
    adjacent_nodes.forEach((value, key, map) => {
        attentioned_dialogs += 'said to &nbsp<b>' + key + '</b>:&nbsp' + value[0] + '<br>';
    });
    var p_dialog_info = document.getElementById('dialog_info');
    p_dialog_info.innerHTML = attentioned_dialogs;
    var point_info = document.getElementById('point_info');
    var attentioned_point_info = '';
    attentioned_point_info += '<b>人物姓名</b>:&nbsp' + d.id + '<br>';
    attentioned_point_info += '<b>角色重要程度</b>:&nbsp' + d.group + '<br>';
    attentioned_point_info += '<b>相关人物</b>:';
    index = 0;
    adjacent_nodes.forEach((value, key, map) => {
        if (index % 4 == 0)
            attentioned_point_info += '<br>';
        attentioned_point_info += key + "&nbsp";
        index++;
    });
    attentioned_point_info += '<br>';
    point_info.innerHTML = attentioned_point_info;
}