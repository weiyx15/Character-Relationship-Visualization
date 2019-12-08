function highlight(d) {
    circles.style("opacity", 0.2);
    d3.select(this)
        .style("opacity", 1.0);

    var attention_name = d.id;

    link.style("opacity", 0.2);

    adjacent_nodes = new Set();

    d3.select("body").selectAll("line").data(graph.links).style("opacity", function (d2) {
        if (d2.target.id === attention_name || d2.source.id === attention_name) {
            adjacent_nodes.add(d2.target.id);
            adjacent_nodes.add(d2.source.id);
            return 1.0;
        } else {
            return 0.2;
        }
    });

    var point_info_label = document.getElementById('point_info_label');
    point_info_label.innerHTML = '节点详细信息';

    var attentioned_dialogs = "";

    graph.dialogs.forEach((item, index, array) => {
        if (item['source'] === attention_name) {
//                排除自己跟自己说的话
            if (item['source'] !== item['target']) {
                attentioned_dialogs += 'said to &nbsp<b>' + item['target'] + '</b>:&nbsp' + item['dialogs'] + '<br>';
            }
        }
    });
    var p_dialog_info = document.getElementById('dialog_info');
    p_dialog_info.innerHTML = attentioned_dialogs;


    var point_info = document.getElementById('point_info');
    var attentioned_point_info = '';
    attentioned_point_info += '<b>人物姓名</b>:&nbsp' + d.id + '<br>';
    attentioned_point_info += '<b>角色重要程度</b>:&nbsp' + d.group + '<br>';
    attentioned_point_info += '<b>相关人物</b>:&nbsp';

    adjacent_nodes.forEach((item, index) => {
        attentioned_point_info += item + "&nbsp";
    });
    point_info.innerHTML = attentioned_point_info;
}

