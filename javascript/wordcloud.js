/**
 * Created by chenyufeng on 2019/12/16.
 */

function draw_word_cloud(words_data) {
    console.log(words_data);
    var chart = echarts.init(document.getElementById('wordcloud'));
    var option = {
        tooltip: {},
        series: [{
            type: 'wordCloud',
            gridSize: 20,
            sizeRange: [10, 30],
            rotationRange: [0, 30],
            width: 300,
            height: 70,
            drawOutOfBound: true,
            textStyle: {
                normal: {
                    color: function () {
                        return 'rgb(' + [
                                Math.round(Math.random() * 160),
                                Math.round(Math.random() * 160),
                                Math.round(Math.random() * 160)
                            ].join(',') + ')';
                    }
                },
                emphasis: {
                    shadowBlur: 10,
                    shadowColor: '#333'
                }
            },
            data: words_data
    }]};

    chart.setOption(option);

    window.onresize = chart.resize;
}
