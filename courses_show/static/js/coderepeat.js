function cmp_source() {
    var code1 = $("#source1").val(),
        code2 = $("#source2").val(),
        method = $("#method").val(),
        data = JSON.stringify({'code1':code1, 'code2':code2, 'method': method});
    
    $.post({
        url: '/cmpcode',
        dataType: 'json',
        data: data,
        success: function (data) {
            var comments = data.comment,
                variables = data.variable,
                codes = data.code;

//          showSimilar(comments, "comment");
//          showSimilar(variables, "variable");
            showCodeSimilar(codes, "code");
        }
    });
}

function showCodeSimilar(pairData, part) {
    var left = pairData[0],
        right = pairData[1],
        code1 = $("#source1").val().split('\n'),
        code2 = $("#source2").val().split('\n'),
        similarity = 0,
        similar_no = 0;

    if (left.length !== right.length) {
        alert("数据有误");
        return -1;
    }

    $("#"+part).css("display", "block");
    $("#"+part+"1").html('');
    $("#"+part+"2").html('');

    for (var i in left) {
        var lp = $("<p></p>"),
            rp = $("<p></p>"),
            left_ele = left[i],
            right_ele = right[i],
            lfont = $("<font>"),
            rfont = $("<font>");

        lfont.text(left_ele < 0?"-":(left_ele + '  ' +
                    code1[left_ele-1]));
        rfont.text(right_ele < 0?"-":(right_ele + '  ' +
                    code2[right_ele-1]));

        if (left_ele > 0 && right_ele > 0) {
            lfont.attr("color", "red");
            rfont.attr("color", "red");
            similar_no++;
        }

        lp.html(lfont);
        $("#"+part+"1").append(lp);
        rp.html(rfont);
        $("#"+part+"2").append(rp);
    }

    if (pairData.length === 2) 
        similarity = 100*similar_no/left.length;
    else
        similarity = pairData[2];

    $("#"+part+"similar").html(similarity+"%");
}

function showSimilar(pairData, part) {
    var left = pairData[0],
        right = pairData[1],
        similarity = 0,
        similar_no = 0;

    if (left.length !== right.length) {
        alert("数据有误");
        return -1;
    }

    $("#"+part).css("display", "block");

    for (var i in left) {
        var lp = $("<p></p>"),
            rp = $("<p></p>"),
            left_ele = left[i],
            right_ele = right[i],
            lfont = $("<font>");
            rfont = $("<font>");
        lfont.text(left_ele);
        rfont.text(right_ele);

        if (left_ele && right_ele) {
            lfont.attr("color", "red");
            rfont.attr("color", "red");
            similar_no++;
        }

        lp.html(lfont);
        $("#"+part+"1").append(lp);
        rp.html(rfont);
        $("#"+part+"2").append(rp);
    }

    if (pairData.length === 2) 
        similarity = 100*similar_no/left.length;
    else
        similarity = pairData[2];

    $("#"+part+"1").html();
    $("#"+part+"2").html();
    $("#"+part+"similar").html(similarity+"%");
            }
