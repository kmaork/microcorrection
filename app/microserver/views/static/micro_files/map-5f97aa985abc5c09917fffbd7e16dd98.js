function levelchanged(e) {
    function t() {
        window.location = `/cpu/debugger/${encodeURIComponent(e)}`;
    }

    cpu.send("/cpu/is_alive", {}, function (e) {
        JSON.parse(e) ? confirm("Starting a level will kill any other levels you have running. Are you sure you want to do so?") && cpu.send("/cpu/dbg/kill", {}, function () {
            t()
        }) : t()
    })
}

$(document).ready(function () {
    cpu.get("/get_levels", function (e) {
        for (var t in e.levels) {
            var n, i = e.levels[t], o = "javascript:levelchanged('" + i.name + "')";
            n = 1 == i.done ? "/static/micro_files/o.png" : "/static/micro_files/x.png", function (e) {
                $("section.countries").append($("<li>").append($("<a>").attr("href", o).text(i.name).css("color", i.done ? "#00b9a0" : "#ec9300").mouseover(function () {
                    $(".marker" + e).css("background", "#fff")
                }).mouseout(function () {
                    $(".marker" + e).css("background", "")
                }).prop("class", "tipsyit").attr("original-title", i.name + "; " + i.rating + " points")))
            }(t), 0 != i.top && $("section#markers").append($("<a>").append($("<img src='" + n + "'>").css("position", "absolute").css("top", i.top + "px").css("left", i.left + "px").prop("class", "marker" + t).prop("class", "tipsyit").attr("original-title", i.name + "; " + i.rating + " points")).attr("href", o))
        }
        return void $(".tipsyit").tipsy({fade: !0, gravity: "n"});
        var i, i
    })
});
var cpu = {
    send: function (e, t, n) {
        $.ajax({
            url: e,
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({body: t})
        }).fail(function () {
        }).done(function (e) {
            n && n(e)
        })
    }, get: function (e, t) {
        $.ajax({url: e, type: "get", dataType: "json"}).fail(function () {
            console.log("Connection to server failed; GET could not be sent.")
        }).done(function (e) {
            t && t(e)
        })
    }
};